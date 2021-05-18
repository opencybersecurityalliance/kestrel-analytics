#!/usr/bin/env python3

import pandas as pd

# Kestrel analytics default paths (single input variable)
INPUT_DATA_PATH = "/data/input/0.parquet.gz"
OUTPUT_DATA_PATH = "/data/output/0.parquet.gz"
OUTPUT_DISPLAY = "/data/display/ret.html"

def analytics(dataframe):
    # analyze data in dataframe

    # provide insights or additional knowledge
    newattr = ["newval" + str(i) for i in range(dataframe.shape[0])]
    dataframe["x_new_attr"] = newattr

    display = "<p>Hello World! -- a Kestrel analytics</p>"

    # return the updated Kestrel variable
    return dataframe, display

if __name__ == "__main__":
    dfi = pd.read_parquet(INPUT_DATA_PATH)
    dfo, disp = analytics(dfi)
    dfo.to_parquet(OUTPUT_DATA_PATH, compression="gzip")
    with open(OUTPUT_DISPLAY, "w") as o:
        o.write(disp)
