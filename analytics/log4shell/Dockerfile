################################################################
#               Kestrel Analytics Container Template
#
# Build the analytics container:
#   docker build -t kestrel-analytics-log4shell .
#
# Call the analytics in Kestrel
#   APPLY log4shell ON varX
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
    pip install --no-cache-dir pandas pyarrow urllib3 lark-parser

WORKDIR /opt/analytics

ADD analytics.py .
ADD unlog4shell.py .

CMD ["python", "analytics.py"]
