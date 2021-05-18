#!/usr/bin/env python3

import pandas as pd
import numpy as np
import os

# Kestrel analytics default paths
INPUT_DATA_PATH = "/data/input/0.parquet.gz"
OUTPUT_DISP_PATH = "/data/display/plot.svg"

x_param = os.environ.get('XPARAM')
y_param = os.environ.get('YPARAM')
if not x_param or not y_param:
    raise Exception('No X or Y parameter specified')

def is_numeric(df, column):
    if column.endswith('_id') or column.endswith('_port'):
        return False
    if str(df[column].dtype) in ['Int32', 'Int64']:
        return True
    return np.issubdtype(df[column].dtype, np.number)


def is_integer(series):
    '''Detect if a numeric array/series/column is all integers'''
    if str(series.dtype) in ['Int32', 'Int64']:
        return True
    return np.issubdtype(series.dtype, np.number) and (np.modf(series)[0].sum() == 0.0)


def is_timestamp(series):
    dtype = str(series.dtype)
    if 'time' in dtype.lower():
        return True
    s = series.dropna()
    if len(s.index) == 0:
        return False
    return s.astype(str).str.match(r'\d{4}-\d{2}-\d{2}T\d{2}\:\d{2}\:\d{2}(\.\d+)?Z').all()


def feature_type(df, column):
    ftype = 'categorical'
    if str(df[column].dtype).startswith('datetime') or is_timestamp(df[column]):
        ftype = 'timestamp'
    elif is_numeric(df, column):
        ftype = 'numerical'
    return ftype


intervals = {
    1: '1S',  # seconds
    5: '5S',  # 5 seconds
    10: '10S',  # 10 seconds
    30: '30S',  # 30 seconds
    60: '1T',  # minutes
    5 * 60: '5T',   # 5 minutes
    10 * 60: '10T',  # 10 minutes
    30 * 60: '30T',  # 30 minutes
    60 * 60: '1H',  # hours
    12 * 60 * 60: '12H',  # 12 hours
    24 * 60 * 60: '1D',  # days
    2 * 24 * 60 * 60: '2D',  # 2 days
    7 * 24 * 60 * 60: '1W',  # week
    30 * 24 * 60 * 60: '1M',  # 30 days
}


def get_rule(t0, t1):
    interval = (t1 - t0).total_seconds()
    res = 1
    for n, rule in intervals.items():
        if interval < n:
            continue
        res = interval/n
        if res >= 10 and res <= 40:
            break
    return rule


def timeseries(df, on, col, rule=None, func=pd.Series.count):
    # Need to convert to a usable timestamp
    ts = df[[on, col]].copy()
    if 'time' not in str(df[on].dtype):
        ts['timestamp'] = pd.to_datetime(df[on], infer_datetime_format=True, utc=True)
    else:
        ts['timestamp'] = df[on]
    ts['timestamp'] = ts['timestamp'].dt.tz_convert(None)
    ts = ts.drop(on, axis=1)

    if not rule:
        t0 = ts['timestamp'].min()
        t1 = ts['timestamp'].max()
        rule = get_rule(t0, t1)

    # Now do the actual resampling
    return ts.resample(rule, on='timestamp').apply(func)


def analytics(df):
    x_col = x_param
    y_col = y_param
    x = df[x_col]
    y = df[y_col]
    x_ftype = feature_type(df, x_col)
    y_ftype = feature_type(df, y_col)
    fig = None

    if y_ftype == 'numerical':
        if x_ftype == 'numerical':
            # scatterplot
            data = pd.DataFrame({x_col: x, y_col: y})
            fig = data.plot.scatter(x=x_col, y=y_col).get_figure()
            return fig
        elif x_ftype == 'categorical':
            # TODO: area chart as density plot
            pass
        elif x_ftype == 'timestamp':
            ts = timeseries(df, x_col, y_col, func=sum)
            return ts.plot.line(y=y_col).get_figure()
        else:
            # TODO: raise
            pass
    elif y_ftype == 'categorical':
        if x_ftype == 'categorical':
            # TODO: stacked or grouped bar chart
            pass
        elif x_ftype == 'timestamp':
            ts = timeseries(df, x_col, y_col)
            return ts.plot.line(y=y_col).get_figure()
        else:
            # ???
            pass
    else:
        # TODO: raise
        pass


if __name__ == "__main__":
    dfi = pd.read_parquet(INPUT_DATA_PATH)
    fig = analytics(dfi)
    if fig:
        fig.savefig(OUTPUT_DISP_PATH)
