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
    138259:{"annotation":"Hartsbrook E-ACT, pre-closure","symbol":"*", "note":"This school reopened as Brook House Primary School (URN: 141209) after being taken over by a new sponsor."},
    141209:{"annotation":"Brook House Primary School (Hartsbrook E-ACT, post-closure)","symbol":"*", "note":"This school was previously known as Hartsbrook E-Act Free School. It changed name, and was given a new URN, when it was taken over by a new sponsor."},
    138780:{"annotation":"St Michael's Secondary School","symbol":"**", "note":"St Michael's Secondary School ceased to be a standalone school in September 2016, merging with an existing academy, Camborne Science and International Academy."},
    138561:{"annotation":"Harpenden Free School, pre-closure","symbol":"***", "note":"This school joined an academy trust in September 2016, and is recorded by the DfE as a technical closure. It now operates under URN 143648."},
    143648:{"annotation":"Harpenden Free School, post-closure","symbol":"***", "note":"Harpenden Free School previously operated under URN 138561."},
    139786:{"annotation":"Royal Greenwich Trust School Academy","symbol":"****", "note":"Royal Greenwich Trust School Academy closed in August 2016 and became Royal Greenwich Trust School (URN: 143927)."},
    143927:{"annotation":"Royal Greenwich Trust School","symbol":"****", "note":"Royal Greenwich Trust School previously operated under URN 139786."}
    }

school_details={
    "URN":None,
    "LAEstab":None,
    "school_name":None,
    "note_symbol":None,
    "notes":None,
    "school_name_with_note_symbol":None,
    "LA":None,
    "school_type":None,
    "phase":None,
    "open_closed":None,
    "open_date":None,
    "close_date":None,
    "inspection_rating":None,
    "inspection_rating_text":None,
    "inspection_date":None,
    "inspection_date_long":None,
    "publication_date":None,
    "publication_date_long":None,
    "URL":None
}

url1="https://github.com/philipnye/free-school-ofsted-ratings-back-end/tree/master/data"
url2= "https://raw.githubusercontent.com/philipnye/free-school-ofsted-ratings-back-end/master/data/"

def compiler():
    html=requests.get(url1).text
    soup=BeautifulSoup(html, 'html.parser')
    for a in soup.find_all('a'):
        if str(a.get('title')).endswith('csv'):     # tag.get('attr') in Beautiful soup works as get works with a Python dictionary, returning None where attr is undefined.
            filename=str(a.get('title'))
            url3=url2+filename        # expectation is that there is only one data file
    csvfile=requests.get(url3)
    csvfile=csvfile.iter_lines()      # is required in order for csv file to be read correctly, without errors caused by new-line characters
    reader=csv.DictReader(csvfile)
    for row in reader:
        if row["EstablishmentTypeGroup (name)"].lower()==("Free Schools").lower():
            URN=int(row["URN"])
            school_details["URN"]=URN
            school_details["LAEstab"]=int(row["LA (code)"]+row["EstablishmentNumber"])
            school_details["school_name"]=row["EstablishmentName"]
            try:        #handles the fact that notes[URN]["symbol"] will only exist for a limited number of URNs
                school_details["school_name_with_note_symbol"]=school_details["school_name"]+notes[URN]["symbol"]
                school_details["notes"]=notes[URN]["note"]
                school_details["note_symbol"]=notes[URN]["symbol"]
            except:
                school_details["school_name_with_note_symbol"]=school_details["school_name"]
                school_details["notes"]=""
                school_details["note_symbol"]=""
            school_details["school_type"]=row["TypeOfEstablishment (name)"]
            school_details["LA"]=row["LA (name)"]
            school_details["open_closed"]=row["EstablishmentStatus (name)"]
            if not row["OpenDate"]=='':     # cheaper than using a try..except statement in this instance
                school_details["open_date"]=datetime.strptime(row["OpenDate"], '%d-%m-%Y').date()       # can subsequently use school_details["opendate"].month and school_details["opendate"].year to identify elements of the date
            if not row["CloseDate"]=='':     # cheaper than using a try..except statement in this instance
                school_details["close_date"]=datetime.strptime(row["CloseDate"], '%d-%m-%Y').date()       # can subsequently use school_details["opendate"].month and school_details["opendate"].year to identify elements of the date
            if row["TypeOfEstablishment (name)"].lower()==("Free Schools alternative provision").lower():
                school_details["phase"]="Alternative provision"
            elif row["TypeOfEstablishment (name)"].lower()==("Free Schools Special").lower():
                school_details["phase"]="Special"
            elif row["PhaseOfEducation (name)"].lower()==("16 Plus").lower():
                school_details["phase"]="16-19"
            elif row["PhaseOfEducation (name)"].lower()==("All Through").lower():
                school_details["phase"]="All-through"
            else:
                school_details["phase"]=row["PhaseOfEducation (name)"]
            scraperwiki.sql.save(["URN"], school_details, "School_details")
            print school_details
    return

compiler()
