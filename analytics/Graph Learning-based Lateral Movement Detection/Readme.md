# Lateral Movement Detection

## Goal

Implement a classifier to detect if an authentication request shows the attempt of an adversary for lateral movement or not.

## Application Scenario

Assume that there is some log about the authentication requests which contains the time of the requests and the user and source and destination hosts
involved in each authentication request. Security analysts can use this Kestrel analytics to analyze this information to see if the lateral movement has occurred.
  


## Arguments

This Kestrel analytics should be applied on a variable which includes STIX Cyber-Observable objects and two tables which are obtained after applying the ADDOBSID transformer on two variables which include the "user-account" and "network-traffic" objects. The first table includes identifiers of the users who have initiated the requests while the second table shows which host have been involved in each authentication request and the status of the authentication request. Initially, the property "status" of a "network-traffic" object is assigned to "unknown" or "benign". 


## Parameters

The Kestrel analytics has two input parameters. The first parameter is called "walkLength", which show the length of the random walks. The second parameter is the name of classifier, and can be set to "svm", "knn", "xgboost", "logisticRegression", and "randomforest".


## Usage

This Kestrel analytics can be built using the following command:
```
docker build -t kestrel-analytics-detect_lm .
```
In the following, we can show that how our Kestrel analytics can be applied when we have a table in a database in which the information of the authentication requests has been stored.
```
users=GET user-account FROM stixshifter://database WHERE [user-account:user_id != null]
connections=FIND network-traffic LINKED users
connections_obs=ADDOBSID(connections)
users_obs=ADDOBSID(users)
observations = GET observed-data FROM stixshifter://database WHERE [user-account:user_id != null]
APPLY docker://detect_lm ON observations, users_obs, connections_obs WITH walkLength=3, classifier=xgboost
```

##More Information

For more information about how to feed the data to the kestrel analytics, you can refer to my online article in the following link:
https://opencybersecurityalliance.org/kestrel-analytics-lateral-movement/ 

## Contributors:
Mahdi Rabbani and Leila Rashidi, Postdoctoral Fellows at the Canadian Institute for Cybersecurity
