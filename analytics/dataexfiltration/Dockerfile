FROM python:3.9

RUN pip install --upgrade pip && \
    pip install --no-cache-dir pandas pyarrow flask flask-cors requests tabulate sklearn

WORKDIR /opt/analytics

COPY *.py ./
COPY *.conf ./
RUN mkdir -p /opt/dataexfil/model/
COPY model/* /opt/dataexfil/model/

CMD ["python3", "analytics.py"]
