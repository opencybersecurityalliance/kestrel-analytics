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
APPLY docker://sklearn-cluster ON conns WITH n=2, columns=src_byte_count,dst_byte_count
```

## Parameters

- `n`: the number of clusters to form (`n_clusters`)
- `columns`: the Kestrel attributes (columns) to use for clustering.  Only these columns will be seen by the clustering algorithm.