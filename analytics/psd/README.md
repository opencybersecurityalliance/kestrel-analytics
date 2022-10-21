# PowerShell Deobfuscator

## Goal

The purpose of this analytic is to assist threat hunters in analyzing
Microsoft PowerShell.  PowerShell is often used in "living off the
land"-style attacks due to its extensive capabilities and ubiquity (on
MS platforms).  To evade detection, the attacker's PowerShell code is
often obfuscated.  This module attempts to deobfuscate.

This code is currently very rudimentary.  It will handle base64
encoding, as well as attempting to normalize case.  It then attempts
to "pretty print" (i.e. format) the PowerShell code in the HTML
output.

This code was developed by Paul Coccoli and Stephen White (IBM
Security) in a few hours during a HackDay.

## Usage (via Docker):

- Build the analytics container:
```
docker build -t kestrel-analytics-psd .
```

- Example command to trigger kestrel-analytics-psd:
```
procs = GET process FROM file:///data/stix_bundle.json WHERE [process:name = 'powershell.exe']
APPLY docker://psd ON procs
```

## Usage (via Python):

- Add something this to your ~/.config/kestrel/pythonanalytics.yaml:
```
    psd:
        module: /home/you/github/kestrel-analytics/analytics/psd/analytics.py
        func: analytics
```

- Example command to trigger kestrel-analytics-psd:
```
procs = GET process FROM file:///data/stix_bundle.json WHERE [process:name = 'powershell.exe']
APPLY python://psd ON procs
```

## Example Output

```
Row 1: process--62688fb6-3dbf-424b-99ac-fe95bebd5d8b
<hr/>
<pre>
if ($PSVERSIONTABLE.psversion.major -ge 3) {
    $ACE6 = [ref].assembly.gettype('System.Management.Automation.Utils').getfield('cachedGroupPolicySettings', 'NonPublic,Static');
    if ($ACE6) {
    ...
```

In a jupyter notebook, the above output would be rendered as the cell output.
