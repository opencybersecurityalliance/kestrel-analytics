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
where an exploit as found will have anything in that column.