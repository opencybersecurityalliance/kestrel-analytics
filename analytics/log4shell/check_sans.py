'''Test script for running ISC SANS honeypot data through unlog4shell.

You can obtain JSON data from their API as described here:
https://isc.sans.edu/forums/diary/Log4j+Log4Shell+Followup+What+we+see+and+how+to+defend+and+how+to+access+our+data/28122/

Save the API JSON response to a file, then pass it to this test script.

My apologies for the quick-and-dirty nature of this junk.
'''

import json
import sys

from unlog4shell import check_url, check_string

with open(sys.argv[1], 'r') as fp:
    data = json.load(fp)

matched_url = 0
matched_ua = 0
matched = 0
total = 0
for record in data:
    total += 1
    url_result = check_url(record['url'])
    ua_result = check_string(record['user_agent'])
    if url_result:
        matched_url += 1
    if ua_result:
        matched_ua += 1
    if not url_result and not ua_result:
        print('FAIL', json.dumps(record))
    else:
        matched += 1

print('matched', matched, 'out of', total)
print(matched_url, 'URLs')
print(matched_ua, 'User-Agents')
