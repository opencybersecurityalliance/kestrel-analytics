# log4shell deobfuscation and detection

This is a quick attempt at detecting exploits of the log4shell
vulnerability with Kestrel.

The vulnerability appears to involve "property substitution" (see
https://logging.apache.org/log4j/2.x/manual/configuration.html#PropertySubstitution),
so this analytic includes a small "pseudo-parser" for log4j property
substitutions.

## Usage

After gathering data from your stix-shifter data sources:
```
urls = GET url FROM <datasource config> WHERE [url:value LIKE '%${%']
```

Or:
```
conns = GET network-traffic
        FROM <datasource config>
        WHERE [network-traffic:extensions.'http-request-ext'.request_header.'User-Agent' LIKE '%${%']
```

Apply this analytic; any exploit attempts found will be deobfuscated
and added to a new `exploit` column: ``` APPLY log4shell ON urls ```

You can then "filter" to find them:
```
attacks = GET url FROM urls WHERE [url:exploit LIKE '%']
```

The `LIKE '%'` comparison will match any non-NULL value; only entries
where an exploit is found will have anything in that column.

## Search raw payloads

If your datasource returns `artifact` SCOs, you can try applying the
analytic against those.  `artifact` SCOs have a `payload_bin` property
that can contain a (base64-encoded) "raw payload," e.g. the log
message that the stix-shifter connector used to create the
`observed-data` SDO.

Determine a reasonable STIX pattern and `GET` some payloads over some
period of time, say the last 24 hours:

```
payloads = GET artifact
           FROM stixshifter://...
           WHERE [ipv4-addr:value LIKE '%'] START t'2021-12-14T20:43:10.000Z' STOP t'2021-12-15T20:43:10.000Z'
```

Run the analytic and then filter for records with an apparent exploit attempt:

```
APPLY log4shell ON payloads
attempts = GET artifact FROM payloads WHERE [artifact:exploit LIKE '%']
DISP attempts ATTR id, first_observed, exploit
```
