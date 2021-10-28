FROM python:3.9

RUN pip install --upgrade pip && \
    pip install --no-cache-dir pandas pyarrow business-rules

WORKDIR /opt/analytics

ADD analytics.py /opt/analytics/
ADD rule_engine.py /opt/analytics/
ADD rules.json /opt/analytics/

CMD ["python3", "analytics.py"]
