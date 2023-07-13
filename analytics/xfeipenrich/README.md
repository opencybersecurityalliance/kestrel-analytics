# XFE Enrich

## Goal

The purpose of this analytic is to leverage X-Force Exchange API
(https://api.xforce.ibmcloud.com/doc/) for threat intel
enrichment. The following fields from XFE will be kept if they exist:
'cats', 'score', 'geo'.

- IP addresses are enriched.
- TODO: Enrich Domains, hashes and urls.

## Usage

- Configuration: set XFE_CRED environment variable to "APIKEY:APIPASSWORD"
  - 'APIKEY' and 'APIPASSWORD' as obtained from https://exchange.xforce.ibmcloud.com/settings/api

### Via docker

- Build the analytics container:
```
docker build -t kestrel-analytics-xfe_enrich .
```

- Commands to trigger xfe_enrich analytics
```
nt = GET network-traffic FROM file://samplestix.json where [ipv4-addr:value LIKE '127.0.0.1']
APPLY docker://xfe_enrich ON foo
DISP nt
```

### Via Python

- Add something this to your ~/.config/kestrel/pythonanalytics.yaml:
```
    xfe-enrich:
        module: /home/you/github/kestrel-analytics/analytics/xfeipenrich/analytics.py
        func: analytics
```

- `APPLY` on a var of type `ipv4-addr`:
```
ips = new ipv4-addr [{"value":"103.115.252.18"}, {"value":"24.116.105.234"}]
APPLY python://xfe-enrich on ips
DISP ips
```
