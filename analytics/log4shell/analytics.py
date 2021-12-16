#!/usr/bin/env python3

import base64
import pandas as pd

from unlog4shell import check_string, check_url, check_payload

# Kestrel analytics default paths (single input variable)
INPUT_DATA_PATH = "/data/input/0.parquet.gz"
OUTPUT_DATA_PATH = "/data/output/0.parquet.gz"


def unbase64(blob):
    return base64.b64decode(blob).decode('utf-8')


def analytics(dataframe):
    # analyze data in dataframe

    # provide insights or additional knowledge
    dataframe['exploit'] = None
    if 'value' in dataframe.columns:
        # Assume URL?  We don't actually know the SCO type.
        dataframe['exploit'] = dataframe['value'].apply(check_url)
    
    for column in dataframe.columns:
        # User agent column in STIX patterns is a bit nasty:
        #  "extensions.'http-request-ext'.request_header.'User-Agent'"
        if 'request_header' in column.lower():
            result = dataframe[column].apply(check_string)
            dataframe['exploit'] = dataframe['exploit'].combine_first(result)
        elif column == 'payload_bin':
            dataframe['exploit'] = dataframe[column].apply(check_payload)
            dataframe['original'] = dataframe[column].apply(unbase64)
            break

    # return the updated Kestrel variable
    return dataframe

if __name__ == "__main__":
    dfi = pd.read_parquet(INPUT_DATA_PATH)
    dfo = analytics(dfi)
    dfo.to_parquet(OUTPUT_DATA_PATH, compression="gzip")
