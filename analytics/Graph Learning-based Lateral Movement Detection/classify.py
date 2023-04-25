from __future__ import print_function

from sklearn.metrics import classification_report
import numpy
import time
import datetime 

import pandas as pd


class Classifier(object):

    def __init__(self, embeddings, clf): 
        self.embeddings = embeddings
        self.clf = clf
        
    
    	
        
    def computeFeatureVector(self, data):
    	
        #ComputeFeatures
      
    	F_src = [numpy.asarray(self.embeddings[x]) for x in data['src_ref.value']] 
    	F_dst = [numpy.asarray(self.embeddings[x]) for x in data['dst_ref.value']]  
    	F_usr = [numpy.asarray(self.embeddings[x]) for x in data['user_id']] 
    	
    	#if (len(F_src)<1):
    	#	return None
    	features1=numpy.concatenate((F_src,F_dst,F_usr),axis=1)
    	#append!
    	
    	data2=data.apply(lambda x: time.mktime(datetime.datetime.strptime(x['first_observed_x'],"%Y-%m-%dT%H:%M:%S.%fZ").timetuple()), axis=1) 
    	
    	
    	
    	F_time = [numpy.asarray(x) for x in  data2] 
    	features=numpy.c_[features1,F_time]
    	
    	
    	
    	return features
    	
    	

    	   	
    	        
    def train(self, data): 
         
        featureVectores= self.computeFeatureVector(data)
        
        data['statusCode']=data.apply(lambda row: 0 if (row['status'] =='benign') else 1, axis=1)
        
        f=numpy.array(featureVectores,dtype=object)
        g=data['statusCode'].to_numpy().astype(int)
        
        self.clf.fit(f,g)
        #print("----This is Y after fit....")
        #print(numpy.array(Y).astype(int))
        
        
        
        
    def evaluate(self, data):
        featureVectores= self.computeFeatureVector(data)
        
       
        Y = self.clf.predict(numpy.array(featureVectores,dtype=object ))
        #Y is an array of lables
        return Y

   
        


    def train_evaluate(self, data):
        
	
        
        train_positive=data[data['status'].astype(str).str.match('benign')].copy()
        train_negative=data[data['status'].astype(str).str.match('malicious')].copy()
        self.train(pd.concat([train_positive, train_negative]))
        test=data[data['status'].astype(str).str.match('unknown')].copy()
        
        if (len(test.index)<1):
        	return None
        Y= self.evaluate(test)
        test['prediction'] = Y
        
        test ['status']=test.apply(lambda row: 'benign' if (row['prediction'] == 0) else 'malicious', axis=1)
        test.drop(['prediction'], axis=1)
        updatedData=pd.concat([train_positive[['first_observed_x','user_id','src_ref.value','dst_ref.value','status']], train_negative[['first_observed_x','user_id','src_ref.value','dst_ref.value','status']],test[['first_observed_x','user_id','src_ref.value','dst_ref.value','status']]], ignore_index=True)
        if (len(updatedData.index)<1):
        	return None
        
        return updatedData



