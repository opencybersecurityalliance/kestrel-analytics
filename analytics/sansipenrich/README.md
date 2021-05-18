# SANS IP Enrich

## Goal

The purpose of this analytic is to leverage SANS API for IP enrichment. The
following field from SANS will be keep if they exist: 'attacks', 'ascountry',
'asname', 'threatfeeds', 'firstseen", 'lastseen'.

- IP addresses `src_ref.value`, `dst_ref.value` of network-traffic in STIX will
  be enriched.

## Usage

- Build the analytics container:

```
docker build -t kestrel-analytics-sans_ip_enrich .
```

- Comment to trigger sans_ip_enrich analytics

```
nt = GET network-traffic FROM file://samplestix.json where [ipv4-addr:value LIKE '127.0.0.1']
APPLY docker://sans_ip_enrich ON foo WITH SANSCRED=your@email.com
DISP nt
```

- 'your@email.com' is the email that you register for using SANS API.
