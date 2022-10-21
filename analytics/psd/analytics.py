#!/usr/bin/env python3

import re

import pandas as pd

from deobfuscator import PS_ENC_RE, PS_COM_RE, decode, reformat

# Kestrel analytics default paths (single input variable)
INPUT_DATA_PATH = "/data/input/0.parquet.gz"
OUTPUT_DATA_PATH = "/data/output/0.parquet.gz"
OUTPUT_DISPLAY = "/data/display/ret.html"


def deobfuscate(df):
    # first check for base64 encoded
    df['ps_enc'] = df['command_line'].str.extract(PS_ENC_RE, flags=re.IGNORECASE)[1]  # group 1

    # Decode when necessary
    df['ps_dec'] = df['ps_enc'].apply(decode)
    df = df.drop('ps_enc', axis=1)

    # Otherwise just get the code
    df['ps_code'] = df['command_line'].str.extract(PS_COM_RE)

    # Merge decoded and unencoded columns
    df = pd.concat([df.drop(['ps_dec'], axis=1), df['ps_dec'].combine_first(df['ps_code'])], axis=1)
    df = df.drop('ps_code', axis=1)

    # Produce a mostly-deobfuscated version
    df['x_psd_deobfuscated'] = df['ps_dec'].apply(reformat)
    df = df.drop('ps_dec', axis=1)

    return df


def analytics(df):
    df = deobfuscate(df)
    display = ""
    for index, row in df.iterrows():
        data = row['x_psd_deobfuscated']
        if pd.isnull(data):
            # Skip empty rows (i.e. no ofuscation was found)
            continue
        # Each row should be a process SCO, but don't require an id, just in case
        oid = row.get('id', '')
        display += f"<br/>Row {index + 1}: {oid}\n<hr/>\n<pre>\n{data}</pre>\n\n"

    # return the updated Kestrel variable
    return df, display


if __name__ == "__main__":
    dfi = pd.read_parquet(INPUT_DATA_PATH)
    dfo, disp = analytics(dfi)
    dfo.to_parquet(OUTPUT_DATA_PATH, compression="gzip")
    with open(OUTPUT_DISPLAY, "w") as o:
        o.write(disp)
