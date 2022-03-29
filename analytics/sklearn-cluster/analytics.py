#!/usr/bin/env python3

import ast
import os

import gower
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

COLS = os.environ.get('columns')
METHOD = os.environ.get('method', 'kmeans')


def mixed_columns(df, cols):
    dtypes = set(df[cols].dtypes.apply(str).tolist())
    return 'object' in dtypes


def analytics(df):
    # Process our parameters
    if COLS:
        cols = COLS.split(',')
    else:
        cols = list(df.columns)
    mixed =  mixed_columns(df, cols)
    if mixed:
        # Can ONLY use dbscan
        method = 'dbscan'
    else:
        method = METHOD.lower()
    algo, params = METHODS[method]
    params = {p: int(v) if v.isdigit() else v for p, v in params.items()}

    if mixed:
        params['metric'] = 'precomputed'
        dist_matrix = gower.gower_matrix(df[cols])
        model = algo(**params).fit(dist_matrix)
    else:
        model = algo(**params).fit(df[cols])

    df['cluster'] = model.labels_

    # return the updated Kestrel variable
    return df


if __name__ == "__main__":
    dfi = pd.read_parquet(INPUT_DATA_PATH)
    dfo = analytics(dfi)
    dfo.to_parquet(OUTPUT_DATA_PATH, compression="gzip")
