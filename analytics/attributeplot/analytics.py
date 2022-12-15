#!/usr/bin/env python3

import os
import pandas as pd
import numpy as np
from matplotlib import rcParams


# Kestrel analytics default paths
INPUT_DATA_PATH = "/data/input/0.parquet.gz"
OUTPUT_DISP_PATH = "/data/display/plot.html"

rcParams.update({"figure.autolayout": True})


class PlotFailure(Exception):
    pass


def is_numeric(df, column):
    if column.endswith("_id") or column == "pid":
        return False
    if str(df[column].dtype) in ["Int32", "Int64"]:
        return True
    return np.issubdtype(df[column].dtype, np.number)


def is_integer(series):
    """Detect if a numeric array/series/column is all integers"""
    if str(series.dtype) in ["Int32", "Int64"]:
        return True
    return np.issubdtype(series.dtype, np.number) and (np.modf(series)[0].sum() == 0.0)


def is_timestamp(series):
    dtype = str(series.dtype)
    if "time" in dtype.lower():
        return True
    s = series.dropna()
    if len(s.index) == 0:
        return False
    return (
        s.astype(str).str.match(r"\d{4}-\d{2}-\d{2}T\d{2}\:\d{2}\:\d{2}(\.\d+)?Z").all()
    )


def feature_type(df, column):
    if not column:
        return None
    if isinstance(column, list):
        return [feature_type(df, c) for c in column]
    ftype = "categorical"
    if str(df[column].dtype).startswith("datetime") or is_timestamp(df[column]):
        ftype = "timestamp"
    elif is_numeric(df, column):
        ftype = "numerical"
    return ftype


intervals = {
    1: "1S",  # seconds
    5: "5S",  # 5 seconds
    10: "10S",  # 10 seconds
    30: "30S",  # 30 seconds
    60: "1T",  # minutes
    5 * 60: "5T",  # 5 minutes
    10 * 60: "10T",  # 10 minutes
    30 * 60: "30T",  # 30 minutes
    60 * 60: "1H",  # hours
    12 * 60 * 60: "12H",  # 12 hours
    24 * 60 * 60: "1D",  # days
    2 * 24 * 60 * 60: "2D",  # 2 days
    7 * 24 * 60 * 60: "1W",  # week
    30 * 24 * 60 * 60: "1M",  # 30 days
}


def get_rule(t0, t1):
    interval = (t1 - t0).total_seconds()
    res = 1
    for n, rule in intervals.items():
        if interval < n:
            continue
        res = interval / n
        if res >= 10 and res <= 40:
            break
    return rule


def timeseries(df, on, col, rule=None, func=pd.Series.count):
    # Need to convert to a usable timestamp
    ts = df[[on, col]].copy()
    if "time" not in str(df[on].dtype):
        ts["timestamp"] = pd.to_datetime(df[on], infer_datetime_format=True, utc=True)
    else:
        ts["timestamp"] = df[on]
    ts["timestamp"] = ts["timestamp"].dt.tz_convert(None)
    ts = ts.drop(on, axis=1)

    if not rule:
        t0 = ts["timestamp"].min()
        t1 = ts["timestamp"].max()
        rule = get_rule(t0, t1)

    # Now do the actual resampling
    return ts.resample(rule, on="timestamp").apply(func)


PLOT_MATRIX = {
    "categorical": {
        "categorical": None,
        "numerical": "area",
        "timestamp": None,
        "None": "count_x",
    },
    "numerical": {
        "categorical": None,
        "numerical": "scatter",
        "timestamp": None,
        "None": "dist_x",
    },
    "timestamp": {
        "categorical": "time_count",
        "numerical": "time_sum",
        "timestamp": None,
        "None": None,
    },
    "None": {
        "categorical": "count_y",
        "numerical": "dist_y",
        "timestamp": None,
        "None": None,
    },
}


def bar(df, x, y):
    """Create a simple plot"""
    return df.plot.bar(x=x, y=y, stacked=False).get_figure()


def area(df, x, y):
    """Create an area plot"""
    return df.plot.bar(x=x, y=y, stacked=False).get_figure()


def dist(df, col):
    """Create a histogram or box plots (if `col` is a list)"""
    if isinstance(col, list):
        return df.boxplot(column=col).get_figure()
    return df[col].plot(kind="hist").get_figure()


def dist_x(df, x, y):
    """Create a histogram or box plots (if `x` is a list)"""
    return dist(df, x)


def dist_y(df, x, y):
    """Create a histogram or box plots (if `y` is a list)"""
    return dist(df, y)


def count_x(df, x, y):
    """Create a bar plot of the count of `x` values"""
    return df[x].value_counts().plot(kind="bar").get_figure()


def count_y(df, x, y):
    """Create a horizontal bar plot of the count of `y` values"""
    return df[y].value_counts().plot(kind="barh").get_figure()


def scatter(df, x, y):
    """Create a scatter plot"""
    return df.plot.scatter(x=x, y=y).get_figure()


def time_chart(df, x, y, func):
    ts = timeseries(df, x, y, func=func)
    return ts.plot.line(y=y).get_figure()


def time_count(df, x, y):
    """Create a timechart with the count of `y` values per time period"""
    return time_chart(df, x, y, pd.Series.count)


def time_sum(df, x, y):
    """Create a timechart with the sum of `y` values per time period"""
    return time_chart(df, x, y, sum)


def analytics(df):
    x_col = os.environ.get("XPARAM")
    y_col = os.environ.get("YPARAM")
    plot_type = os.environ.get("PLOTTYPE")
    if not x_col and not y_col:
        raise Exception("No X or Y parameter specified")

    if x_col and "," in x_col:
        x_col = x_col.split(",")
    x_ftype = feature_type(df, x_col)
    if isinstance(x_ftype, list):
        ftypes = set(x_ftype)
        if len(ftypes) > 1:
            raise PlotFailure(
                f'Not implemented: no plot type for "{x_ftype}" (must be single type)'
            )
        x_ftype = x_ftype[0]
    y_ftype = feature_type(df, y_col)

    if not plot_type:
        plot_type = PLOT_MATRIX[str(x_ftype)][str(y_ftype)]
    if plot_type:
        return globals()[plot_type](df, x_col, y_col)
    raise PlotFailure(f'Not implemented: no plot type for "{y_ftype}" over "{x_ftype}"')


if __name__ == "__main__":
    dfi = pd.read_parquet(INPUT_DATA_PATH)
    fig = analytics(dfi)
    if fig:
        fig.savefig(OUTPUT_DISP_PATH, format="svg")
