# -*- coding: utf-8 -*-

import json, re
from pyproj import Transformer
from datetime import date

files   = ['anlagenbaeume.json', 'strassenbaeume.json']
outFile = 'occurrence.tsv'

current_year = date.today().year
# coordinate transformer
transformer = Transformer.from_crs("EPSG:25833", "EPSG:4326", always_xy=True)

def clean(x):
    return re.sub('[\n\r\t]',' ', x)

def writeRec(out, rec):
    props   = rec["properties"]
    sn      = props["art_bot"]
    if not sn or sn=='Unbekannt' or sn=='None':
        return
    ID = rec["id"]
    yearStr = props["pflanzjahr"]
    year = int(yearStr) if yearStr else 0

    vcoord = rec["geometry"]["coordinates"]
    vlon = vcoord[0]
    vlat = vcoord[1] 

    # ref system http://www.opengis.net/def/crs/EPSG/0/25833
    coord=transformer.transform(vlon, vlat)
    lon = coord[0]
    lat = coord[1]
    dp = "{\"age\":%s, \"trunk diameter\":%s, \"height\":%s, \"planting year\":%s}" % (props["standalter"], props["stammumfg"], props["baumhoehe"], props["pflanzjahr"])
    data = "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s" % (ID, props["kennzeich"], sn, props["art_dtsch"], props["gattung"], clean(props["bezirk"]), clean(props["namenr"]), lat, lon, vlat, vlon)
    # record for this year
    out.write("%s\t%s\t%s\t%s\t%s\n" % (ID, data, current_year, "", dp))
    # do another record for the year it was planted. The oldest tree in Berlin is "Die alte Marie", a 860 year old oak
    if year > 1000 and year < current_year:
        out.write("%s.planted\t%s\t%s\t%s\t%s\n" % (ID, data, year, "Year the tree was planted", ""))
    elif year < 2025 and year > 0:
        print("Ignore planting year %s" % (year))



with open(outFile, 'w', newline='') as out:
    out.write("occurrenceID\torganismID\tcatalogNumber\tscientificName\tvernacularName\tgenus\tmunicipality\tlocality\tdecimalLatitude\tdecimalLongitude\tverbatimLatitude\tverbatimLongitude\tyear\toccurrenceRemarks\tdynamicProperties\n")
    for fn in files:
        print("Process file "+fn)
        with open(fn) as f:
            data = json.load(f)
            for rec in data["features"]:
                writeRec(out, rec)
print("Done.")