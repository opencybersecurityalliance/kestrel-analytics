# XFE Enrich

## Goal

The purpose of this analytic is to leverage X-Force exchange API for threat intel enrichment. The 
following field from XFE will be keep if they exist: 'cats', 'score'.

- IP addresses are enriched.
- TODO: Enrich Domains, hashes and urls.

## Usage

- Build the analytics container:

```
docker build -t kestrel-analytics-xfe_enrich .
```

- Comment to trigger xfe_enrich analytics

```
nt = GET network-traffic FROM file://samplestix.json where [ipv4-addr:value LIKE '127.0.0.1']
APPLY docker://xfe_enrich ON foo WITH XFECRED=APIKEY:APIPASSWORD
DISP nt
```

- Alternatively use Python interface
```
ips = new ipv4-addr [{"value":"103.115.252.18"}, {"value":"24.116.105.234"}]
APPLY python://xfeipenrich on ips WITH XFE_CRED="APIKEY:APIPASSWORD"
DISP ips
```
- 'APIKEY' and 'APIPASSWORD' as obtained from https://exchange.xforce.ibmcloud.com/settings/api
