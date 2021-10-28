FROM python:3.9

RUN pip install --upgrade pip && \
    pip install --no-cache-dir pandas pyarrow geoip2 folium ipython

WORKDIR /opt/analytics

ADD analytics.py .
ADD GeoLite2-City.mmdb .

CMD ["python3", "analytics.py"]
