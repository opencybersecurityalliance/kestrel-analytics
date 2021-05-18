# ATTRIBUTE Plot

## Goal
The purpose of this analytic is to plot attributes and return a SVG. The analytic requires the x and y parameters to be passed to the analytic.


## Usage: 
- Build the analytics container:
```
docker build -t kestrel-attrib-plot .
```

- Command to trigger kestrel-attrib-plot analytic
```
nt = get network-traffic from file://samplestix.json where [ipv4-addr:value LIKE '127.0.0.1']
apply docker://attrib-plot ON foo with XPARAM=pid, YPARAM=number_observed
disp nt
```
  
