# ATTRIBUTE Plot

## Goal
The purpose of this analytic is to plot attributes and return a SVG. The analytic requires the x and y parameters to be passed in, and then it attempts to find an appropriate data visualization.


## Usage: 
- Build the analytics container:
```
docker build -t kestrel-analytics-attrib-plot .
```

- Example command to trigger kestrel-analytics-attrib-plot analytic
```
nt = GET network-traffic FROM file://samplestix.json WHERE [ipv4-addr:value LIKE '127.0.0.1']
APPLY docker://attrib-plot ON foo WITH XPARAM=pid, YPARAM=number_observed
```

## Examples

Assume you have a variable `procs` with `process` entities.  You can see a distribution of count of process names via:
```
APPLY docker://attrib-plot ON procs with XPARAM=name
```
Note that we left out `YPARAM` here.

If you have `network-traffic` in a variable `conns`, you can see a scatterplot of `src_byte_count` versus `dst_byte_count`:
```
APPLY docker://attrib-plot ON conns with XPARAM=src_byte_count, YPARAM=dst_byte_count
```

Or you can get an idea of the distribution of ports as box plots:
```
APPLY docker://attrib-plot ON conns with XPARAM=src_port,dst_port
```
Note that we pass a list as `XPARAM` and don't use a `YPARAM`.
