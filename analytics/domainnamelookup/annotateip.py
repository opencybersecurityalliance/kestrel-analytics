#!/usr/bin/env python3
#
# Copyright 2021 International Business Machines
# 
# License: Apache 2.0
#
import pandas as pd
import subprocess

#
# This analytic adds two columns based on the destination IP address
#
#  x_domain_name ->  The DNS name that the IP address inverse resolves to.
#                    Note that this may not, and frequently does not,
#                    correspond to the FQDN that was queried and resolved
#                    to the IP.  It also frequently will not resolve.
#
#  x_domain_organization -> The organization, from 'whois', associated with
#                    the IP network containing this IP address.
#
#  This analytic requires Internet access to retrieve the information.
#
#
#  It has no long term storage.  It does cache in memory the lookups in
#  order to avoid duplicate lookups during a single run.
#
#  Doug Schales - schales@us.ibm.com
#
#  Additional Files:
#
#         exploreIP.pl, NameInspector.pl, WhoisMapper.cf
#
#  Dependencies:
#
#         Perl for 'exploreIP.pl' and 'NameInspector.pl'
#         dig for 'exploreIP.pl'
#         whois for 'NameInspector'
#
#------------------------------------------------------------------------
# THL analytics default paths
INPUT_DATA_PATH = "/data/input/0.parquet.gz"
OUTPUT_DATA_PATH = "/data/output/0.parquet.gz"

def analytics(dataframe):
    # analyze data in dataframe

    # provide insights or additional knowledge
    newattr = ["" for i in range(dataframe.shape[0])]
    cache={}

    dataframe["x_domain_name"] = newattr
    dataframe["x_domain_organization"] = newattr

    cacheHits=0
    lookups=0

    #
    # This is to disable warnings for the
    #    dataframe[<key>][i] = value
    # The attempt to use the "better" method (commented out) from
    # the documentation results in a mess in the output.  
    #
    pd.set_option('mode.chained_assignment', None)

    for i in range(dataframe.shape[0]):
        #ndx = str(i)
        ip = dataframe["dst_ref.value"][i]
        if ip in cache:
            cacheHits = cacheHits + 1
            if 'ptr' in cache[ip]:
                dataframe["x_domain_name"][i] = cache[ip]["ptr"]
                #dataframe.loc[:, ("x_domain_name",ndx)] = cache[ip]["ptr"]
            if 'org' in cache[ip]:
                dataframe["x_domain_organization"][i] = cache[ip]["org"]
                #dataframe.loc[:, ("x_domain_organization",ndx)] = cache[ip]["org"]
        else:
            cache[ip] = {}
            lookups = lookups + 1
            exploreIP = subprocess.Popen(['./exploreIP.pl', str(ip)],
                                         stdout=subprocess.PIPE)
            if exploreIP.returncode == None:
                for line in exploreIP.stdout:
                    # default codec of Perl
                    line = line.decode("ISO-8859-1").rstrip()
                    word = line.split(':')
                    if word[0] == 'ptr':
                        revlookup = word[1].lstrip()
                        cache[ip]['ptr'] = revlookup
                        dataframe["x_domain_name"][i] = revlookup
                        #dataframe.loc[:,("x_domain_name", ndx)] = revlookup
                    elif word[0] == 'organization':
                        org = word[1].lstrip()
                        cache[ip]['org'] = org
                        dataframe["x_domain_organization"][i] = org
                        #dataframe.loc[:,("x_domain_organization", ndx)] = org

    #print("Cache hits: " + str(cacheHits) + ", Lookups: " + str(lookups))
    return dataframe

if __name__ == "__main__":
    dfi = pd.read_parquet(INPUT_DATA_PATH)
    dfo = analytics(dfi)
    dfo.to_parquet(OUTPUT_DATA_PATH, compression="gzip")
