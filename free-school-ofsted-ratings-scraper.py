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

ofsted_url_stub="http://www.ofsted.gov.uk/inspection-reports/find-inspection-report/provider/ELS/"
import_url="https://premium.scraperwiki.com/jp7l75x/h3ylw4drepnmbch/sql/?q=--%20INPUT%20DATA%20FOR%20SCRAPER%0D%0Aselect%0D%0A%20%20%20%20URN%2C%0D%0A%20%20%20%20LAEstab%2C%0D%0A%20%20%20%20school_name%2C%0D%0A%20%20%20%20note_symbol%2C%0D%0A%20%20%20%20notes%2C%0D%0A%20%20%20%20school_name_with_note_symbol%2C%0D%0A%20%20%20%20LA%2C%0D%0A%20%20%20%20school_type%2C%0D%0A%20%20%20%20phase%2C%0D%0A%20%20%20%20open_closed%2C%0D%0A%20%20%20%20open_date%2C%0D%0A%20%20%20%20close_date%2C%0D%0A%20%20%20%20inspection_rating%2C%0D%0A%20%20%20%20inspection_rating_text%2C%0D%0A%20%20%20%20publication_date%2C%0D%0A%20%20%20%20publication_date_long%2C%0D%0A%20%20%20%20inspection_date%2C%0D%0A%20%20%20%20inspection_date_long%2C%0D%0A%20%20%20%20URL%0D%0Afrom%20School_details%0D%0Awhere%0D%0A%20%20%20%20school_type%20in%20(%27Free%20schools%27%2C%27Free%20schools%20alternative%20provision%27%2C%27Free%20schools%20special%27%2C%27Free%20schools%2016%20to%2019%27)"
# ^^ compiler refactor output

json=requests.get(import_url, verify=False).json()        # pulls in json and converts to json that can be used in python

log=OrderedDict([
    ("run_date",None),
    ("run_date_short",None),
    ("get_pass",None),
    ("yesterday_inspected_pass",None),
    ("yesterday_ratings_pass",None),
    ("saving_pass",None)
    ])

error_log=OrderedDict([
    ("run_date",None),
    ("run_date_short",None),
    ("error_no",None),
    ("error",None)
    ])

