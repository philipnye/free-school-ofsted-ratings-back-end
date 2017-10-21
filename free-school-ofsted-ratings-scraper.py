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

#scraperwiki.sqlite.execute("drop table admin_totals")
#scraperwiki.sqlite.execute("drop table Last_successful_ratings_summary")
#scraperwiki.sqlite.execute("drop table Last_successful_school_details")
#scraperwiki.sqlite.execute("drop table Today_ratings_summary")
#scraperwiki.sqlite.execute("drop table Today_school_details")

Ofsted_url_stub = "http://www.ofsted.gov.uk/inspection-reports/find-inspection-report/provider/ELS/"
import_url="https://premium.scraperwiki.com/mse5vbk/i7mrbh7eb5ovppc/sql/?q=select%0A%09URN%2C%0A%20%20%20%20schooltype%2C%0A%20%20%20%20schoolname%2C%0A%20%20%20%20schoolname_with_note_symbol%2C%0A%20%20%20%20phase%2C%0A%20%20%20%20LA%2C%0A%20%20%20%20open_date%2C%0A%20%20%20%20inspection_rating%2C%0A%20%20%20%20inspection_rating2%2C%0A%20%20%20%20publication_date%2C%0A%20%20%20%20publication_date_long%2C%0A%20%20%20%20published_recent%2C%0A%20%20%20%20inspection_date%2C%0A%20%20%20%20inspection_date_long%2C%0A%20%20%20%20URL%2C%0A%20%20%20%20include%2C%0A%20%20%20%20open_closed%2C%0A%20%20%20%20notes%2C%0A%20%20%20%20note_symbol%0Afrom%20School_details%0Aorder%20by%20urn"

json = requests.get(import_url, verify=False).json() #pulls in json and converts to json that can be used in python

NumberOfSchools = len(json)     #nb includes closed schools and yet-to-open schools
get_pass="Pass"     #changed to fail if calling a page fails, or we get an error in working with data from a page
NumberOfOpenSec5School=0
ratings =[
    {"ID":0.1,"ratingtype":"Overall","rating":1, "ratingname":"Outstanding", "ratingcount":0, "percentage":0},
    {"ID":0.2,"ratingtype":"Overall","rating":2, "ratingname":"Good", "ratingcount":0,"percentage":0},
    {"ID":0.3,"ratingtype":"Overall","rating":3, "ratingname":"Requires improvement", "ratingcount":0,"percentage":0},
    {"ID":0.4,"ratingtype":"Overall","rating":4, "ratingname":"Inadequate", "ratingcount":0,"percentage":0},
    {"ID":1.1,"ratingtype":"Primary","rating":1, "ratingname":"Outstanding", "ratingcount":0, "percentage":0},
    {"ID":1.2,"ratingtype":"Primary","rating":2, "ratingname":"Good", "ratingcount":0,"percentage":0},
    {"ID":1.3,"ratingtype":"Primary","rating":3, "ratingname":"Requires improvement", "ratingcount":0,"percentage":0},
    {"ID":1.4,"ratingtype":"Primary","rating":4, "ratingname":"Inadequate", "ratingcount":0,"percentage":0},
    {"ID":2.1,"ratingtype":"Secondary","rating":1, "ratingname":"Outstanding", "ratingcount":0, "percentage":0},
    {"ID":2.2,"ratingtype":"Secondary","rating":2, "ratingname":"Good", "ratingcount":0,"percentage":0},
    {"ID":2.3,"ratingtype":"Secondary","rating":3, "ratingname":"Requires improvement", "ratingcount":0,"percentage":0},
    {"ID":2.4,"ratingtype":"Secondary","rating":4, "ratingname":"Inadequate", "ratingcount":0,"percentage":0},
    {"ID":3.1,"ratingtype":"All-through","rating":1, "ratingname":"Outstanding", "ratingcount":0, "percentage":0},
    {"ID":3.2,"ratingtype":"All-through","rating":2, "ratingname":"Good", "ratingcount":0,"percentage":0},
    {"ID":3.3,"ratingtype":"All-through","rating":3, "ratingname":"Requires improvement", "ratingcount":0,"percentage":0},
    {"ID":3.4,"ratingtype":"All-through","rating":4, "ratingname":"Inadequate", "ratingcount":0,"percentage":0},
    {"ID":4.1,"ratingtype":"Alternative provision","rating":1, "ratingname":"Outstanding", "ratingcount":0, "percentage":0},
    {"ID":4.2,"ratingtype":"Alternative provision","rating":2, "ratingname":"Good", "ratingcount":0,"percentage":0},
    {"ID":4.3,"ratingtype":"Alternative provision","rating":3, "ratingname":"Requires improvement", "ratingcount":0,"percentage":0},
    {"ID":4.4,"ratingtype":"Alternative provision","rating":4, "ratingname":"Inadequate", "ratingcount":0,"percentage":0},
    {"ID":5.1,"ratingtype":"Special","rating":1, "ratingname":"Outstanding", "ratingcount":0, "percentage":0},
    {"ID":5.2,"ratingtype":"Special","rating":2, "ratingname":"Good", "ratingcount":0,"percentage":0},
    {"ID":5.3,"ratingtype":"Special","rating":3, "ratingname":"Requires improvement", "ratingcount":0,"percentage":0},
    {"ID":5.4,"ratingtype":"Special","rating":4, "ratingname":"Inadequate", "ratingcount":0,"percentage":0}]

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
                school["inspection_rating"] = "No section 5 inspection"
                school["inspection_rating2"] = "n/a"
                school["inspection_date"]= "n/a"
                school["inspection_date_long"]= None
                school["publication_date"]= "n/a"
                school["publication_date_long"]= None
                school["published_recent"]= "n/a"                     #we record a get error if page cannot be accessed
        except:
            get_pass="Fail"         #fails if calling page fails, or some other error occurs when working with page data
    return get_pass

