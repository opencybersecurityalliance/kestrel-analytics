#!/usr/bin/env python3

import pandas as pd
import geoip2.database
from geoip2.errors import AddressNotFoundError
import folium
from folium.plugins import MiniMap
from IPython.core.formatters import DisplayFormatter

# Kestrel analytics default paths
INPUT_DATA_PATH = "/data/input/0.parquet.gz"
OUTPUT_DISP_PATH = "/data/display/ret.html"

def visualize_ips(ips):
    client = geoip2.database.Reader('GeoLite2-City.mmdb')
    locations = []
    for ip in ips:
        try:
            r = client.city(ip)
        except AddressNotFoundError:
            pass
        else:
            locations.append(((r.location.latitude,r.location.longitude), ip))
    map_osm = folium.Map(location=(r.location.latitude,r.location.longitude))
    for l in locations:
        loc, ip = l
        m = folium.map.Marker(loc, tooltip=ip)
        map_osm.add_child(m)
    minimap = MiniMap()
    map_osm.add_child(minimap)
    return map_osm

def analytics(dataframe):
    entity_type = dataframe["type"].unique()[0]
    if entity_type == "ipv4-addr":
        ips = list(dataframe["value"].unique())
    elif entity_type == "network-traffic":
        src_ips = list(dataframe["src_ref.value"].unique())
        dst_ips = list(dataframe["dst_ref.value"].unique())
        ips = src_ips + dst_ips
    else:
        ips = []
    viz = visualize_ips(ips)
    disp = DisplayFormatter()
    html = disp.format(viz)[0]['text/html']
    return html

if __name__ == "__main__":
    dfi = pd.read_parquet(INPUT_DATA_PATH)
    html = analytics(dfi)
    with open(OUTPUT_DISP_PATH, "w") as od:
        od.write(html)
