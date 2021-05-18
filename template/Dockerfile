################################################################
#               Kestrel Analytics Container Template
#
# Build the analytics container:
#   docker build -t kestrel-analytics-xxx .
#
# Call the analytics in Kestrel
#   APPLY xxx ON varX
#
# Input/output:
#   - volume "/data" will be mounted by Kestrel runtime
#   - input: Kestrel variable arguments of APPLY:
#       - /data/input/0.parquet.gz
#       - /data/input/1.parquet.gz
#       - ...
#   - output: updated Kestrel variables (same index)
#       - /data/input/0.parquet.gz
#       - /data/input/1.parquet.gz
#       - ...
#   - output display object:
#       - /data/display/ret.html
#
################################################################

FROM python:3

RUN pip install --upgrade pip && \
    pip install --no-cache-dir pandas pyarrow

WORKDIR /opt/analytics

ADD analytics.py .

CMD ["python", "analytics.py"]
