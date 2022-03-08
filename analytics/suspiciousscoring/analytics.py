#!/usr/bin/env python3

import fnmatch
import json
import os

import pandas as pd

import rule_engine

# Kestrel analytics default paths
INPUT_DATA_PATH = "/data/input/0.parquet.gz"
OUTPUT_DATA_PATH = "/data/output/0.parquet.gz"

PATTERNS = [
    # Sigma patterns
    # Source: https://github.com/Neo23x0/sigma/blob/32ecb816307e3639cf815851fac8341a60631f45/rules/linux/lnx_shell_susp_commands.yml
    # Retrieved: 2020-09-15
    # Author: Florian Roth
    # LICENSE: https://github.com/Neo23x0/sigma/blob/32ecb816307e3639cf815851fac8341a60631f45/LICENSE.Detection.Rules.md
    'wget * - http* | perl',
    'wget * - http* | sh',
    'wget * - http* | bash',
    'python -m SimpleHTTPServer',
    '-m http.server'  # Python 3,
    'import pty; pty.spawn*',
    'socat exec:*',
    'socat -O /tmp/*',
    'socat tcp-connect*',
    '*echo binary >>*',
    '*wget *; chmod +x*',
    '*wget *; chmod 777 *',
    '*cd /tmp || cd /var/run || cd /mnt*',
    '*stop;service iptables stop;*',
    '*stop;SuSEfirewall2 stop;*',
    'chmod 777 2020*',
    '*>>/etc/rc.local',
    '*base64 -d /tmp/*',
    '* | base64 -d *',
    '*/chmod u+s *',
    '*chmod +s /tmp/*',
    '*chmod u+s /tmp/*',
    '* /tmp/haxhax*',
    '* /tmp/ns_sploit*',
    'nc -l -p *',
    'cp /bin/ksh *',
    'cp /bin/sh *',
    '* /tmp/*.b64 *',
    '*/tmp/ysocereal.jar*',
    '*/tmp/x *',
    '*; chmod +x /tmp/*',
    '*;chmod +x /tmp/*',
    '*tweet*'
    # End of sigma patterns
]


def get_network_connections(df):
    if "x_opened_connection_count" in df.keys():
        agg_func = pd.Series.sum
        column = "x_opened_connection_count"
    elif "opened_connection_ref_0.id" in df.keys():
        agg_func = pd.Series.nunique
        column = "opened_connection_ref_0.id"
    else:
        return df

    if "x_guid" in df.keys():
        network = df.groupby("x_guid").agg({column: agg_func}).reset_index()
        network_susp = df[["x_guid", "command_line"]]
        network_susp = network_susp.merge(network, left_on="x_guid", right_on="x_guid")
        network_susp["network_susp_score"] = network_susp.apply(
            lambda row: row[column] if row["command_line"] else 0, axis=1)
        df["network_susp_score"] += network_susp["network_susp_score"]

    return df


def get_lu(df, column, method, parameters):
    if method == 'iqr':
        k = parameters['k'] if 'k' in parameters else 1.5
        q1 = df[column].quantile(0.25)
        q3 = df[column].quantile(0.75)
        iqr = q3 - q1
        cutoff = iqr * k
        lower = q1 - cutoff
        upper = q3 + cutoff
    else:
        # Default to method == 'stddev'
        k = parameters['k'] if 'k' in parameters else 3
        mean = df[column].mean()
        stddev = df[column].std()
        cutoff = stddev * k
        lower = mean - cutoff
        upper = mean + cutoff
    return lower, upper


def score_outliers(df, columns, method, parameters, value):
    if isinstance(columns, list):
        column = columns[0]
        if len(columns) > 1:
            print('WARN: Only using 1 column "{}" for univariate method "{}"'.format(column, method))
    else:
        column = columns
    lower, upper = get_lu(df, column, method, parameters)
    mask = (df[column] < lower) | (df[column] > upper)
    df.loc[mask, 'x_suspicious_score'] += value


def analytics(df):
    # init suspicious scores
    df["x_suspicious_score"] = 0

    # analytics firs step
    # - check unknown malicious command line
    for pattern in PATTERNS:
        # Convert the pattern to a RE
        pattern = fnmatch.translate(pattern)

        # Find all matching rows and convert boolean result to 0 or 1
        if 'command_line' in df.columns:
            score = df['command_line'].str.contains(pattern, na=False).astype(int)

            # Add to score column
            df["x_suspicious_score"] += score
        else:
            df["x_suspicious_score"] = 0

    # analytics second step
    # - check how many network connection with each x_guid
    df = get_network_connections(df)
    if 'network_susp_score' in df.columns:
        score_outliers(df, 'network_susp_score', 'stddev', {'k': 3}, 1)

    # Apply rules
    cwd = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(cwd, 'rules.json'), 'r') as fp:
        rules = json.load(fp)
    engine = rule_engine.RuleEngine(rules)

    def score_rules(row):
        """Adapter func for passing DataFrame rows to rule engine"""
        obj = dict(row)  # rule engine wants a dict
        engine.apply_rules(obj)
        score = obj.get('x_suspicious_score', 0)
        return score
    results = df.apply(score_rules, axis=1)
    df["x_suspicious_score"] = results

    # return a list of entities/SCOs
    return df


if __name__ == "__main__":
    dfi = pd.read_parquet(INPUT_DATA_PATH)
    dfo = analytics(dfi)
    dfo.to_parquet(OUTPUT_DATA_PATH, compression="gzip")
