#!/usr/bin/env python3

import pandas as pd

from unlog4shell import deobfuscate, check_string, check_url

# Kestrel analytics default paths (single input variable)
INPUT_DATA_PATH = "/data/input/0.parquet.gz"
OUTPUT_DATA_PATH = "/data/output/0.parquet.gz"

def check_string(s):
    match = re.search(r'(\$\{.*\})', s)
    if match:
        subst = match.group(0)
        deob = deobfuscate(subst)
        if deob and '${jndi:' in deob:
            return deob
    return None


def check_url(url):
    while re.search(r'%[0-9A-Fa-f]{2}', url):
        url = unquote(url)
    return check_string(url)

def analytics(dataframe):
    # analyze data in dataframe
    
    # provide insights or additional knowledge
    if 'value' in dataframe.columns:
        dataframe['exploit'] = dataframe['value'].apply(check_url)
    for column in dataframe.columns:
        # User agent column in STIX patterns is a bit nasty:
        #  "extensions.'http-request-ext'.request_header.'User-Agent'"
        if 'user-agent' in column.lower() or 'user_agent' in column.lower():
            dataframe['exploit'] = dataframe[column].apply(check_string)
            break

    # return the updated Kestrel variable
    return dataframe

if __name__ == "__main__":
    dfi = pd.read_parquet(INPUT_DATA_PATH)
    dfo = analytics(dfi)
    dfo.to_parquet(OUTPUT_DATA_PATH, compression="gzip")
