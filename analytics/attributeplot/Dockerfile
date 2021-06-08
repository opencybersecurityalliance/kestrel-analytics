################################################################
#               Kestrel Analytics: Attribute Plot
#
# Build the analytics container:
#   docker build -t kestrel-attrib-plot .
#
################################################################

FROM python:3

RUN pip install --upgrade pip && \
    pip install --no-cache-dir pandas pyarrow matplotlib && \
    apt-get update && \
    apt-get clean


WORKDIR /opt/analytics

ADD analytics.py  /opt/analytics/

CMD ["python3", "analytics.py"]
