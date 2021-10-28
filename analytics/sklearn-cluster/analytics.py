#!/usr/bin/env python3

import ast
import os

import pandas as pd
from sklearn.cluster import DBSCAN, KMeans

# Kestrel analytics default paths (single input variable)
INPUT_DATA_PATH = "/data/input/0.parquet.gz"
OUTPUT_DATA_PATH = "/data/output/0.parquet.gz"

# Our analytic parameter from the WITH clause
# Kestrel will create env vars for them
METHODS = {
    'dbscan': (DBSCAN, {p:v for p, v in os.environ.items() if p in DBSCAN()._get_param_names()}),
    'kmeans': (KMeans, {p:v for p, v in os.environ.items() if p in KMeans()._get_param_names()}),
}

COLS = os.environ['columns']
METHOD = os.environ.get('method', 'kmeans')


def analytics(df):
    # Process our parameters
    cols = COLS.split(',')
    method = METHOD.lower()
    algo, params = METHODS[method]
    params = {p: int(v) if v.isdigit() else v for p, v in params.items()}
    model = algo(**params).fit(df[cols])
    df['cluster'] = model.labels_

    # return the updated Kestrel variable
    return df


if __name__ == "__main__":
    dfi = pd.read_parquet(INPUT_DATA_PATH)
    dfo = analytics(dfi)
    dfo.to_parquet(OUTPUT_DATA_PATH, compression="gzip")