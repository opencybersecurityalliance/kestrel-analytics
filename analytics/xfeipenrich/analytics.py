#!/usr/bin/env python3

import os
import pandas as pd
import requests
from datetime import datetime
import base64, time
import json
# Kestrel analytics default paths
INPUT_DATA_PATH = "/data/input/0.parquet.gz"
OUTPUT_DATA_PATH = "/data/output/0.parquet.gz"

xfe_cred = os.environ.get("XFE_CRED")
if not xfe_cred:
    raise Exception('No API credentials!')
ENRICH_COLUMNS = ['cats', 'score', 'geo']

XFE_URL = "https://api.xforce.ibmcloud.com"
def get_xfe_ip_enrich(key, ips):
    ipurl = XFE_URL + "/ipr/"
    cred  = str(xfe_cred.value).strip('\"')
    token = base64.b64encode(cred.encode())
    headers = {'Authorization': "Basic " + str(token.decode()), 'Accept': 'application/json', 'content-type': 'applications/json'}
    result = {f"x_{key}_{c}": [] for c in ENRICH_COLUMNS}
    for _ip in ips:
        iprurl = ipurl + _ip
        resp = requests.get(iprurl, params='', headers=headers, timeout=20)
        if resp.status_code == 401:
            raise Exception('Not Authorized')
        elif resp.status_code == 429:
            #getting rate limited so sleep.
            for c in ENRICH_COLUMNS:
                result[f"x_{key}_{c}"].append(None)
            time.sleep(1)
        elif resp.status_code == 200:
            data = resp.json()
            if 'ip' not in data:
                return None

            for c in ENRICH_COLUMNS:
                if c == 'geo':
                    if c not in data:
                        result[f"x_{key}_geo"].append(None)
                    else:
                        country = data['geo']['country']
                        result[f"x_{key}_geo"].append(country)
                elif c == 'cats':
                    cat =""
                    for k in data['cats']:
                        cat = cat + k + ","
                    #trim last char
                    if len(data['cats']) >0:  
                        cat = cat[:-1]    
                    result[f"x_{key}_{c}"].append(cat)
                else:
                    if c not in data['ip']:
                        result[f"x_{key}_{c}"].append(None)
                    else:
                        result[f"x_{key}_{c}"].append(data[c])
        else:
            raise Exception('API error' + str(ipurl))
    #return {k: v for k, v in result.items() if len(v)}
    return result

def analytics(df):
    columns=[]
    if df['type'][0] in ['ipv4-addr','ipv6-addr']:
        columns = ["value"]
    elif df['type'][0] == 'network-traffic':
        columns = ["src_ref.value", "dst_ref.value"]
    for c in columns:
        if c not in df.columns:
            continue
        result = get_xfe_ip_enrich(c, df[c])
        for k, v in result.items():
            df[k] = v
    return df


if __name__ == "__main__":
    dfi = pd.read_parquet(INPUT_DATA_PATH)
    dfo = analytics(dfi)
    dfo.to_parquet(OUTPUT_DATA_PATH, compression="gzip")
