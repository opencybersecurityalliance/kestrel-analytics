import os
import time
import pickle
import ipaddress
import numpy as np
import pandas as pd
import datetime as dt
import sklearn.cluster as cluster
from sklearn.cluster import KMeans
from sklearn.preprocessing import MinMaxScaler


DATA_PATH = "/data/input/0.parquet.gz"
DATA_PATH_1 = "/data/input/1.parquet.gz"
DATA_PATH_2 = "/data/input/2.parquet.gz"
OUTPUT_DATA_PATH = "/data/output/0.parquet.gz"


ku = int(os.environ["ku"])
ks = int(os.environ["ks"])
kd = int(os.environ["kd"])


def process(data):
    # need a method call to find weekday
    data["timestamp"] = pd.to_datetime(
        data["first_observed"], unit="ms", infer_datetime_format=True
    ).dt.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    data["timeofweek"] = data.apply(
        lambda row: (row["timestamp"] // 3600 + 24 * 2) % 168, axis=1
    )
    # the number of seconds passed from midnight Monday of that week.
    data["weekday"] = data.apply(
        lambda row: ((row["timestamp"] // 3600 + 24 * 2) % 168) // 24, axis=1
    )
    data["HourRange"] = data.apply(lambda row: (row["timeofweek"] % 24) // 6, axis=1)
    data["Days"] = data.apply(lambda row: (row["timestamp"] // (3600 * 24)), axis=1)
    data["Mo"] = data.apply(lambda row: 1 if (row["timeofweek"] < 24) else 0, axis=1)
    data["Tu"] = data.apply(
        lambda row: 1 if (row["timeofweek"] < 48) and (row["timeofweek"] >= 24) else 0,
        axis=1,
    )
    data["We"] = data.apply(
        lambda row: 1 if (row["timeofweek"] < 72) and (row["timeofweek"] >= 48) else 0,
        axis=1,
    )
    data["Th"] = data.apply(
        lambda row: 1 if (row["timeofweek"] < 96) and (row["timeofweek"] >= 72) else 0,
        axis=1,
    )
    data["Fr"] = data.apply(
        lambda row: 1 if (row["timeofweek"] < 120) and (row["timeofweek"] >= 96) else 0,
        axis=1,
    )
    data["Sa"] = data.apply(
        lambda row: 1
        if (row["timeofweek"] < 148) and (row["timeofweek"] >= 120)
        else 0,
        axis=1,
    )
    data["Su"] = data.apply(lambda row: 1 if (row["timeofweek"] >= 148) else 0, axis=1)
    data["0to6"] = data.apply(lambda row: 1 if (row["HourRange"] == 0) else 0, axis=1)
    data["6to12"] = data.apply(lambda row: 1 if (row["HourRange"] == 1) else 0, axis=1)
    data["12to18"] = data.apply(lambda row: 1 if (row["HourRange"] == 2) else 0, axis=1)
    data["18to0"] = data.apply(lambda row: 1 if (row["HourRange"] == 3) else 0, axis=1)
    data["NoOfRecords"] = 1

    return data


def sourceclustering(dfdata):
    sources = dfdata[["source", "username"]].groupby(["source"])["username"].nunique()
    temp = (
        dfdata[["source", "destination"]].groupby(["source"])["destination"].nunique()
    )
    sources = pd.merge(sources, temp, how="inner", on=["source"]).rename(
        columns={"username": "F1"}
    )
    temp = dfdata[["source", "Mo"]].groupby(["source"])["Mo"].sum()
    sources = pd.merge(sources, temp, how="inner", on=["source"])
    temp = dfdata[["source", "Tu"]].groupby(["source"])["Tu"].sum()
    sources = pd.merge(sources, temp, how="inner", on=["source"])
    temp = dfdata[["source", "We"]].groupby(["source"])["We"].sum()
    sources = pd.merge(sources, temp, how="inner", on=["source"])
    temp = dfdata[["source", "Th"]].groupby(["source"])["Th"].sum()
    sources = pd.merge(sources, temp, how="inner", on=["source"])
    temp = dfdata[["source", "Fr"]].groupby(["source"])["Fr"].sum()
    sources = pd.merge(sources, temp, how="inner", on=["source"])
    temp = dfdata[["source", "Sa"]].groupby(["source"])["Sa"].sum()
    sources = pd.merge(sources, temp, how="inner", on=["source"])
    temp = dfdata[["source", "Su"]].groupby(["source"])["Su"].sum()
    sources = pd.merge(sources, temp, how="inner", on=["source"])
    temp = dfdata[["source", "NoOfRecords"]].groupby(["source"])["NoOfRecords"].sum()
    sources = pd.merge(sources, temp, how="inner", on=["source"])
    temp = dfdata[["source", "0to6"]].groupby(["source"])["0to6"].sum()
    sources = pd.merge(sources, temp, how="inner", on=["source"])
    temp = dfdata[["source", "6to12"]].groupby(["source"])["6to12"].sum()
    sources = pd.merge(sources, temp, how="inner", on=["source"])
    temp = dfdata[["source", "12to18"]].groupby(["source"])["12to18"].sum()
    sources = pd.merge(sources, temp, how="inner", on=["source"])
    temp = dfdata[["source", "18to0"]].groupby(["source"])["18to0"].sum()
    sources = pd.merge(sources, temp, how="inner", on=["source"])
    temp = (
        dfdata[["source", "Days", "id"]]
        .groupby(["source", "Days"])["id"]
        .count()
        .reset_index()
        .rename(columns={"id": "Count"})
    )
    temp = (
        temp.groupby(["source"])["Count"]
        .mean()
        .reset_index()
        .rename(columns={"Count": "Mean"})
    )
    sources = pd.merge(sources, temp, how="inner", on=["source"])
    temp = (
        dfdata[["source", "destination", "id"]]
        .groupby(["source", "destination"])["id"]
        .count()
        .reset_index()
        .rename(columns={"id": "Count"})
    )
    temp = (
        temp.groupby(["source"])["Count"]
        .max()
        .reset_index()
        .rename(columns={"Count": "Max"})
    )
    sources = pd.merge(sources, temp, how="inner", on=["source"])

    mms = MinMaxScaler()
    mms.fit(
        sources[
            [
                "F1",
                "NoOfRecords",
                "Mean",
                "Max",
                "Mo",
                "Tu",
                "We",
                "Th",
                "Fr",
                "Sa",
                "Su",
                "0to6",
                "6to12",
                "12to18",
                "18to0",
            ]
        ]
    )
    sources[
        [
            "F1",
            "NoOfRecords",
            "Mean",
            "Max",
            "Mo",
            "Tu",
            "We",
            "Th",
            "Fr",
            "Sa",
            "Su",
            "0to6",
            "6to12",
            "12to18",
            "18to0",
        ]
    ] = mms.transform(
        sources[
            [
                "F1",
                "NoOfRecords",
                "Mean",
                "Max",
                "Mo",
                "Tu",
                "We",
                "Th",
                "Fr",
                "Sa",
                "Su",
                "0to6",
                "6to12",
                "12to18",
                "18to0",
            ]
        ]
    )
    kmeans = KMeans(n_clusters=ks, random_state=0)
    sources["c_src"] = kmeans.fit_predict(
        sources[
            [
                "F1",
                "NoOfRecords",
                "Mean",
                "Max",
                "Mo",
                "Tu",
                "We",
                "Th",
                "Fr",
                "Sa",
                "Su",
                "0to6",
                "6to12",
                "12to18",
                "18to0",
            ]
        ]
    )

    return sources


def usernamedomainclustering(dfdata):
    usernames = (
        dfdata[["username", "domain", "source"]]
        .groupby(["username", "domain"])["source"]
        .nunique()
    )
    temp = (
        dfdata[["username", "domain", "destination"]]
        .groupby(["username", "domain"])["destination"]
        .nunique()
    )
    usernames = pd.merge(
        usernames, temp, how="inner", on=["username", "domain"]
    ).rename(columns={"source": "F1", "destination": "F2"})
    temp = (
        dfdata[["username", "domain", "Mo"]].groupby(["username", "domain"])["Mo"].sum()
    )
    usernames = pd.merge(usernames, temp, how="inner", on=["username", "domain"])
    temp = (
        dfdata[["username", "domain", "Tu"]].groupby(["username", "domain"])["Tu"].sum()
    )
    usernames = pd.merge(usernames, temp, how="inner", on=["username", "domain"])
    temp = (
        dfdata[["username", "domain", "We"]].groupby(["username", "domain"])["We"].sum()
    )
    usernames = pd.merge(usernames, temp, how="inner", on=["username", "domain"])
    temp = (
        dfdata[["username", "domain", "Th"]].groupby(["username", "domain"])["Th"].sum()
    )
    usernames = pd.merge(usernames, temp, how="inner", on=["username", "domain"])
    temp = (
        dfdata[["username", "domain", "Fr"]].groupby(["username", "domain"])["Fr"].sum()
    )
    usernames = pd.merge(usernames, temp, how="inner", on=["username", "domain"])
    temp = (
        dfdata[["username", "domain", "Sa"]].groupby(["username", "domain"])["Sa"].sum()
    )
    usernames = pd.merge(usernames, temp, how="inner", on=["username", "domain"])
    temp = (
        dfdata[["username", "domain", "Su"]].groupby(["username", "domain"])["Su"].sum()
    )
    usernames = pd.merge(usernames, temp, how="inner", on=["username", "domain"])
    temp = (
        dfdata[["username", "domain", "NoOfRecords"]]
        .groupby(["username", "domain"])["NoOfRecords"]
        .sum()
    )
    usernames = pd.merge(usernames, temp, how="inner", on=["username", "domain"])
    temp = (
        dfdata[["username", "domain", "0to6"]]
        .groupby(["username", "domain"])["0to6"]
        .sum()
    )
    usernames = pd.merge(usernames, temp, how="inner", on=["username", "domain"])
    temp = (
        dfdata[["username", "domain", "6to12"]]
        .groupby(["username", "domain"])["6to12"]
        .sum()
    )
    usernames = pd.merge(usernames, temp, how="inner", on=["username", "domain"])
    temp = (
        dfdata[["username", "domain", "12to18"]]
        .groupby(["username", "domain"])["12to18"]
        .sum()
    )
    usernames = pd.merge(usernames, temp, how="inner", on=["username", "domain"])
    temp = (
        dfdata[["username", "domain", "18to0"]]
        .groupby(["username", "domain"])["18to0"]
        .sum()
    )
    usernames = pd.merge(usernames, temp, how="inner", on=["username", "domain"])
    temp = (
        dfdata[["username", "domain", "Days", "id"]]
        .groupby(["username", "domain", "Days"])["id"]
        .count()
        .reset_index()
        .rename(columns={"id": "Count"})
    )
    temp = (
        temp.groupby(["username", "domain"])["Count"]
        .mean()
        .reset_index()
        .rename(columns={"Count": "Mean"})
    )
    usernames = pd.merge(usernames, temp, how="inner", on=["username", "domain"])
    temp = (
        dfdata[["username", "domain", "destination", "id"]]
        .groupby(["username", "domain", "destination"])["id"]
        .count()
        .reset_index()
        .rename(columns={"id": "Count"})
    )
    temp = (
        temp.groupby(["username", "domain"])["Count"]
        .max()
        .reset_index()
        .rename(columns={"Count": "Max"})
    )
    usernames = pd.merge(usernames, temp, how="inner", on=["username", "domain"])

    mms = MinMaxScaler()
    mms.fit(
        usernames[
            [
                "F1",
                "F2",
                "NoOfRecords",
                "Mean",
                "Max",
                "Mo",
                "Tu",
                "We",
                "Th",
                "Fr",
                "Sa",
                "Su",
                "0to6",
                "6to12",
                "12to18",
                "18to0",
            ]
        ]
    )
    usernames[
        [
            "F1",
            "F2",
            "NoOfRecords",
            "Mean",
            "Max",
            "Mo",
            "Tu",
            "We",
            "Th",
            "Fr",
            "Sa",
            "Su",
            "0to6",
            "6to12",
            "12to18",
            "18to0",
        ]
    ] = mms.transform(
        usernames[
            [
                "F1",
                "F2",
                "NoOfRecords",
                "Mean",
                "Max",
                "Mo",
                "Tu",
                "We",
                "Th",
                "Fr",
                "Sa",
                "Su",
                "0to6",
                "6to12",
                "12to18",
                "18to0",
            ]
        ]
    )
    kmeans = KMeans(n_clusters=ku, random_state=0)
    usernames["c_usr"] = kmeans.fit_predict(
        usernames[
            [
                "F1",
                "F2",
                "NoOfRecords",
                "Mean",
                "Max",
                "Mo",
                "Tu",
                "We",
                "Th",
                "Fr",
                "Sa",
                "Su",
                "0to6",
                "6to12",
                "12to18",
                "18to0",
            ]
        ]
    )

    return usernames


def usernameclustering(dfdata):
    usernames = dfdata[["username", "source"]].groupby(["username"])["source"].nunique()
    temp = (
        dfdata[["username", "destination"]]
        .groupby(["username"])["destination"]
        .nunique()
    )
    usernames = pd.merge(usernames, temp, how="inner", on=["username"]).rename(
        columns={"source": "F1", "destination": "F2"}
    )
    temp = dfdata[["username", "Mo"]].groupby(["username"])["Mo"].sum()
    usernames = pd.merge(usernames, temp, how="inner", on=["username"])
    temp = dfdata[["username", "Tu"]].groupby(["username"])["Tu"].sum()
    usernames = pd.merge(usernames, temp, how="inner", on=["username"])
    temp = dfdata[["username", "We"]].groupby(["username"])["We"].sum()
    usernames = pd.merge(usernames, temp, how="inner", on=["username"])
    temp = dfdata[["username", "Th"]].groupby(["username"])["Th"].sum()
    usernames = pd.merge(usernames, temp, how="inner", on=["username"])
    temp = dfdata[["username", "Fr"]].groupby(["username"])["Fr"].sum()
    usernames = pd.merge(usernames, temp, how="inner", on=["username"])
    temp = dfdata[["username", "Sa"]].groupby(["username"])["Sa"].sum()
    usernames = pd.merge(usernames, temp, how="inner", on=["username"])
    temp = dfdata[["username", "Su"]].groupby(["username"])["Su"].sum()
    usernames = pd.merge(usernames, temp, how="inner", on=["username"])
    temp = (
        dfdata[["username", "NoOfRecords"]].groupby(["username"])["NoOfRecords"].sum()
    )
    usernames = pd.merge(usernames, temp, how="inner", on=["username"])
    temp = dfdata[["username", "0to6"]].groupby(["username"])["0to6"].sum()
    usernames = pd.merge(usernames, temp, how="inner", on=["username"])
    temp = dfdata[["username", "6to12"]].groupby(["username"])["6to12"].sum()
    usernames = pd.merge(usernames, temp, how="inner", on=["username"])
    temp = dfdata[["username", "12to18"]].groupby(["username"])["12to18"].sum()
    usernames = pd.merge(usernames, temp, how="inner", on=["username"])
    temp = dfdata[["username", "18to0"]].groupby(["username"])["18to0"].sum()
    usernames = pd.merge(usernames, temp, how="inner", on=["username"])
    temp = (
        dfdata[["username", "Days", "id"]]
        .groupby(["username", "Days"])["id"]
        .count()
        .reset_index()
        .rename(columns={"id": "Count"})
    )
    temp = (
        temp.groupby(["username"])["Count"]
        .mean()
        .reset_index()
        .rename(columns={"Count": "Mean"})
    )
    usernames = pd.merge(usernames, temp, how="inner", on=["username"])
    temp = (
        dfdata[["username", "destination", "id"]]
        .groupby(["username", "destination"])["id"]
        .count()
        .reset_index()
        .rename(columns={"id": "Count"})
    )
    temp = (
        temp.groupby(["username"])["Count"]
        .max()
        .reset_index()
        .rename(columns={"Count": "Max"})
    )
    usernames = pd.merge(usernames, temp, how="inner", on=["username"])

    mms = MinMaxScaler()
    mms.fit(
        usernames[
            [
                "F1",
                "F2",
                "NoOfRecords",
                "Mean",
                "Max",
                "Mo",
                "Tu",
                "We",
                "Th",
                "Fr",
                "Sa",
                "Su",
                "0to6",
                "6to12",
                "12to18",
                "18to0",
            ]
        ]
    )
    usernames[
        [
            "F1",
            "F2",
            "NoOfRecords",
            "Mean",
            "Max",
            "Mo",
            "Tu",
            "We",
            "Th",
            "Fr",
            "Sa",
            "Su",
            "0to6",
            "6to12",
            "12to18",
            "18to0",
        ]
    ] = mms.transform(
        usernames[
            [
                "F1",
                "F2",
                "NoOfRecords",
                "Mean",
                "Max",
                "Mo",
                "Tu",
                "We",
                "Th",
                "Fr",
                "Sa",
                "Su",
                "0to6",
                "6to12",
                "12to18",
                "18to0",
            ]
        ]
    )
    kmeans = KMeans(n_clusters=ku, random_state=0)
    usernames["c_usr"] = kmeans.fit_predict(
        usernames[
            [
                "F1",
                "F2",
                "NoOfRecords",
                "Mean",
                "Max",
                "Mo",
                "Tu",
                "We",
                "Th",
                "Fr",
                "Sa",
                "Su",
                "0to6",
                "6to12",
                "12to18",
                "18to0",
            ]
        ]
    )

    return usernames


def destinationclustering(dfdata):
    destinations = (
        dfdata[["destination", "username"]]
        .groupby(["destination"])["username"]
        .nunique()
    )
    temp = (
        dfdata[["destination", "source"]].groupby(["destination"])["source"].nunique()
    )
    destinations = pd.merge(destinations, temp, how="inner", on=["destination"]).rename(
        columns={"username": "F1", "source": "F2"}
    )
    temp = dfdata[["destination", "Mo"]].groupby(["destination"])["Mo"].sum()
    destinations = pd.merge(destinations, temp, how="inner", on=["destination"])
    temp = dfdata[["destination", "Tu"]].groupby(["destination"])["Tu"].sum()
    destinations = pd.merge(destinations, temp, how="inner", on=["destination"])
    temp = dfdata[["destination", "We"]].groupby(["destination"])["We"].sum()
    destinations = pd.merge(destinations, temp, how="inner", on=["destination"])
    temp = dfdata[["destination", "Th"]].groupby(["destination"])["Th"].sum()
    destinations = pd.merge(destinations, temp, how="inner", on=["destination"])
    temp = dfdata[["destination", "Fr"]].groupby(["destination"])["Fr"].sum()
    destinations = pd.merge(destinations, temp, how="inner", on=["destination"])
    temp = dfdata[["destination", "Sa"]].groupby(["destination"])["Sa"].sum()
    destinations = pd.merge(destinations, temp, how="inner", on=["destination"])
    temp = dfdata[["destination", "Su"]].groupby(["destination"])["Su"].sum()
    destinations = pd.merge(destinations, temp, how="inner", on=["destination"])
    temp = (
        dfdata[["destination", "NoOfRecords"]]
        .groupby(["destination"])["NoOfRecords"]
        .sum()
    )
    destinations = pd.merge(destinations, temp, how="inner", on=["destination"])
    temp = dfdata[["destination", "0to6"]].groupby(["destination"])["0to6"].sum()
    destinations = pd.merge(destinations, temp, how="inner", on=["destination"])
    temp = dfdata[["destination", "6to12"]].groupby(["destination"])["6to12"].sum()
    destinations = pd.merge(destinations, temp, how="inner", on=["destination"])
    temp = dfdata[["destination", "12to18"]].groupby(["destination"])["12to18"].sum()
    destinations = pd.merge(destinations, temp, how="inner", on=["destination"])
    temp = dfdata[["destination", "18to0"]].groupby(["destination"])["18to0"].sum()
    destinations = pd.merge(destinations, temp, how="inner", on=["destination"])
    temp = (
        dfdata[["destination", "Days", "id"]]
        .groupby(["destination", "Days"])["id"]
        .count()
        .reset_index()
        .rename(columns={"id": "Count"})
    )
    temp = (
        temp.groupby(["destination"])["Count"]
        .mean()
        .reset_index()
        .rename(columns={"Count": "Mean"})
    )
    destinations = pd.merge(destinations, temp, how="inner", on=["destination"])
    temp = (
        dfdata[["source", "destination", "id"]]
        .groupby(["source", "destination"])["id"]
        .count()
        .reset_index()
        .rename(columns={"id": "Count"})
    )
    temp = (
        temp.groupby(["destination"])["Count"]
        .max()
        .reset_index()
        .rename(columns={"Count": "Max"})
    )
    destinations = pd.merge(destinations, temp, how="inner", on=["destination"])

    mms = MinMaxScaler()
    mms.fit(
        destinations[
            [
                "F1",
                "F2",
                "NoOfRecords",
                "Mean",
                "Max",
                "Mo",
                "Tu",
                "We",
                "Th",
                "Fr",
                "Sa",
                "Su",
                "0to6",
                "6to12",
                "12to18",
                "18to0",
            ]
        ]
    )
    destinations[
        [
            "F1",
            "F2",
            "NoOfRecords",
            "Mean",
            "Max",
            "Mo",
            "Tu",
            "We",
            "Th",
            "Fr",
            "Sa",
            "Su",
            "0to6",
            "6to12",
            "12to18",
            "18to0",
        ]
    ] = mms.transform(
        destinations[
            [
                "F1",
                "F2",
                "NoOfRecords",
                "Mean",
                "Max",
                "Mo",
                "Tu",
                "We",
                "Th",
                "Fr",
                "Sa",
                "Su",
                "0to6",
                "6to12",
                "12to18",
                "18to0",
            ]
        ]
    )
    kmeans = KMeans(n_clusters=kd, random_state=0)
    destinations["c_dst"] = kmeans.fit_predict(
        destinations[
            [
                "F1",
                "F2",
                "NoOfRecords",
                "Mean",
                "Max",
                "Mo",
                "Tu",
                "We",
                "Th",
                "Fr",
                "Sa",
                "Su",
                "0to6",
                "6to12",
                "12to18",
                "18to0",
            ]
        ]
    )

    return destinations


if __name__ == "__main__":
    out = pd.read_parquet(DATA_PATH)
    in1 = pd.read_parquet(DATA_PATH_1)
    in2 = pd.read_parquet(DATA_PATH_2)
    out["index1"] = out.index

    # data = pd.merge(in1,in2, how='inner', on =['first_observed'])
    data = pd.merge(in1, in2, left_index=True, right_index=True)
    data["index1"] = data.index
    data["first_observed"] = data["first_observed_x"]
    data["id"] = data["id_x"]
    data["source"] = data["src_ref.value"]
    data["destination"] = data["dst_ref.value"]
    data["username"] = data["user_id"]
    # dfdata['domain'] = dfdata['objects.3.value']

    dftest = data[data["status"].astype(str).str.match("unknown")].copy()
    dftrain = data[data["status"].astype(str).str.match("benign")].copy()
    dftest = process(dftest)
    dftrain = process(dftrain)
    csources = sourceclustering(dftrain)[["source", "c_src"]]
    dftrain = pd.merge(csources, dftrain, how="inner", on=["source"])
    cusernames = usernameclustering(dftrain)[["username", "c_usr"]]
    dftrain = pd.merge(cusernames, dftrain, how="inner", on=["username"])
    cdestination = destinationclustering(dftrain)[["destination", "c_dst"]]
    dftrain = pd.merge(cdestination, dftrain, how="inner", on=["destination"])

    dftest = pd.merge(csources[["source", "c_src"]], dftest, how="right", on=["source"])
    dftest = pd.merge(
        cusernames[["username", "c_usr"]], dftest, how="right", on=["username"]
    )
    dftest = pd.merge(
        cdestination[["destination", "c_dst"]], dftest, how="right", on=["destination"]
    )
    dftest = pd.merge(
        dftrain[["c_usr", "c_src", "c_dst", "status"]].drop_duplicates(),
        dftest[
            [
                "index1",
                "first_observed",
                "source",
                "destination",
                "username",
                "c_usr",
                "c_src",
                "c_dst",
            ]
        ],
        how="right",
        on=["c_usr", "c_src", "c_dst"],
    )

    dftest["status"] = dftest["status"].fillna("malicious")
    dftest["c_usr"] = dftest["c_usr"].fillna(-1)
    dftest["c_src"] = dftest["c_src"].fillna(-1)
    dftest["c_dst"] = dftest["c_dst"].fillna(-1)

    # data=pd.merge(data[['first_observed','source','destination','username']],dftest,how='right', on = ['source','destination','username'])

    data = pd.concat(
        [
            dftrain[
                [
                    "index1",
                    "first_observed",
                    "source",
                    "destination",
                    "username",
                    "c_usr",
                    "c_src",
                    "c_dst",
                    "status",
                ]
            ],
            dftest[
                [
                    "index1",
                    "first_observed",
                    "source",
                    "destination",
                    "username",
                    "c_usr",
                    "c_src",
                    "c_dst",
                    "status",
                ]
            ],
        ],
        ignore_index=True,
    )
    out = pd.merge(
        out,
        data[
            [
                "index1",
                "username",
                "c_usr",
                "source",
                "c_src",
                "destination",
                "c_dst",
                "status",
            ]
        ],
        how="inner",
        on=["index1"],
    )

    out.to_parquet(OUTPUT_DATA_PATH, compression="gzip")