def ratings_counts_and_percentages():
    NumberOfOpenSec5Schools=0
    NumberOfOpenPrimarySec5Schools=0
    NumberOfOpenSecondarySec5Schools=0
    NumberOfOpenAllThroughSec5Schools=0
    NumberOfOpenAPSec5Schools=0
    NumberOfOpenSpecialSec5Schools=0
    NumberOfOpenLSSchools=0
    NumberOfClosedSchools= 0
    NumberOfUnopenedSchools=0
    NumberOfOpenUninspectedSchools=0
    percentage_total_overall = 0
    percentage_total_primary =0
    percentage_total_secondary =0
    percentage_total_all_through =0
    percentage_total_AP =0
    percentage_total_special =0
    for school in json:
        if school["include"]==True:
            NumberOfOpenSec5Schools+=1
            for i in range (0, 24):                         #adds one to rating total for relevant rating in Overall section of ratings dictionary, and likewise for the correct phase section
                if ratings[i]["ratingtype"]=="Overall":
                    if school["inspection_rating2"] == str(ratings[i]["rating"]):
                        ratings[i]["ratingcount"] +=1
                if ratings[i]["ratingtype"]==school["phase"]:
                    if school["inspection_rating2"] == str(ratings[i]["rating"]):
                        ratings[i]["ratingcount"] +=1
                        if school["phase"]=="Primary":
                            NumberOfOpenPrimarySec5Schools+=1
                        elif school["phase"]=="Secondary":
                            NumberOfOpenSecondarySec5Schools+=1
                        elif school["phase"]=="All-through":
                            NumberOfOpenAllThroughSec5Schools+=1
                        elif school["phase"]=="Alternative provision":
                            NumberOfOpenAPSec5Schools+=1
                        elif school["phase"]=="Special":
                            NumberOfOpenSpecialSec5Schools+=1
        elif school["include"]==False:
            if school["open_closed"]== "Closed":
                NumberOfClosedSchools +=1
            elif school["open_closed"]== "Proposed to open":
                NumberOfUnopenedSchools +=1
            else:       #not included in tables, but not closed nor proposed to open
                if school["inspection_rating"]=="College inspection report - findings not scraped" or school["inspection_rating"]=="Learning and skills inspection - findings not scraped":
                    NumberOfOpenLSSchools+=1
                else:
                    NumberOfOpenUninspectedSchools+=1
    for i in range (0, 24):      #calculates percentage for each rating
        if ratings[i]["ratingtype"]=="Overall":
            percentage=round(float(ratings[i]["ratingcount"])/NumberOfOpenSec5Schools*100,0)        #rounds to 0d.p.
            ratings[i]["percentage"]=percentage
            percentage_total_overall+=percentage
        elif ratings[i]["ratingtype"]=="Primary":
            percentage=round(float(ratings[i]["ratingcount"])/NumberOfOpenPrimarySec5Schools*100,0)        #rounds to 0d.p.
            ratings[i]["percentage"]=percentage
            percentage_total_primary+=percentage
        elif ratings[i]["ratingtype"]=="Secondary":
            percentage=round(float(ratings[i]["ratingcount"])/NumberOfOpenSecondarySec5Schools*100,0)        #rounds to 0d.p.
            ratings[i]["percentage"]=percentage
            percentage_total_secondary+=percentage
        elif ratings[i]["ratingtype"]=="All-through":
            percentage=round(float(ratings[i]["ratingcount"])/NumberOfOpenAllThroughSec5Schools*100,0)        #rounds to 0d.p.
            ratings[i]["percentage"]=percentage
            percentage_total_all_through+=percentage
        elif ratings[i]["ratingtype"]=="Alternative provision":
            percentage=round(float(ratings[i]["ratingcount"])/NumberOfOpenAPSec5Schools*100,0)        #rounds to 0d.p.
            ratings[i]["percentage"]=percentage
            percentage_total_AP+=percentage
        elif ratings[i]["ratingtype"]=="Special":
            percentage=round(float(ratings[i]["ratingcount"])/NumberOfOpenSpecialSec5Schools*100,0)        #rounds to 0d.p.
            ratings[i]["percentage"]=percentage
            percentage_total_special+=percentage
    Checksum_open_inspected_schools = ratings[0]["ratingcount"]+ratings[1]["ratingcount"]+ratings[2]["ratingcount"]+ratings[3]["ratingcount"]
    Checksum_school_statuses = NumberOfOpenSec5Schools+NumberOfClosedSchools+NumberOfUnopenedSchools+NumberOfOpenLSSchools+NumberOfOpenUninspectedSchools
    admin_totals["NumberOfSchools"]  = NumberOfSchools
    admin_totals["NumberOfOpenSec5Schools"]=NumberOfOpenSec5Schools
    admin_totals["NumberOfClosedSchools"]  =NumberOfClosedSchools
    admin_totals["NumberOfUnopenedSchools"]  =NumberOfUnopenedSchools
    admin_totals["NumberOfOpenUninspectedSchools"]  =NumberOfOpenUninspectedSchools
    admin_totals["NumberOfOpenLSSchools"]  =NumberOfOpenLSSchools
    admin_totals["Checksum_school_statuses"]=Checksum_school_statuses
    admin_totals["Checksum_open_inspected_schools"]=Checksum_open_inspected_schools
    admin_totals["Percentage_total_overall"]=percentage_total_overall
    admin_totals["Percentage_total_primary"]=percentage_total_primary
    admin_totals["Percentage_total_secondary"]=percentage_total_secondary
    admin_totals["Percentage_total_all_through"]=percentage_total_all_through
    admin_totals["Percentage_total_AP"]=percentage_total_AP
    admin_totals["Percentage_total_special"]=percentage_total_special
    return NumberOfOpenSec5School

