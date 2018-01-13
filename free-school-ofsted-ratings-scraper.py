#!/usr/bin/env python
# -*- coding: utf-8 -*-

import scraperwiki
import requests
import time
from datetime import date
from datetime import datetime
from collections import OrderedDict

import urllib
from bs4 import BeautifulSoup

#scraperwiki.sqlite.execute("drop table log")
#scraperwiki.sqlite.execute("drop table inspections")

Ofsted_url_stub = "http://www.ofsted.gov.uk/inspection-reports/find-inspection-report/provider/ELS/"
import_url="https://premium.scraperwiki.com/mse5vbk/i7mrbh7eb5ovppc/sql/?q=select%0D%0A%20%20%20%20URN%2C%0D%0A%20%20%20%20LAEstab%2C%0D%0A%20%20%20%20schooltype%2C%0D%0A%20%20%20%20schoolname%2C%0D%0A%20%20%20%20schoolname_with_note_symbol%2C%0D%0A%20%20%20%20phase%2C%0D%0A%20%20%20%20LA%2C%0D%0A%20%20%20%20open_date%2C%0D%0A%20%20%20%20inspection_rating%2C%0D%0A%20%20%20%20inspection_rating2%2C%0D%0A%20%20%20%20publication_date%2C%0D%0A%20%20%20%20publication_date_long%2C%0D%0A%20%20%20%20published_recent%2C%0D%0A%20%20%20%20inspection_date%2C%0D%0A%20%20%20%20inspection_date_long%2C%0D%0A%20%20%20%20URL%2C%0D%0A%20%20%20%20include%2C%0D%0A%20%20%20%20open_closed%2C%0D%0A%20%20%20%20notes%2C%0D%0A%20%20%20%20note_symbol%0D%0Afrom%20School_details%0D%0Aorder%20by%20urn"

json = requests.get(import_url, verify=False).json() #pulls in json and converts to json that can be used in python

get_pass="Pass"     #changed to fail if calling a page fails, or we get an error in working with data from a page
log=OrderedDict([
    ("Run_date","intentionally_blank"),
    ("Run_date_short","intentionally_blank"),
    ("Get_pass","intentionally_blank"),
    ("Yesterday_inspected_pass","intentionally_blank"),
    ("Yesterday_ratings_pass","intentionally_blank"),
    ("Spreadsheet_pass","intentionally_blank"),
    ("Saving_pass","intentionally_blank")
    ])

