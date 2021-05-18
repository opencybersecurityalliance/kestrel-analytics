# Domain Name Lookup

## Goal
Implement a context enrichment function to lookup domain names for IP addresses.

## Application Scenario

When `network-traffic` entities are retrieved from data sources in Kestrel, the
analyst may want to get a more human perspective of the IPs, especially the
domain names. This analytics completes the context.

## Author

Douglas Schales (schales@us.ibm.com)

## Requirements

- Internet access

## Functionality Description

This analytic adds two columns based on the destination IP address

- `x_domain_name`: The DNS name that the IP address inverse resolves to. Note
  that this may not, and frequently does not, correspond to the FQDN that was
  queried and resolved to the IP. It also frequently will not resolve.

- `x_domain_organization`: The organization, from `whois`, associated with the
  IP network containing this IP address.

## Building The Analytics

Build it in a terminal:
```
$ docker build -t kestrel-analytics-domainnamelookup .
```

Then use it in Kestrel:
```
# varX is network-traffic from previous commands
APPLY docker://domainnamelookup ON varX
# show the new fields
DISP varX ATTR dst_ref.value, dst_port, x_domain_name, x_domain_organization
```