def ofsted_scraper():
    get_pass=1     # changed to fail if calling a page fails, or we get an error in working with data from a page
    for school in json:
        ofsted_full_url=ofsted_url_stub+str(school["URN"])
        school["URL"]=ofsted_full_url
        try:
            html=requests.get(ofsted_full_url)
            soup=BeautifulSoup(html.content, "html.parser")
            pgtitle=soup.find("title").get_text()
            if not pgtitle=="Ofsted | Page not found ":
                if soup.find("span", "ins-rep-date")!=None:
                    if soup.find("span", "ins-judgement ins-judgement-1")!=None:
                        school["inspection_rating_text"]= soup.find("span", "ins-judgement ins-judgement-1").get_text()
                        school["inspection_rating"]=1
                    elif soup.find("span", "ins-judgement ins-judgement-2")!=None:
                        school["inspection_rating_text"]= soup.find("span", "ins-judgement ins-judgement-2").get_text()
                        school["inspection_rating"]=2
                    elif soup.find("span", "ins-judgement ins-judgement-5")!=None:      # RI results have this span
                        school["inspection_rating_text"]= "Requires improvement"     # done as page styles it as 'Requires Improvement'
                        school["inspection_rating"]=3
                    elif soup.find("span", "ins-judgement ins-judgement-4")!=None:
                        school["inspection_rating_text"]= soup.find("span", "ins-judgement ins-judgement-4").get_text()
                        school["inspection_rating"]=4
                    else:
                        rating="Error - no rating found"
                        rating2=None
                    school["inspection_date"]=soup.find_all("span", "ins-rep-date")[0].get_text()
                    school["inspection_date_long"]=datetime.strptime(school["inspection_date"], "%d %b %Y").date()
                    school["publication_date"]=soup.find_all("span", "ins-rep-date")[1].get_text()
                    school["publication_date_long"]= datetime.strptime(school["publication_date"], "%d %b %Y").date()
                    published_days=date.today()-school["publication_date_long"]       # converts publication date string to a datetime object, then a date object and calculates difference from today's date
                else:
                    school["include"]=False     # even schools that have had college/learning and skills inspections we don't want to include in our results
                    if soup.find(text=" College inspection report ") is not None:
                        school["inspection_rating_text"]="College inspection report - findings not scraped"
                        school["inspection_rating"]=None
                        school["inspection_date"]=soup.find_all("td", class_="date")[0].get_text()
                        school["inspection_date_long"]=datetime.strptime(school["inspection_date"], "%d %b %Y").date()
                        school["publication_date"]=soup.find_all("td", class_="date")[1].get_text()
                        school["publication_date_long"]= datetime.strptime(school["publication_date"], "%d %b %Y").date()
                        published_days=date.today()-school["publication_date_long"]       # converts publication date string to a datetime object, then a date object and calculates difference from today's date
                        if published_days.days<=7:      # strips 'days' from published.days and saves the number of days if <= a week
                            school["published_recent"]= str(published_days.days)        # saved as a string so that we don't have mixed data types for this key, and get errors when saving in SqlAlchemy
                        else:
                            school["published_recent"]= "No"
                    elif soup.find(text=" Learning and skills inspection report ") is not None:
                        school["inspection_rating_text"]="Learning and skills inspection - findings not scraped"
                        school["inspection_rating"]=None
                        school["inspection_date"]=soup.find_all("td", class_="date")[0].get_text()
                        school["inspection_date_long"]=datetime.strptime(school["inspection_date"], "%d %b %Y").date()
                        school["publication_date"]=soup.find_all("td", class_="date")[1].get_text()
                        school["publication_date_long"]= datetime.strptime(school["publication_date"], "%d %b %Y").date()
                        published_days=date.today()-school["publication_date_long"]       # converts publication date string to a datetime object, then a date object and calculates difference from today's date
                        if published_days.days<=7:      # strips 'days' from published.days and saves the number of days if <= a week
                            school["published_recent"]= str(published_days.days)        # saved as a string so that we don't have mixed data types for this key, and get errors when saving in SqlAlchemy
                        else:
                            school["published_recent"]= "No"
                    else:       # this scenario will occur where e.g. an academy conversion letter is posted on the Ofsted website, but no sec 5 or learning and skills inspection has been carried out yet
                        school["inspection_rating"]=None
                        school["inspection_date"]= "n/a"
                        school["inspection_date_long"]= None
                        school["publication_date"]= "n/a"
                        school["publication_date_long"]= None
                        school["published_recent"]= "n/a"
                        if school["school_type"]=="Free school":
                            school["inspection_rating_text"]="No section 5 inspection"
                        elif school["school_type"]== "Sponsored academy" or school["school_type"]=="Converter academy":
                            school["inspection_rating_text"]="No section 5 inspection as an academy"
            else:
                school["include"]=False
                school["inspection_rating_text"]="No section 5 inspection"
                school["inspection_rating"]=None
                school["inspection_date"]="n/a"
                school["inspection_date_long"]= None
                school["publication_date"]="n/a"
                school["publication_date_long"]= None
                school["published_recent"]="n/a"
        except:
            get_pass=0     # fails if calling page fails, or some other error occurs when working with page data
            print "Error getting inspection details: " + str(school)
    return get_pass

