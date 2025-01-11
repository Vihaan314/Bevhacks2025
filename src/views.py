from flask import Blueprint, render_template, request, flash, jsonify, session, redirect, url_for
from openai import OpenAI
from . import db
import os

import requests
from urllib.request import urlopen
from bs4 import BeautifulSoup
import sys

import json



def remove_first_last_lines(string):
    lines = string.splitlines()
    if len(lines) > 2:
        return '\n'.join(lines[1:-1])
    else:
        return ""
                
class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    latitude = db.Column(db.Numeric(precision = 17, scale = 14), nullable = False)
    longitude = db.Column(db.Numeric(precision = 17, scale = 14), nullable = False)

    description = db.Column(db.String())

    date = db.Column(db.DateTime(timezone=True))

    def __init__(self,lat,long,desc):
        self.latitude = lat
        self.longitude = long
        self.description = desc
    
    def to_dict(self):
        return {
            'latitude': self.latitude,
            'longitude': self.longitude,
            'description': self.description
        }
views = Blueprint('views', __name__)

@views.route('/loading', methods=['GET', 'POST'])
def loading():
    location = request.form.get('location')
    return render_template("loading.html", location=location)

@views.route('/', methods=['GET', 'POST'])
def index():
    if request.method == "POST":
        location = request.form.get('location')
        return redirect(url_for('loading', location=location))
    return render_template("index.html")

@views.route('/createWildfireStats/<location>', methods=['GET', 'POST'])
def createWildfireStats(location):
    locationFormatted = location.replace(" ", "%20")
    response = requests.request("GET", f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{locationFormatted}?unitGroup=us&key=V8W3J672HBCHJXDLTLNX248Q7&contentType=json")
    if response.status_code!=200:
        print('Unexpected Status code: ', response.status_code)
        sys.exit()  
    jsonData = response.json()

    alerts = jsonData["alerts"]
    weather = jsonData["days"][0]
    
    #national fire news scraping
    url = "https://www.nifc.gov/fire-information/nfn"
    html = urlopen(url).read()

    soup = BeautifulSoup(html, features="html.parser")

    for script in soup(["script", "style"]):
        script.extract()  

    text = soup.get_text()

    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    websiteText = '\n'.join(chunk for chunk in chunks if chunk)

    client = OpenAI()
    
    completion = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {
            "role": "user",
            "content": f"This is the location of somebody who wants to get information about wildfires in this area: {location}. Based on the recent fire news, determine if any of the information is relevant to the given location, and if so provide a summary in markdown with new lines compilable, if not return 'NA': {websiteText}"
        }
    ]
    )
    newsSummary = remove_first_last_lines(completion.choices[0].message.content)
    print(newsSummary)
    
    completion = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": f"This is the location of somebody who wants to get information about wildfires in this area: {location}. "},
        {
            "role": "user",
            "content": f"These are the alerts for the inputted location {alerts}. Please extract the alerts (especially firewatches) and return a nicely foramtted markdown of just all the alerts for that areaGive the format in markdown with appropriate new lines that is compilable. Don't add ANY other text but the plain markdown."
        }
    ]
    )
    alertsFormatted = remove_first_last_lines(completion.choices[0].message.content)
    print(alertsFormatted)

    completion = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": f"This is the location of somebody who wants to get information about wildfires in this area: {location}. "},
        {
            "role": "user",
            "content": f"These are the weather statistics for the inputted location {weather}. Please extract the main useful weather statistics and return a nicely foramtted markdown of just that for that area compilable. Don't add ANY other text but the plain markdown."
        }
    ]
    )
    weatherStats = remove_first_last_lines(completion.choices[0].message.content)

    completion = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": f"This is the location of somebody who wants to get information about wildfires in this area: {location}. "},
        {
            "role": "user",
            "content": f"I will give you a summary from the national fire news, alerts for the particular location, and the weather statistics for the particular location, and given all that you should return a final verdict (a few sentences) evaluating whether a wildfire is occuring in the location given all this information. Info: {newsSummary}, {alertsFormatted}, {weatherStats}. Please give the final verdict in a nicely foramtted markdown of just that for that area compilable. Don't add ANY other text but the plain markdown."
        }
    ]
    )
    wildfireVerdict = remove_first_last_lines(completion.choices[0].message.content)
    return redirect(url_for('views.getWildfireData', location=location, 
                            newsSummary=newsSummary, alertsFormatted=alertsFormatted, 
                            weatherStats=weatherStats, wildfireVerdict=wildfireVerdict))

@views.route('/getWildfireData', methods=['GET', 'POST'])
def getWildfireData():
    location = request.args.get('location', '')
    newsSummary = request.args.get('newsSummary', '')
    alertsFormatted = request.args.get('alertsFormatted', '')
    weatherStats = request.args.get('weatherStats', '')
    wildfireVerdict = request.args.get('wildfireVerdict', '')
    return render_template("getWildfireData.html", location=location, 
                           newsSummary=newsSummary, alertsFormatted=alertsFormatted, 
                           weatherStats=weatherStats, wildfireVerdict=wildfireVerdict)

@views.route("/report", methods = ["GET","POST"])
def report():
    
    latitude = request.form.get('lat')
    longitude = request.form.get('long')
    description = request.form.get('desc')


    try:
        new_report = Report(float(latitude), float(longitude), description)
        db.session.add(new_report)
        db.session.commit()
    
    except(Exception):
        pass
    
    
    
    
    
    reports = Report.query.all()
    reports_dict = [report.to_dict() for report in reports]
    for i in reports_dict:
        print(i['latitude'])
    return render_template('report.html', reports=reports_dict)

@views.route("\viewreport", methods = ["GET"])

def view_report():
    report_id = request.args.get('report_id')

    return render_template('viewReport.html')