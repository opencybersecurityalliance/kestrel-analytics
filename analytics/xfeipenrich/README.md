# XFE Enrich

## Goal

The purpose of this analytic is to leverage X-Force Exchange API
(https://api.xforce.ibmcloud.com/doc/) for threat intel
enrichment. Data returned by XFE will be prefixed with 'x_xfe_'.

Supported observable types:
- IP addresses (`ipv4-addr` and `ipv6-addr`)
  - 'cats', 'score', 'geo' (country), 'company' (from ASN)
- Domain names (`domain-name`) and URLs (`url`)
  - 'cats', 'score'
- Files (`file`, using `hashes.MD5`, `hashes.'SHA-1', or `hashes.'SHA-256'`)
  - 'risk', 'family'

## Usage

- Configuration: set XFE_CRED environment variable to "APIKEY:APIPASSWORD"
  - 'APIKEY' and 'APIPASSWORD' as obtained from https://exchange.xforce.ibmcloud.com/settings/api

### Via docker

- Build the analytics container:
```
docker build -t kestrel-analytics-xfe-enrich .
```

- Commands to trigger xfe-enrich analytics
```
domains = NEW domain-name [{"value":"opencybersecurityalliance.org"}]
APPLY docker://xfe-enrich ON domains
DISP domain
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
ips = NEW ipv4-addr [{"value":"103.115.252.18"}, {"value":"24.116.105.234"}]
APPLY python://xfe-enrich on ips
DISP ips
```