def validation_tests(get_pass):
    if admin_totals["Checksum_school_statuses"]<>admin_totals["NumberOfSchools"]:
        ratings_test_pass="Fail"
    else:
        ratings_test_pass="Pass"
    if admin_totals["Checksum_open_inspected_schools"]<>admin_totals["NumberOfOpenSec5Schools"]:
        count_test_pass="Fail"
    else:
        count_test_pass="Pass"
    if admin_totals["Percentage_total_overall"]>103 or admin_totals["Percentage_total_overall"]<97:
        percentage_test_pass="Fail"
    elif admin_totals["Percentage_total_primary"]>103 or admin_totals["Percentage_total_primary"]<97:
        percentage_test_pass="Fail"
    elif admin_totals["Percentage_total_secondary"]>103 or admin_totals["Percentage_total_secondary"]<97:
        percentage_test_pass="Fail"
    elif admin_totals["Percentage_total_all_through"]>103 or admin_totals["Percentage_total_all_through"]<97:
        percentage_test_pass="Fail"
    elif admin_totals["Percentage_total_AP"]>103 or admin_totals["Percentage_total_AP"]<97:
        percentage_test_pass="Fail"
    elif admin_totals["Percentage_total_special"]>103 or admin_totals["Percentage_total_special"]<97:
        percentage_test_pass="Fail"
    else:
        percentage_test_pass="Pass"
    if get_pass=="Fail" or ratings_test_pass=="Fail" or count_test_pass=="Fail" or percentage_test_pass=="Fail":
        spreadsheet_pass="Fail"
    else:
        spreadsheet_pass="Pass"
    admin_totals["Run_date"]  =datetime.now()
    admin_totals["Run_date_short"]= time.strftime("%d %B %Y")
    admin_totals["Get_pass"]= get_pass
    admin_totals["Ratings_test_pass"]  =ratings_test_pass
    admin_totals["Count_test_pass"]  =count_test_pass
    admin_totals["Percentage_test_pass"]  =percentage_test_pass
    # admin_totals["Spreadsheet_pass"]  =spreadsheet_pass           #saved in second set of validation tests
    return spreadsheet_pass