def ofsted_scraper(get_pass):
    for school in json:
        Ofsted_full_url=Ofsted_url_stub+school["URN"]
        school["URL"]=Ofsted_full_url
        try:
            html = requests.get(Ofsted_full_url)
            soup = BeautifulSoup(html.content, "html.parser")
            pgtitle = soup.find("title").get_text()
            if not pgtitle == "Ofsted | Page not found ":
                if not soup.find("span", "ins-rep-date") == None:
                    if school["open_closed"] == "Open" or school["open_closed"] == "Open, but proposed to close":     # checks open status of schools. Only open, pre-16 schools which have had a sec 5 inspection are included
                        school["include"]=True
                    else:
                        school["include"]=False
                    if not soup.find("span", "ins-judgement ins-judgement-1") == None:
                        school["inspection_rating"]= soup.find("span", "ins-judgement ins-judgement-1").get_text()
                        school["inspection_rating2"] = "1"
                    else:
                        if not soup.find("span", "ins-judgement ins-judgement-2") == None:
                            school["inspection_rating"]= soup.find("span", "ins-judgement ins-judgement-2").get_text()
                            school["inspection_rating2"] = "2"
                        else:
                            if not soup.find("span", "ins-judgement ins-judgement-4") == None:
                                school["inspection_rating"]= soup.find("span", "ins-judgement ins-judgement-4").get_text()
                                school["inspection_rating2"] = "4"
                            else:
                                if not soup.find("span", "ins-judgement ins-judgement-5") == None:      #weirdly, RI results have this span
                                    school["inspection_rating"]= "Requires improvement"                 #done as page has a capital I for 'improvement'...
                                    school["inspection_rating2"] = "3"
                                else:
                                        rating = "Error - no rating found"
                                        rating2= "n/a"
                    school["inspection_date"] = soup.find_all("span", "ins-rep-date")[0].get_text()
                    school["inspection_date_long"] = datetime.strptime(school["inspection_date"], "%d %b %Y").date()
                    school["publication_date"] = soup.find_all("span", "ins-rep-date")[1].get_text()
                    school["publication_date_long"]= datetime.strptime(school["publication_date"], "%d %b %Y").date()
                    published_days = date.today()-school["publication_date_long"]   #converts publication date string to a datetime object, then a date object and calculates difference from today's date
                    if published_days.days<=7:       #strips 'days' from published.days and saves the number of days if <= a week
                        school["published_recent"]= str(published_days.days)        #saved as a string so that we don't have mixed data types for this key, and get errors when saving in SqlAlchemy
                    else:
                        school["published_recent"]= "No"
                else:
                    school["include"]=False         #even schools that have had college/learning and skills inspections we don't want to include in our results
                    if soup.find(text=" College inspection report ") is not None:
                        school["inspection_rating"] = "College inspection report - findings not scraped"
                        school["inspection_rating2"] = "College inspection report - findings not scraped"
                        school["inspection_date"] = soup.find_all("td", class_="date")[0].get_text()
                        school["inspection_date_long"] = datetime.strptime(school["inspection_date"], "%d %b %Y").date()
                        school["publication_date"] = soup.find_all("td", class_="date")[1].get_text()
                        school["publication_date_long"]= datetime.strptime(school["publication_date"], "%d %b %Y").date()
                        published_days = date.today()-school["publication_date_long"]   #converts publication date string to a datetime object, then a date object and calculates difference from today's date
                        if published_days.days<=7:       #strips 'days' from published.days and saves the number of days if <= a week
                            school["published_recent"]= str(published_days.days)        #saved as a string so that we don't have mixed data types for this key, and get errors when saving in SqlAlchemy
                        else:
                            school["published_recent"]= "No"
                    elif soup.find(text=" Learning and skills inspection report ") is not None:
                        school["inspection_rating"] = "Learning and skills inspection - findings not scraped"
                        school["inspection_rating2"] = "Learning and skills inspection - findings not scraped"
                        school["inspection_date"] = soup.find_all("td", class_="date")[0].get_text()
                        school["inspection_date_long"] = datetime.strptime(school["inspection_date"], "%d %b %Y").date()
                        school["publication_date"] = soup.find_all("td", class_="date")[1].get_text()
                        school["publication_date_long"]= datetime.strptime(school["publication_date"], "%d %b %Y").date()
                        published_days = date.today()-school["publication_date_long"]   #converts publication date string to a datetime object, then a date object and calculates difference from today's date
                        if published_days.days<=7:       #strips 'days' from published.days and saves the number of days if <= a week
                            school["published_recent"]= str(published_days.days)        #saved as a string so that we don't have mixed data types for this key, and get errors when saving in SqlAlchemy
                        else:
                            school["published_recent"]= "No"
                    else:           #this scenario will occur where e.g. an academy conversion letter is posted on the Ofsted website, but no sec 5 or learning and skills inspection has been carried out yet
                        school["inspection_rating2"] = "n/a"
                        school["inspection_date"]= "n/a"
                        school["inspection_date_long"]= None
                        school["publication_date"]= "n/a"
                        school["publication_date_long"]= None
                        school["published_recent"]= "n/a"
                        if school["schooltype"]=="Free school":
                            school["inspection_rating"] = "No section 5 inspection"
                        elif school["schooltype"]== "Sponsored academy" or school["schooltype"]=="Converter academy":
                            school["inspection_rating"] = "No section 5 inspection as an academy"
            else:
                school["include"]=False
                school["inspection_rating"]="No section 5 inspection"
                school["inspection_rating2"]="n/a"
                school["inspection_date"]="n/a"
                school["inspection_date_long"]= None
                school["publication_date"]="n/a"
                school["publication_date_long"]= None
                school["published_recent"]="n/a"
        except:
            get_pass="Fail"         #fails if calling page fails, or some other error occurs when working with page data
    return get_pass

