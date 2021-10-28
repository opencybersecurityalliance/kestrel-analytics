################################################################
#
# Copyright 2021 International Business Machines
# 
# License: Apache 2.0
#
################################################################

FROM python:3.9

RUN pip install --upgrade pip && \
    pip install --no-cache-dir pandas pyarrow && \
    apt-get update && \
    apt-get install -y dnsutils whois && \
    apt-get clean


WORKDIR /opt/analytics

ADD annotateip.py NameInspector.pl WhoisMapper.cf exploreIP.pl /opt/analytics/

CMD ["python3", "annotateip.py"]
