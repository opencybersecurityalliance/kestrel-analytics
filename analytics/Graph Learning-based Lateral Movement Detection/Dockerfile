FROM python:3

RUN pip install --upgrade pip && \
   pip install --no-cache-dir pandas pyarrow scikit-learn gensim xgboost networkx 
  
WORKDIR /opt/analytics


ADD main.py .
ADD classify.py .
ADD deepwalk.py .
ADD walker.py .

CMD ["python", "main.py"]
