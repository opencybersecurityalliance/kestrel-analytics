import os
import numpy as np
import time
import pandas as pd
from classify import  Classifier
from deepwalk import DeepWalk
from xgboost import XGBClassifier
from sklearn.linear_model import LogisticRegression
from sklearn import svm
from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier




import networkx as nx



DATA_PATH = "/data/input/0.parquet.gz"
DATA_PATH_1 = "/data/input/1.parquet.gz"
DATA_PATH_2 = "/data/input/2.parquet.gz"
OUTPUT_DATA_PATH = "/data/output/0.parquet.gz"

walk_length = int(os.environ['walkLength'])
classificationMethod= os.environ['classifier']

def evaluate_embeddings(embeddings,data):
 
    if classificationMethod == "svm":
    	clf = Classifier(embeddings=embeddings, clf=svm.SVC(probability=True))
    elif classificationMethod == "knn":
    	clf = Classifier(embeddings=embeddings, clf=KNeighborsClassifier())
    elif classificationMethod == "xgboost":
    	clf = Classifier(embeddings=embeddings, clf=XGBClassifier())
    elif classificationMethod == "logisticRegression":
    	clf = Classifier(embeddings=embeddings, clf=LogisticRegression())
    elif classificationMethod == "randomforest":
    	clf = Classifier(embeddings=embeddings, clf=RandomForestClassifier())
    	
    return clf.train_evaluate(data)

   



if __name__ == "__main__":
    out = pd.read_parquet(DATA_PATH)
    in1 = pd.read_parquet(DATA_PATH_1)
    in2 = pd.read_parquet(DATA_PATH_2)  
    data=pd.merge(in1,in2, left_index=True, right_index=True)
    data = data.reset_index()  # make sure indexes pair with number of rows
    G = nx.Graph()
    for index, row in data.iterrows():
    	G.add_edges_from([(row['src_ref.value'], row['user_id']), (row['user_id'], row['dst_ref.value'])])
    
    

    
    #model = DeepWalk(G, walk_length=3, num_walks=10, workers=1)
    model = DeepWalk(G, walk_length, num_walks=1, workers=1)
    model.train(window_size=5, iter=3)
    embeddings = model.get_embeddings() 


    output=evaluate_embeddings(embeddings, data)
    out['index1'] = out.index
    output['index1']=output.index
    #in2['index1']=in2.index
    
    #changing out
    output['source']=output['src_ref.value']
    output['destination']=output['dst_ref.value']
    out['first_observed']=output['first_observed_x']
    out=pd.merge(out,output[['index1','source', 'destination', 'user_id', 'status']], how='inner', on =['index1'])
    #out=output
    out.to_parquet(OUTPUT_DATA_PATH, compression="gzip")

    
    
