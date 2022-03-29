################################################################
#               Kestrel Analytics - scikit-learn clustering
#
# Build the analytics container:
#   docker build -t kestrel-analytics-sklearn-cluster .
#
# Call the analytics in Kestrel
#   APPLY sklearn-cluster ON my_var WITH n=N,columns=...
#
################################################################

FROM python:3.9

RUN pip install --upgrade pip && \
    pip install --no-cache-dir pandas pyarrow scikit-learn gower

WORKDIR /opt/analytics

ADD analytics.py .

CMD ["python", "analytics.py"]
