import os
import logging
import tempfile
import shutil
import json
import ipaddress
import gzip
import pandas as pd
from tabulate import tabulate
import numpy as np
import scipy.stats

logger = logging.getLogger("demo." + __name__)

# THL analytics default paths
INPUT_DATA_PATH = "/data/input/0.parquet.gz"
OUTPUT_DATA_PATH = "/data/output/0.parquet.gz"

sensitive_ips = [ipaddress.IPv4Address('9.59.150.142')]

def build_model_pdf(p):
    #unzip to folder
    tempinputdir = tempfile.mkdtemp(dir='/var/tmp/')
    with open(tempinputdir + "/modelinput.parquet.gz", "wb") as f:
      f.write(p)
    df = pd.read_parquet(tempinputdir+'/modelinput.parquet.gz')
  
    # key: hr in the 24hr period
    # value: minutes in during that hour that connection occurred
    time_buckets = {}
    for index, row in df.iterrows():
      hr = int(row['first_observed'].split("T")[1].split(":")[0])
      mn = int(row['first_observed'].split("T")[1].split(":")[1])
      sec = int(row['first_observed'].split("T")[1].split(":")[2][:-5])
      if hr not in time_buckets:
          time_buckets[hr] = []
      time_buckets[hr].append(mn * 60 + sec)

    bins = [0,60*10*1,60*10*2,60*10*3,60*10*4,60*10*5,60*10*6]
    for hr in range(0,24):
      if hr in time_buckets:
        hist = np.histogram(time_buckets[hr], bins=bins)
      else:
        hist = np.histogram([], bins=bins)
      logger.info(str(hist))
      np.save('/opt/dataexfil/model/' + str(hr), hist, allow_pickle=True)

    # remove temp dir
    shutil.rmtree(tempinputdir)

def forecast_pdf(df):
    prop = []
    for index, row in df.iterrows():
      hr = int(row['first_observed'].split("T")[1].split(":")[0])
      mn = int(row['first_observed'].split("T")[1].split(":")[1])
      sec = int(row['first_observed'].split("T")[1].split(":")[2][:-5])

      m_hist = np.load('/opt/dataexfil/model/' + str(hr)+'.npy', allow_pickle=True)
      #hist_dist = scipy.stats.rv_histogram(m_hist)
      #p = hist_dist.pdf(mn*60+sec)
      tot = 0
      for h in m_hist[0]:
        tot += h
      b = int((mn*60+sec)/600)
      p = m_hist[0][b]/tot
      prop.append(1-p)

    logger.info(str(prop))
    df["x_exfil_op_probability"] = prop

    return df 

def categorize(df):
    ibmips = ipaddress.ip_network('9.0.0.0/8')
    categories = []
    for index, row in df.iterrows():
      cat = 'Unknown-'
      srcip = ipaddress.ip_address(row['src_ref.value'])
      dstip = ipaddress.ip_address(row['dst_ref.value'])
      if srcip in sensitive_ips:
        cat = 'Sensitive->'
      elif srcip.is_private:
        cat = 'Private->'
      elif srcip in ibmips:
        cat = 'IBM->'
      elif not dstip.is_private and not dstip in ibmips:
        cat = 'External->'

      if not dstip.is_private and not dstip in ibmips:
        cat += 'External'
      elif dstip in ibmips:
        cat += 'IBM'
      else:
        cat += 'Unknown'
      categories.append(cat)

    df["x_possible_exfil_op"] = categories

    return df

def eval(df):
    # generate catgories
    df = categorize(df)
    # generate prob
    df = forecast_pdf(df)

    logger.info(tabulate(df, headers='keys', tablefmt='psql'))

    return df

def analytics(dataframe):
    # analyze data in dataframe
    dataframe = eval(dataframe)

    # return a list of entities/SCOs
    return dataframe

if __name__ == "__main__":
    dfi = pd.read_parquet(INPUT_DATA_PATH)
    dfo = analytics(dfi)
    dfo.to_parquet(OUTPUT_DATA_PATH, compression="gzip")
