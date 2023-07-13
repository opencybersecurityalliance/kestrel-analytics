# Geovisualization

This analytics accepts any entities that have latitude and longitude
as attributes and creates an interactive map with those entities
plotted as markers.

## Parameters:

- `LAT`: the attribute name that holds the latitude
- `LON`: the attribute name that holds the longitude
- `LABELS`: the attribute names to put into the map marker tooltips. Use a comma-separated list in quotes for more than one.

## Usage (via Python):

- Add something this to your ~/.config/kestrel/pythonanalytics.yaml:
```
    geoviz:
        module: /home/you/github/kestrel-analytics/analytics/geoviz/geoviz.py
        func: analytics
```

- Example command:
```
events = GET x-oca-event FROM ibm_verify
         WHERE outcome = 'failure'
         LAST 7 DAYS
APPLY python://geoviz ON events WITH LAT=x_location_lat, LON=x_location_lon, LABELS="action,outcome"
```

Note that `x_location_lat` and `x_location_lon` are custom attributes
returned by the `ibm_security_verify` stix-shifter connector module.
Other modules might use different attribute names, if they return lat
and long at all.

## Credits

Based on code written by Ritesh Kumar, IBM.