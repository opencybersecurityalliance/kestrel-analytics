#!/usr/bin/env python3

import os

import pandas as pd
from sklearn.cluster import KMeans

# Kestrel analytics default paths (single input variable)
INPUT_DATA_PATH = "/data/input/0.parquet.gz"
OUTPUT_DATA_PATH = "/data/output/0.parquet.gz"

# Our analytic parameters from the WITH clause
# Kestrel will create env vars for them 
COLS = os.environ['columns']
N = os.environ['n']


def analytics(df):
    # Process our parameters
    cols = COLS.split(',')
    n = int(N)

    # Run the algorithm
    kmeans = KMeans(n_clusters=n).fit(df[cols])
    df['cluster'] = kmeans.labels_

    # return the updated Kestrel variable
    return df


if __name__ == "__main__":
    dfi = pd.read_parquet(INPUT_DATA_PATH)
    dfo = analytics(dfi)
    dfo.to_parquet(OUTPUT_DATA_PATH, compression="gzip")
