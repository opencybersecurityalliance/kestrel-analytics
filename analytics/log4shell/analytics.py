#!/usr/bin/env python3

import base64
import socket
from urllib.parse import urlparse

import pandas as pd

from unlog4shell import check_string, check_url, check_payload

# Kestrel analytics default paths (single input variable)
INPUT_DATA_PATH = "/data/input/0.parquet.gz"
OUTPUT_DATA_PATH = "/data/output/0.parquet.gz"


def unbase64(blob):
    return base64.b64decode(blob).decode('utf-8')


def split_url(url):
    if url:
        result = urlparse(url)
        return (result.hostname, result.port, result.path, result.query)
    return (None, None, None, None)


def analytics(df):
    # analyze data in dataframe

    # provide insights or additional knowledge
    df['exploit'] = None
    if 'value' in df.columns:
        # Assume URL?  We don't actually know the SCO type.
        df['exploit'] = df['value'].apply(check_url)
    
    for column in df.columns:
        # User agent column in STIX patterns is a bit nasty:
        #  "extensions.'http-request-ext'.request_header.'User-Agent'"
        if 'request_header' in column.lower():
            result = df[column].apply(check_string)
            df['exploit'] = df['exploit'].combine_first(result)
        elif column == 'payload_bin':
            df['exploit'] = df[column].apply(check_payload)
            df['original'] = df[column].apply(unbase64)
            break

    # Split apart the url into new columns
    df[['hostname', 'port', 'path', 'query']] = pd.DataFrame(df['exploit'].apply(split_url).tolist(), index=df.index)

    # Look up hostname to get IP
    df['addr'] = df['hostname'].apply(socket.gethostbyname)

    # return the updated Kestrel variable
    return df


if __name__ == "__main__":
    dfi = pd.read_parquet(INPUT_DATA_PATH)
    dfo = analytics(dfi)
    dfo.to_parquet(OUTPUT_DATA_PATH, compression="gzip")
