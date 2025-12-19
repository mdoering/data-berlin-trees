# -*- coding: utf-8 -*-

import csv, re, json
from pyproj import CRS, Transformer

files   = ['anlagenbaeume.json', 'strassenbaeume.json']
outFile = 'occurrences.csv'
crs = CRS.from_epsg(25833)
wgs84 = CRS.from_epsg(4326)
transformer = Transformer.from_crs("EPSG:25833", "EPSG:4326", always_xy=True)

def writeRec(out, rec):
    ID = rec["id"]

    props=rec["properties"]
    vcoord = rec["geometry"]["coordinates"]
    vlon = vcoord[0]
    vlat = vcoord[1] 

    # ref system http://www.opengis.net/def/crs/EPSG/0/25833
    coord=transformer.transform(vlon, vlat)
    lon = coord[0]
    lat = coord[1]
    dp = "{\"age\":%s, \"trunk diameter\":%s, \"height\":%s, \"planting year\":%s}" % (props["standalter"], props["stammumfg"], props["baumhoehe"], props["pflanzjahr"])
    out.write("\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\"\n" % (ID, props["art_bot"], props["kennzeich"], props["art_dtsch"], props["gattung"], props["bezirk"], props["namenr"], lat, lon, vlat, vlon, dp.replace('"', '\\"')))



with open(outFile, 'w', newline='') as out:
    out.write("occurrenceID,scientificName,vernacularName,genus,municipality,locality,decimalLatitude,decimalLongitude,verbatimLatitude,verbatimLongitude,dynamicProperties\n")
    for fn in files:
        print("Process file "+fn)
        with open(fn) as f:
            data = json.load(f)
            for rec in data["features"]:
                writeRec(out, rec)
print("Done.")