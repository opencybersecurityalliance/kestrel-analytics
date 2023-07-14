#!/usr/bin/env python3
import os

import folium
from folium.plugins import MarkerCluster
import pandas as pd
from IPython.core.formatters import DisplayFormatter

# Kestrel analytics default paths
INPUT_DATA_PATH = "/data/input/0.parquet.gz"
OUTPUT_DISP_PATH = "/data/display/ret.html"


def geoviz(df, lat_col, lon_col, label_cols):
    df['x_geoviz_label'] = df[label_cols].apply(lambda l: "\n".join([str(i) for i in l]), axis=1)
    df.columns = df.columns.str.replace(r"'", "")
    loc = df[[lat_col, lon_col, 'x_geoviz_label']]
    loc = [tuple(x[1]) for x in loc.iterrows()]
    center = (loc[0][0], loc[0][1])
    default_map = folium.Map(location=center, zoom_start=5, tiles='cartodbpositron')
    marker_cluster = MarkerCluster().add_to(default_map)

    for data in loc:
        lat, lon, label = data
        popup = folium.Popup(label)
        icon1 = folium.Icon(color="red")
        folium.Marker((lat, lon), popup=popup, icon=icon1).add_to(marker_cluster)

    return default_map


def analytics(dataframe):
    lat_col = os.environ.get("LAT")
    lon_col = os.environ.get("LON")
    label_cols = os.environ.get("LABELS").split(',')
    viz = geoviz(dataframe, lat_col, lon_col, label_cols)
    disp = DisplayFormatter()
    return disp.format(viz)[0]['text/html']


if __name__ == "__main__":
    dfi = pd.read_parquet(INPUT_DATA_PATH)
    html = analytics(dfi)
    with open(OUTPUT_DISP_PATH, "w") as od:
        od.write(html)
