#!/usr/bin/env python3

import os
import pandas as pd
import requests
from datetime import datetime

# Kestrel analytics default paths
INPUT_DATA_PATH = "/data/input/0.parquet.gz"
OUTPUT_DATA_PATH = "/data/output/0.parquet.gz"

SANS_CRED = os.environ.get('SANSCRED')
if not SANS_CRED:
    raise Exception('No API credentials!')
ENRICH_COLUMNS = ['attacks', 'ascountry', 'asname', 'threatfeeds', "firstseen", "lastseen"]


def get_sans_ip_enrich(key, ips):
    header = {'user-agent': SANS_CRED}
    result = {f"x_{key}_{c}": [] for c in ENRICH_COLUMNS}
    for _ip in ips:
        sans_url = f'https://isc.sans.edu/api/ip/{_ip}?json'
        resp = requests.get(sans_url, headers=header)
        if resp.status_code == 200:
            data = resp.json()
            if 'ip' not in data:
                return None

            for c in ENRICH_COLUMNS:
                if c in ["firstseen", "lastseen"]:
                    continue
                elif c == 'threatfeeds':
                    if c not in data['ip']:
                        result[f"x_{key}_threatfeeds"].append(None)
                        result[f"x_{key}_firstseen"].append(None)
                        result[f"x_{key}_lastseen"].append(None)
                    else:
                        threat_feeds = ','.join(list(data['ip'][c].keys()))
                        first_seen = []
                        last_seen = []
                        for t, s in data['ip'][c].items():
                            first_seen.append(datetime.strptime(s['firstseen'], '%Y-%m-%d'))
                            last_seen.append(datetime.strptime(s['lastseen'], '%Y-%m-%d'))
                        first_seen = sorted(first_seen)[0].strftime('%Y-%m-%d')
                        last_seen = sorted(last_seen)[-1].strftime('%Y-%m-%d')
                        result[f"x_{key}_threatfeeds"].append(threat_feeds)
                        result[f"x_{key}_firstseen"].append(first_seen)
                        result[f"x_{key}_lastseen"].append(last_seen)
                elif c == 'attacks':
                    attack_value = data['ip'][c] if data['ip'][c] else 0
                    result[f"x_{key}_{c}"].append(attack_value)
                else:
                    if c not in data['ip']:
                        result[f"x_{key}_{c}"].append(None)
                    else:
                        result[f"x_{key}_{c}"].append(data['ip'][c])
    return {k: v for k, v in result.items() if len(v)}


def analytics(df):
    columns = ["src_ref.value", "dst_ref.value"]
    for c in columns:
        if c not in df.columns:
            continue
        result = get_sans_ip_enrich(c, df[c])
        for k, v in result.items():
            df[k] = v
    return df


if __name__ == "__main__":
    dfi = pd.read_parquet(INPUT_DATA_PATH)
    dfo = analytics(dfi)
    dfo.to_parquet(OUTPUT_DATA_PATH, compression="gzip")