def validation_tests(get_pass):
    # need to implement tests to check:
        # 1. number of inspected schools (open + closed) is in line with yesterday
        # 2. ratings are in line with yesterday

    inspected_count=0
    1count=0
    2count=0
    3count=0
    4count=0
    1pct=0
    2pct=0
    3pct=0
    4pct=0

    for school in json:     #saves today's data, whether or not validation checks have passed. Records whether saving has been successful in saving_pass
        if school["inspection_rating2"] in ("1","2","3","4"):
            inspected_count+=1
        if school["inspection_rating2"]==1:
            1count+=1
        elif school["inspection_rating2"]==2:
            2count+=1
        elif school["inspection_rating2"]==3:
            3count+=1
        elif school["inspection_rating2"]==4:
            4count+=1

    1pct=1.0*1count/inspected_count
    2pct=1.0*2count/inspected_count
    3pct=1.0*3count/inspected_count
    4pct=1.0*4count/inspected_count

    try:
        if inspected_count>=scraperwiki.sqlite.execute("select count(1) from inspections q join (select urn, max(inspection_date_long) as max_date from inspections r group by urn) s on q.urn= s.urn and q.inspection_date_long = s.max_date where q.inspection_rating2 in ("1","2","3","4")")["data"])<0.1:
            then yesterday_inspected_pass="Pass"
    except:
        yesterday_inspected_pass="No data to compare against"

    try:
        if abs(1pct-scraperwiki.sqlite.execute("select count(1) from inspections q join (select urn, max(inspection_date_long) as max_date from inspections r group by urn) s on q.urn= s.urn and q.inspection_date_long = s.max_date where q.inspection_rating2=1")["data"])<0.1:
            then yesterday_ratings_pass=="Fail"
        elif abs(1pct-scraperwiki.sqlite.execute("select count(1) from inspections q join (select urn, max(inspection_date_long) as max_date from inspections r group by urn) s on q.urn= s.urn and q.inspection_date_long = s.max_date where q.inspection_rating2=2")["data"])<0.1:
            then yesterday_ratings_pass=="Fail"
        elif abs(1pct-scraperwiki.sqlite.execute("select count(1) from inspections q join (select urn, max(inspection_date_long) as max_date from inspections r group by urn) s on q.urn= s.urn and q.inspection_date_long = s.max_date where q.inspection_rating2=3")["data"])<0.1:
            then yesterday_ratings_pass=="Fail"
        elif abs(1pct-scraperwiki.sqlite.execute("select count(1) from inspections q join (select urn, max(inspection_date_long) as max_date from inspections r group by urn) s on q.urn= s.urn and q.inspection_date_long = s.max_date where q.inspection_rating2=4")["data"])<0.1:
            then yesterday_ratings_pass=="Fail"
    except:
        yesterday_ratings_pass="No data to compare against"

    if get_pass=="Fail" or yesterday_inspected_pass=="Fail" or yesterday_ratings_pass=="Fail":
        spreadsheet_pass="Fail"
    else:
        spreadsheet_pass="Pass"
    log["Run_date"]=datetime.now()
    log["Run_date_short"]=time.strftime("%d %B %Y")
    log["Get_pass"]=get_pass
    log["Yesterday_inspected_pass"]=yesterday_inspected_pass
    log["Yesterday_ratings_pass"]=yesterday_ratings_pass
    log["Spreadsheet_pass"]=spreadsheet_pass
    return spreadsheet_pass

def saving(spreadsheet_pass):
    saving_pass="Pass"        #true, as saving code sets this to false only if saving fails
    for school in json:     #saves today's data, whether or not validation checks have passed. Records whether saving has been successful in saving_pass
        urn=school["URN"]
        try:
            previous_inspection_date=scraperwiki.sqlite.execute("SELECT inspection_date FROM today_school_details WHERE URN=(?) ORDER BY inspection_date LIMIT 1", [urn])["data"][0][0]       # scraperwiki.sqlite.execute returns a dictionary containing an array of 'keys' and an array of 'data'. ["data"][0] returns a tuple with one element, therefore we want to select that element
            if school["inspection_date"]>previous_inspection_date:
                try:
                    scraperwiki.sql.save(["URN"], school, "inspections")
                except:
                    print "Error saving row: " + str(school)
                    saving_pass="Fail"
        except:                 # no previous inspection is recorded for this URN
            try:
                scraperwiki.sql.save(["URN"], school, "inspections")
            except:
                print "Error saving row: " + str(school)
                saving_pass="Fail"
    log["Saving_pass"]=saving_pass
    scraperwiki.sql.save(["Run_date"], log, "log")
    return

get_pass=ofsted_scraper(get_pass)   #we will use get_pass status in validation tests
spreadsheet_pass=validation_tests(get_pass)
saving(spreadsheet_pass)