def validation_tests(get_pass):     # tests for two things: 1. number of inspected schools (open + closed) is in line with yesterday, 2. ratings are in line with yesterday
    saving_pass=1      # true, as code sets this to false only if one of the tests fails
    inspected_count=0
    count1,count2,count3,count4=(0,0,0,0)
    pct1,pct2,pct3,pct4=(0,0,0,0)
    for school in json:     # saves today's data, whether or not validation checks have passed. Records whether saving has been successful in saving_pass
        if school["inspection_rating"] in (1,2,3,4):
            inspected_count+=1
        if school["inspection_rating"]==1:
            count1+=1
        elif school["inspection_rating"]==2:
            count2+=1
        elif school["inspection_rating"]==3:
            count3+=1
        elif school["inspection_rating"]==4:
            count4+=1
    pct1=1.0*count1/inspected_count
    pct2=1.0*count2/inspected_count
    pct3=1.0*count3/inspected_count
    pct4=1.0*count4/inspected_count
    try:        # 1. Number of inspected schools (open + closed) is in line with yesterday
        if inspected_count>=scraperwiki.sqlite.execute("select count(1) from inspections q join (select urn, max(inspection_date_long) as max_date from inspections r group by urn) s on q.urn=s.urn and q.inspection_date_long=s.max_date where q.inspection_rating_int in (1,2,3,4)")["data"]:
            yesterday_inspected_pass=1
        else:
            yesterday_inspected_pass=0
            # print "Error saving row: " + str(school)

    except:
        yesterday_inspected_pass=None       # i.e. no data to compare against
    try:        # 2. Ratings are in line with yesterday. Needs to pass all four tests, otherwise we will set yesterday_ratings_pass to fail
        if abs(pct1-scraperwiki.sqlite.execute("select count(1) from inspections q join (select urn, max(inspection_date_long) as max_date from inspections r group by urn) s on q.urn= s.urn and q.inspection_date_long=s.max_date where q.inspection_rating_int=1")["data"])<0.05:
            yesterday_ratings_pass=0
            # print "Error saving row: " + str(school)
        elif abs(pct2-scraperwiki.sqlite.execute("select count(1) from inspections q join (select urn, max(inspection_date_long) as max_date from inspections r group by urn) s on q.urn= s.urn and q.inspection_date_long=s.max_date where q.inspection_rating_int=2")["data"])<0.05:
            yesterday_ratings_pass=0
            # print "Error saving row: " + str(school)
        elif abs(pct3-scraperwiki.sqlite.execute("select count(1) from inspections q join (select urn, max(inspection_date_long) as max_date from inspections r group by urn) s on q.urn= s.urn and q.inspection_date_long=s.max_date where q.inspection_rating_int=3")["data"])<0.05:
            yesterday_ratings_pass=0
            # print "Error saving row: " + str(school)
        elif abs(pct4-scraperwiki.sqlite.execute("select count(1) from inspections q join (select urn, max(inspection_date_long) as max_date from inspections r group by urn) s on q.urn= s.urn and q.inspection_date_long=s.max_date where q.inspection_rating_int=4")["data"])<0.05:
            yesterday_ratings_pass=0
            # print "Error saving row: " + str(school)
    except:
        yesterday_ratings_pass=None         # i.e. no data to compare against
    return yesterday_inspected_pass, yesterday_ratings_pass

def saving(yesterday_inspected_pass, yesterday_ratings_pass, get_pass):     # school results are saved where a more recent inspection exists, whatever the outcome of our validation tests are: implicit
    saving_pass=1      # true, as saving code sets this to false only if saving fails
    for school in json:     # saves today's data, whether or not validation checks have passed. Records whether saving has been successful in saving_pass
        urn=school["URN"]
        try:
            previous_inspection_date=scraperwiki.sqlite.execute("SELECT inspection_date FROM today_school_details WHERE URN=(?) ORDER BY inspection_date LIMIT 1", [urn])["data"][0][0]       # scraperwiki.sqlite.execute returns a dictionary containing an array of 'keys' and an array of 'data'. ["data"][0] returns a tuple with one element, therefore we want to select that element
            if school["inspection_date"]>previous_inspection_date:
                try:
                    scraperwiki.sql.save(["URN"], school, "Inspections")
                except:
                    saving_pass=0
                    print "Error saving row: " + str(school)
        except:         # no previous inspection is recorded for this URN
            try:
                scraperwiki.sql.save(["URN"], school, "Inspections")
            except:
                saving_pass=0
                print "Error saving row: " + str(school)
    log["run_date"]=error_log["run_date"]=datetime.now()
    log["run_date_short"]=error_log["run_date_short"]=time.strftime("%d %B %Y")
    log["get_pass"]=get_pass
    log["yesterday_inspected_pass"]=yesterday_inspected_pass
    log["yesterday_ratings_pass"]=yesterday_ratings_pass
    log["saving_pass"]=saving_pass
    scraperwiki.sql.save(["run_date"], log, "Log")
    return

get_pass=ofsted_scraper()       # get_pass status used in validation tests
yesterday_inspected_pass, yesterday_ratings_pass=validation_tests(get_pass)
saving(yesterday_inspected_pass, yesterday_ratings_pass, get_pass)