def yesterday_validation_tests(NumberOfOpenSec5School,spreadsheet_pass):
    try:        #catches error where admin_totals table doesn't exist (e.g. we've cleared dataset)
        scraperwiki.sqlite.execute("select Run_date, Spreadsheet_pass, Saving_pass, NumberOfClosedSchools, NumberOfUnopenedSchools, NumberOfOpenUninspectedSchools, NumberOfOpenSec5Schools from admin_totals ORDER BY Run_date DESC")["data"]
        for row in scraperwiki.sqlite.execute("select Run_date, Spreadsheet_pass, Saving_pass, NumberOfClosedSchools, NumberOfUnopenedSchools, NumberOfOpenUninspectedSchools, NumberOfOpenSec5Schools from admin_totals ORDER BY Run_date DESC")["data"]:
            yest_spreadsheet_pass=row[1]
            yest_saving_pass=row[2]
            if yest_spreadsheet_pass=="Pass"and yest_saving_pass=="Pass":   #stops once we've found first passing entry. Note that data is read in in reverse chronological order
                yest_open_sec5_schools=row[6]
                if yest_open_sec5_schools>admin_totals["NumberOfOpenSec5Schools"]:
                    yesterday_inspected_pass="Fail"
                else:
                    yesterday_inspected_pass="Pass"
                break
    except:
        yesterday_inspected_pass="No data to compare against"
    try:    #catches error where Last_successful_ratings_summary table doesn't exist (e.g. we've cleared dataset)
        for row in scraperwiki.sqlite.execute("select rating, ratingtype, ratingcount, percentage from Last_successful_ratings_summary WHERE ratingtype='Overall' ORDER BY ID")["data"]:
            #no need to check whether data has passed, as we're looking at last successful data already. Reads in only overall percentages totals
            yest_rating=row[0]   #returns data in range 1-4
            yest_count=row[2]
            for rating in ratings:      #gets use the relevant rating total from today that we want to compare against
                if rating["ratingtype"]=="Overall" and rating["rating"]==yest_rating:
                    today_count=rating["ratingcount"]
                    break       #hopefully just breaks iteration over today's rating data
            if abs(yest_count-today_count)>10:       #if we have more than 5 new ratings of any given type since the last successful run
                yesterday_ratings_pass="Fail"
                break
            else:
                yesterday_ratings_pass="Pass"
    except:
        yesterday_ratings_pass="No data to compare against"
    if not ((yesterday_inspected_pass=="Pass" and yesterday_ratings_pass=="Pass") or (yesterday_inspected_pass=="No data to compare against" and yesterday_ratings_pass=="No data to compare against")):  #existence of no yesterday data still allows today's run to be considered a success
        spreadsheet_pass="Fail"
    admin_totals["Yesterday_inspected_pass"]=yesterday_inspected_pass
    admin_totals["Yesterday_ratings_pass"]=yesterday_ratings_pass
    admin_totals["Spreadsheet_pass"]=spreadsheet_pass
    return spreadsheet_pass

