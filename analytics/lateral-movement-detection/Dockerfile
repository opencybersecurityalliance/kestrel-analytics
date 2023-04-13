FROM python:3.8.10

RUN pip install --upgrade pip && \
    pip install --no-cache-dir pandas pyarrow scikit-learn

WORKDIR /opt/analytics


ADD DetectLM.py .

CMD ["python", "DetectLM.py"]
