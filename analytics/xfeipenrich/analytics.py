#!/usr/bin/env python3

import base64
import os
import time
import requests

import pandas as pd

# Kestrel analytics default paths
INPUT_DATA_PATH = "/data/input/0.parquet.gz"
OUTPUT_DATA_PATH = "/data/output/0.parquet.gz"

xfe_cred = os.environ.get("XFE_CRED")
if not xfe_cred:
    raise Exception('No XFE API credentials found in XFE_CRED!')
cred  = xfe_cred.strip('\"')
token = base64.b64encode(cred.encode())
headers = {
    'Authorization': "Basic " + str(token.decode()),
    'Accept': 'application/json',
    'content-type': 'applications/json'
}


XFE_URL = "https://api.xforce.ibmcloud.com"


def _get_company(data, result):
    company = None
    history = data.get('history', [])
    if history:
        last_entry = history[-1]
        asns = last_entry.get('asns', {})
        for _, asn_data in asns.items():
            removed = asn_data.get('removed', False)
            if not removed:
                company = asn_data.get('Company')
                if company:
                    break
    result["x_xfe_company"].append(company)


def get_xfe_enrich(endpoint, observables, enrich_cols):
    # result columns
    result = {f"x_xfe_{c}": [] for c in enrich_cols}

    for observable in observables:
        if not observable:
            # Could get Nones for some rows
            for c in enrich_cols:
                result[f"x_xfe_{c}"].append(None)
            continue

        url = "/".join([XFE_URL, endpoint, observable])
        resp = requests.get(url, params='', headers=headers, timeout=20)
        if resp.status_code == 401:
            raise Exception('Not Authorized')
        if resp.status_code == 429:
            # getting rate limited so sleep.
            for c in enrich_cols:
                result[f"x_xfe_{c}"].append(None)  #FIXME: retry this item?
            time.sleep(1)
        elif resp.status_code == 404:
            # Not found, so add some Nones
            for c in enrich_cols:
                result[f"x_xfe_{c}"].append(None)
        elif resp.status_code == 200:
            data = resp.json()

            # Do some endpoint-specific stuff
            if endpoint == 'url':
                data = data.get('result', {})
            elif endpoint == 'malware':
                data = data.get('malware', {})

            for c in enrich_cols:
                if c == 'geo':
                    country = data[c].get('country')
                    result[f"x_xfe_{c}"].append(country)
                elif c == 'cats':
                    cats = list(data[c].keys()) if data[c] else None
                    result[f"x_xfe_{c}"].append(cats)
                elif c == 'company':
                    _get_company(data, result)
                else:
                    if c not in data:
                        result[f"x_xfe_{c}"].append(None)
                    else:
                        result[f"x_xfe_{c}"].append(data[c])
        else:
            raise Exception(f'API error {resp.status_code} for {url}')

    return result


def analytics(df):
    column = 'value'
    otype = df['type'][0]
    if otype in ['ipv4-addr','ipv6-addr']:
        enrich_cols = ['cats', 'score', 'geo', 'company']
        endpoint = 'ipr'
    elif otype in ['domain-name', 'url']:
        enrich_cols = ['cats', 'score']
        endpoint = 'url'
    elif otype in ['file']:
        # Create a single hash column
        hash_cols = [c for c in list(df.columns) if c.startswith('hashes.')]
        df['x_hash'] = df[hash_cols].bfill(axis=1).iloc[:, 0]
        column = 'x_hash'
        enrich_cols = ['risk', 'family']
        endpoint = 'malware'

    if column in df.columns:
        result = get_xfe_enrich(endpoint, df[column], enrich_cols)
        for key, value in result.items():
            df[key] = value

    # Clean up any temp columns
    if otype in ['file']:
        df.drop('x_hash', axis=1, inplace=True)

    return df


if __name__ == "__main__":
    dfi = pd.read_parquet(INPUT_DATA_PATH)
    dfo = analytics(dfi)
    dfo.to_parquet(OUTPUT_DATA_PATH, compression="gzip")
