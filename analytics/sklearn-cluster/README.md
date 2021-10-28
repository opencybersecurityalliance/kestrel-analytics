# scikit-learn K-Means Clusting

Uses https://scikit-learn.org/stable/modules/generated/sklearn.cluster.KMeans.html

## Usage

Build it:
```
docker build -t kestrel-analytics-sklearn-cluster .
```

Example usage in Kestrel:
```
conns = GET network-traffic FROM file://samplestix.json where [network-traffic:dst_port > 0]
APPLY docker://sklearn-cluster ON conns WITH method=kmeans, n_clusters=3, columns=src_byte_count,dst_byte_count
```

## Parameters

- `method`: the clustering algorithm. Clustering algorithms such as `kmeans`, and `dbscan` are supported. 
- Please refer to the following document for the parameters when you specify a algorithm. https://scikit-learn.org/stable/modules/clustering.html
- `columns`: the Kestrel attributes (columns) to use for clustering.  Only these columns will be seen by the clustering algorithm.