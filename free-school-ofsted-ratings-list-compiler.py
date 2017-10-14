#!/usr/bin/env python
# -*- coding: utf-8 -*-

import scraperwiki
import csv
from datetime import datetime
import calendar
import urllib
import requests
from bs4 import BeautifulSoup

scraperwiki.sqlite.execute("drop table School_details")

notes={
    "138259":{"annotation":"Hartsbrook E-ACT, pre-closure","symbol":"*", "note":"This school reopened as Brook House Primary School (URN: 141209) after being taken over by a new sponsor."},
    "141209":{"annotation":"Brook House Primary School (Hartsbrook E-ACT, post-closure)","symbol":"*", "note":"This school was previously known as Hartsbrook E-Act Free School. It changed name, and was given a new URN, when it was taken over by a new sponsor."},
    "138780":{"annotation":"St Michael's Secondary School","symbol":"**", "note":"St Michael's Secondary School ceased to be a standalone school in September 2016, merging with an existing academy, Camborne Science and International Academy."},
    "143648":{"annotation":"Harpenden Free School","symbol":"***", "note":"***Harpenden Free School previously operated under URN 138561."}
    }

schooldetails={
    "URN":"Not yet scraped",
    "schoolname":"Not yet scraped",
    "schoolname_with_note_symbol":"Not yet scraped",
    "schooltype":"Free school",
    "open_date":"Not yet scraped",
    "LA":"Not yet scraped",
    "phase":"Not yet scraped",
    "inspection_rating":"Not yet scraped",
    "inspection_rating2":"Not yet scraped",
    "inspection_date":"Not yet scraped",
    "inspection_date_long":"Not yet scraped",
    "publication_date":"Not yet scraped",
    "publication_date_long":"Not yet scraped",
    "published_recent":"Not yet scraped",
    "URL":"Not yet scraped",
    "open_closed":"Not yet scraped",
    "include":"Not yet scraped",
    "notes":"Not yet scraped",
    "note_symbol":"Not yet scraped"
}

def compiler():
    csvfile = requests.get("https://raw.githubusercontent.com/philipnye/free-school-ofsted-ratings-back-end/master/data/edubasealldata20171007.csv")
    csvfile = csvfile.iter_lines()      # is required in order for csv file to be read correctly, without errors caused by new-line characters
    reader = csv.DictReader(csvfile)
    for row in reader:
        if row["EstablishmentTypeGroup (name)"].lower()==("Free Schools").lower():
            if not (row["TypeOfEstablishment (name)"].lower()==("University technical college").lower() or row["TypeOfEstablishment (name)"].lower()==("Studio schools").lower()):
                URN = row["URN"]
                schooldetails["URN"]=URN
                schooldetails["schoolname"] = row["EstablishmentName"]
                try:        #handles the fact that notes[URN]["symbol"] will only exist for a limited number of URNs            
                    schooldetails["schoolname_with_note_symbol"] = schooldetails["schoolname"]+notes[URN]["symbol"]
                    schooldetails["notes"]=notes[URN]["note"]
                    schooldetails["note_symbol"]=notes[URN]["symbol"]
                except:
                    schooldetails["schoolname_with_note_symbol"] = schooldetails["schoolname"]
                    schooldetails["notes"]=""
                    schooldetails["note_symbol"]=""
                if not row["OpenDate"]=='':     # cheaper than using a try..except statement in this instance. No else statement required to save missing open_date values (though in this case missing values wouldn't be expected)
                    schooldetails["open_date"] = datetime.strptime(row["OpenDate"], '%d-%m-%Y').date()       # can subsequently use schooldetails["opendate"].month and schooldetails["opendate"].year to identify elements of the date
                schooldetails["LA"] = row["LA (name)"]
                schooldetails["open_closed"] = row["EstablishmentStatus (name)"]
                if row["TypeOfEstablishment (name)"].lower()==("Free Schools alternative provision").lower():
                    schooldetails["phase"] = "Alternative provision"
                elif row["TypeOfEstablishment (name)"].lower()==("Free Schools Special").lower():
                    schooldetails["phase"] = "Special"
                else:
                    if row["PhaseOfEducation (name)"].lower()==("16 Plus").lower():
                        schooldetails["phase"] = "16-19"
                    elif row["PhaseOfEducation (name)"].lower()==("All Through").lower():
                        schooldetails["phase"] = "All-through"
                    else:
                        schooldetails["phase"] = row["PhaseOfEducation (name)"]
                # print schooldetails
                if not schooldetails["URN"]=="138561":                # this is old Harpenden Free School, which we don't want to show as a closed school as there wasn't even a change in sponsor
                    scraperwiki.sql.save(["URN"], schooldetails, "School_details")
    return schooldetails

compiler()