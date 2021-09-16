# Pin IP Address on A Map

This is a visualization analytics.

This analytics retrieves all IP addresses in `network-traffic` or
`ipv4-addr` entities, check their geolocation, and then pin the geolocation
on a map to return.

## Requirement

Get your copy of `GeoLite2-City.mmdb` from
[MAXMIND](https://dev.maxmind.com/geoip/geoip2/geolite2/). Put it in this
directory.

## Building The Analytics

Build it in a terminal:
```
$ docker build -t kestrel-analytics-pinip .
```

Then use it in Kestrel:
```
# varX is network-traffic from previous commands
# this command should return an interactive map with IPs pinned on the map
APPLY docker://pinip ON varX
```
