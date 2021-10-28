FROM python:3.9

RUN pip install --upgrade pip && \
    pip install --no-cache-dir pandas pyarrow requests

WORKDIR /opt/analytics

ADD analytics.py .

CMD ["python3", "analytics.py"]