def saving(spreadsheet_pass):
    saving_pass="Pass"        #true, as saving code sets this to false only if saving fails
    for school in json:     #saves today's data, whether or not validation checks have passed. Records whether saving has been successful in saving_pass
        try:
            scraperwiki.sql.save(["URN"], school, "Today_school_details")
        except:
            print "Error saving row: " + str(school)
            saving_pass="Fail"
    for rating in ratings:      #saves today's ratings summary, whether or not validation checks have passed. Records whether saving has been successful in saving_pass
        try:
            print rating
            scraperwiki.sql.save(["ID"], rating, "Today_ratings_summary")
        except:
            print "Error saving row: " + str(rating)
            saving_pass="Fail"
    if spreadsheet_pass == "Pass" and saving_pass == "Pass": #if data has passed all validation checks and saving has worked with no errors, data and ratings summary are saved as last successful records
        for school in json:
            scraperwiki.sql.save(["URN"], school, "Last_successful_school_details")
        for rating in ratings:
            scraperwiki.sql.save(["ID"], rating, "Last_successful_ratings_summary")
    admin_totals["Saving_pass"]=saving_pass
    scraperwiki.sql.save(["Run_date"], admin_totals, "admin_totals")
    return


### MAIN PROGRAMME###
get_pass=ofsted_scraper(get_pass)   #we will use get_pass status in validation tests
admin_totals=OrderedDict([
    ("Run_date","intentionally_blank"),
    ("Run_date_short","intentionally_blank"),
    ("Get_pass","intentionally_blank"),
    ("NumberOfSchools","intentionally_blank"),
    ("Checksum_school_statuses","intentionally_blank"),
    ("Count_test_pass","intentionally_blank"),
    ("NumberOfClosedSchools","intentionally_blank"),
    ("NumberOfUnopenedSchools","intentionally_blank"),
    ("NumberOfOpenUninspectedSchools","intentionally_blank"),
    ("NumberOfOpenSec5Schools","intentionally_blank"),
    ("NumberOfOpenLSSchools","intentionally_blank"),
    ("Checksum_open_inspected_schools","intentionally_blank"),
    ("Ratings_test_pass","intentionally_blank"),
    ("Percentage_total_overall","intentionally_blank"),
    ("Percentage_total_primary","intentionally_blank"),
    ("Percentage_total_secondary","intentionally_blank"),
    ("Percentage_total_all_through","intentionally_blank"),
    ("Percentage_total_AP","intentionally_blank"),
    ("Percentage_total_special","intentionally_blank"),
    ("Percentage_test_pass","intentionally_blank"),
    ("Yesterday_inspected_pass","intentionally_blank"),
    ("Yesterday_ratings_pass","intentionally_blank"),
    ("Spreadsheet_pass","intentionally_blank"),
    ("Saving_pass","intentionally_blank")
    ])
NumberOfOpenSec5School=ratings_counts_and_percentages()
spreadsheet_pass=validation_tests(get_pass)
spreadsheet_pass=yesterday_validation_tests(NumberOfOpenSec5School,spreadsheet_pass)
saving(spreadsheet_pass)
