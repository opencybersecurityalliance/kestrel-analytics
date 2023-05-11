# Lateral Movement Detection

## Goal

Implement a classifier to detect if an authentication request shows the attempt of an adversary for lateral movement or not.

## Application Scenario

Assume that there is some log about the authentication requests which contains the time of the requests and the user and source and destination hosts
involved in each authentication request. Security analysts can use this Kestrel analytics to analyze this information to see if the lateral movement has occurred.
  

## Basic Idea

Three entities are involved in each authentication request: a user, a source host, from which the request is made, and a destination host, that the user has requested to access it.
Note that the source and destination can be same or different. Users, sources, and destinations can be clustered based on how they are represented by the set of the training authentication
requests. For example, a feature to represent a user can be the number of distinct sources from where he/she has sent the benign authentication requests or a source host can be represented by
a feature which equals the percentage of their authentication request which are made on a specific weekday. Thus, an authentication request can be modeled as a triplet of the clusters
of users, sources, and destinations to which the user, source, and destination involved in the request belongs, respectively. If the triplet representing a test request is the same as a
triplet representing a benign/train request, it can be considered as "benign"; otherwise, it can be labeled as "malicious".

## Arguments

This Kestrel analytics should be applied on a variable which includes STIX Cyber-Observable objects and two tables which are obtained after applying the OBSERVED transformer on two variables which include the "user-account" and "network-traffic" objects. The first table includes identifiers of the users who have initiated the requests while the second table includess which host have been involved in each authentication request and the status of the authentication request. Initially, the property "status" of a "network-traffic" object is assigned to "unknown" or "benign". 


## Parameters

The Kestrel analytics gets the number of clusters into which the users, sources, and destinations should be divided as the input parameters. Thus, three parameters should be passed to
the container. The first parameter represents the number of clusters of users, and the second and third parameters represent the number of clusters of sources and destinations, respectively.


## Usage

This Kestrel analytics can be built using the following command:
```
docker build -t kestrel-analytics-detect_lm .
```
In the following, we can show that how our Kestrel analytics can be applied via Docker interface. Note that you cannot use this Kestrel analytics via a Python analytics interface. 
```
users=GET user-account FROM stixshifter://database WHERE [user-account:user_id != null]
connections=FIND network-traffic LINKED users
connections_obs=OBSERVED(connections)
users_obs=OBSERVED(users)
observations = GET observed-data FROM stixshifter://database WHERE [user-account:user_id != null]
APPLY docker://detect_lm ON observations, users_obs, connections_obs WITH ku=60, ks=60, kd=60
```

##More Information

For more information regarding this kestrel analytics including using it, you can refer to my online article in the following link:
https://opencybersecurityalliance.org/kestrel-analytics-lateral-movement/ 
