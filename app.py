from app_store_scraper import AppStore
from expertai.nlapi.common.model import sentiment
from flask import Flask, render_template, request
from datetime import datetime
import tweepy
import os
import json
import requests
import re
from bs4 import BeautifulSoup
import database




os.environ["EAI_USERNAME"] = 'pratyushks159@gmail.com'
os.environ["EAI_PASSWORD"] = 'n&wS7tiNTeGj24x'

access_token = "1428296597885095936-9Dbf97CIbdAYjfhKvBwVRARfs3bBKi"
access_token_secret = "zVIIfiGM7mUAFXhdEqqq6PU4HM2N6Rxl1X3DWJDbEzT3l"

api_key = "KOFO5sKlut0sc3F30py0ktwHF"
api_key_secret = "OykIIGOfgIr5iYwcSW7J5C72k95cRdci3E6jvYCU01uwgvDN7D"

from expertai.nlapi.cloud.client import ExpertAiClient
client = ExpertAiClient()
import os

app = Flask(__name__)

database.create_tables()

database.create_tables_playstore()

database.create_table_chat()

auth = tweepy.OAuthHandler(consumer_key=api_key,consumer_secret=api_key_secret)
auth.set_access_token(access_token,access_token_secret)
api=tweepy.API(auth)



language= 'en'

@app.route("/home", methods=["GET", "POST"])
def House():   
    return render_template("home.html")



@app.route("/", methods=["GET", "POST"])
def home():
    negative=[]
    positive=[]
    neutral=[]
    review=[]
    neg=[]
    comnam=[]   
        
    if request.method == "POST":
        negative.clear()
        positive.clear()
        neutral.clear()
        review.clear()
        neg.clear()
        comnam.clear()
        database.delete_entries()
        entry_content = request.form.get("content")
        r = requests.get(entry_content)
        soup = BeautifulSoup(r.text, 'html.parser')
        results = soup.findAll('p', {'class':re.compile('.*comment.*')})
        reviews = [result.text for result in results]

        result = soup.findAll('h1', attrs={'class':'css-11q1g5y'})
        name = [results.text for results in result]
        comnam.append(name)

        
        for info in reviews:            
            output = client.specific_resource_analysis(body={"document": {"text":  info}}, params={'language': language, 'resource': 'sentiment'})
            review.append(info)
            database.create_entry(info, output.sentiment.overall)
            
            if output.sentiment.overall>0:
                positive.append(info)
            elif output.sentiment.overall<0:
                negative.append(info)
                document = client.specific_resource_analysis(body={"document": {"text": info}}, params={'language': language, 'resource': 'relevants'})
                for mainlemma in document.main_lemmas:
                    neg.append(mainlemma.value)

            else:
                neutral.append(output.sentiment.overall)           
 
    return render_template("dashboard.html", positive=json.dumps(positive), negative=json.dumps(negative), neutral=json.dumps(neutral), neg=neg, reviews=review, comnam=json.dumps(comnam), neutralrev=neutral,negativerev=negative,positiverev=positive)

@app.route("/AmazonReviews", methods=["GET", "POST"])
def AmazonReviews():
    negative=[]
    positive=[]
    neutral=[]
    review=[]
    neg=[]    
        
    if request.method == "POST":
        negative.clear()
        positive.clear()
        neutral.clear()
        review.clear()
        neg.clear()
        entry_content = request.form.get("content")
        r = requests.get(entry_content)
        soup = BeautifulSoup(r.text, 'html.parser')
        results = soup.findAll('span', attrs={'data-hook':'review-body'})
        reviews = [result.text for result in results]
        
        for info in reviews:            
            output = client.specific_resource_analysis(body={"document": {"text":  info}}, params={'language': language, 'resource': 'sentiment'})
            review.append(info)
            
            if output.sentiment.overall>0:
                positive.append(info)
            elif output.sentiment.overall<0:
                negative.append(info)
                document = client.specific_resource_analysis(body={"document": {"text": info}}, params={'language': language, 'resource': 'relevants'})
                for mainlemma in document.main_lemmas:
                    neg.append(mainlemma.value)

            else:
                neutral.append(output.sentiment.overall)           
 
    return render_template("AmazonReviews.html", positive=json.dumps(positive), negative=json.dumps(negative), neutral=json.dumps(neutral), neg=neg, reviews=review)


@app.route("/AppStore-Reviews", methods=["GET", "POST"])
def AppStoreReviews():
           
    negative=[]
    positive=[]
    neutral=[]
    review=[]
    neg=[]  
    data = []  
    applinkedd=[]
    dates=[]
    sorteddates=[]
    clear=[]
    ratings=[]
        
    if request.method == "POST":
        negative.clear()
        positive.clear()
        neutral.clear()
        review.clear()
        neg.clear()
        data.clear()
        applinkedd.clear()
        dates.clear()
        sorteddates.clear()
        clear.clear()
        ratings.clear()
        database.delete_entries_playstore()
        entry_content = request.form.get("content")       
        applink=entry_content
        applinks=entry_content
        applinklo=entry_content
        applink = applink[applink.index('id')+2:]
 
        applinke = applinks[applinks.index('/app/')+5:applinks.index('id')-1]
        applinklo = applinklo[applinklo.index('com')+4:applinklo.index('app/')-1]
   

        minecraft = AppStore(country=applinklo, app_name=applinke, app_id=applink)
        applinkedd.append(applinke)
        minecraft.review(how_many=10)
        
        for i in range(10):
            data.append(minecraft.reviews[i]['review'])
            dates.append(minecraft.reviews[i]['date'])
            ratings.append(minecraft.reviews[i]['rating']) 

        dates.sort(key=lambda date: datetime.strftime(date, "%Y-%m-%d"))

        for i in range(10):
            sorteddates.append(str(dates[i]))

        for i in range(10):
            cleardates = sorteddates[i][sorteddates[i].index(' ')-10:sorteddates[i].index(' ')+1:]
            clear.append(cleardates)
        
        for info in data:            
            output = client.specific_resource_analysis(body={"document": {"text":  info}}, params={'language': language, 'resource': 'sentiment'})
            review.append(info)
            database.create_entry_playstore(info, output.sentiment.overall)
            
            if output.sentiment.overall>0:
                positive.append(info)
            elif output.sentiment.overall<0:
                negative.append(info)
                document = client.specific_resource_analysis(body={"document": {"text": info}}, params={'language': language, 'resource': 'relevants'})
                for mainlemma in document.main_lemmas:
                    neg.append(mainlemma.value)

            else:
                neutral.append(output.sentiment.overall)           
 
    return render_template("AppStore-Reviews.html", positive=json.dumps(positive), negative=json.dumps(negative), neutral=json.dumps(neutral), neg=neg, reviews=review,  neutralrev=neutral,negativerev=negative,positiverev=positive,applinke=json.dumps(applinkedd),clear=json.dumps(clear),ratings=json.dumps(ratings))




@app.route("/Twitter-Search", methods=["GET", "POST"])
def tweet():

    tweet=[]
    sentiment=[]
    positive=[]
    negative=[]
    neutral=[]
    
    if request.method == "POST":
        negative.clear()
        positive.clear()
        neutral.clear()
        tweet.clear()
        sentiment.clear()
        entry_content = request.form.get("content")
        tweets = tweepy.Cursor(api.search,q=entry_content).items(10)

        for info in tweets:
            tweet.append(info.text)
            output = client.specific_resource_analysis(body={"document": {"text":  info.text}}, params={'language': language, 'resource': 'sentiment'})
            sentiment.append(output.sentiment.overall)
            if output.sentiment.overall>0:
                positive.append(output.sentiment.overall)
            elif output.sentiment.overall<0:
                negative.append(output.sentiment.overall)
            else:
                neutral.append(output.sentiment.overall)

 
    return render_template("TwitterSearch.html", positive=json.dumps(len(positive)), negative=json.dumps(len(negative)), neutral=json.dumps(len(neutral)), tweet=tweet)


@app.route("/compare-yelp", methods=["GET", "POST"])
def Compare():
    negative=[]
    positive=[]
    neutral=[]
    review=[]
    neg=[]
    
    
    if request.method == "POST":
        negative.clear()
        positive.clear()
        neutral.clear()
        review.clear()
        neg.clear()
        entry_content = request.form.get("content")
        r = requests.get(entry_content)
        soup = BeautifulSoup(r.text, 'html.parser')
        results = soup.findAll('p', {'class':re.compile('.*comment.*')})
        reviews = [result.text for result in results]

        result = soup.findAll('h1', attrs={'class':'css-11q1g5y'})
        review = [result.text for result in result]
        
        for info in reviews:            
            output = client.specific_resource_analysis(body={"document": {"text":  info}}, params={'language': language, 'resource': 'sentiment'})
            review.append(info)    
            if output.sentiment.overall>0:
                positive.append(output.sentiment.overall)
            elif output.sentiment.overall<0:
                negative.append(output.sentiment.overall)
            else:
                neutral.append(output.sentiment.overall)  
    entries=database.retrieve_entries()
    return render_template("competative_analysis.html", data=json.dumps(entries),positive=json.dumps(len(positive)), negative=json.dumps(len(negative)), neutral=json.dumps(len(neutral)), neg=neg, reviews=review, entries=entries)


@app.route("/compare-appstore", methods=["GET", "POST"])
def Compareappstore():
    negative=[]
    positive=[]
    neutral=[]
    review=[]
    neg=[]
    reviews=[]
    
    
    if request.method == "POST":
        negative.clear()
        positive.clear()
        neutral.clear()
        review.clear()
        reviews.clear()
        neg.clear()
        entry_content = request.form.get("content")       
        applink=entry_content
        applinks=entry_content
        applinklo=entry_content
        applink = applink[applink.index('id')+2:]
 
        applinke = applinks[applinks.index('/app/')+5:applinks.index('id')-1]

        applinklo = applinklo[applinklo.index('com')+4:applinklo.index('app/')-1]
   

        minecraft = AppStore(country=applinklo, app_name=applinke, app_id=applink)
        minecraft.review(how_many=10)
        for i in range(10):
            reviews.append(minecraft.reviews[i]['review']) 
        
        for info in reviews:            
            output = client.specific_resource_analysis(body={"document": {"text":  info}}, params={'language': language, 'resource': 'sentiment'})
            review.append(info)    
            if output.sentiment.overall>0:
                positive.append(output.sentiment.overall)
            elif output.sentiment.overall<0:
                negative.append(output.sentiment.overall)
            else:
                neutral.append(output.sentiment.overall)  
    entries=database.retrieve_entries_playstore()
    return render_template("competative_playstore.html", data=json.dumps(entries),positive=json.dumps(len(positive)), negative=json.dumps(len(negative)), neutral=json.dumps(len(neutral)), neg=neg, reviews=review, entries=entries)


@app.route("/feedback", methods=["GET", "POST"])
def feedback():
    if request.method == "POST":
          entry_contents = request.form.get("contents")
          output = client.specific_resource_analysis(body={"document": {"text": entry_contents}},params={'language': language, 'resource': 'sentiment'})
          
          database.create_entrys_chat(entry_contents, output.sentiment.overall)
          print(output.sentiment.overall)

    return render_template("feedback.html")


@app.route('/negative', methods=["GET", "POST"])
def negative():
    return render_template("negative.html", entries=database.retrieve_entrie_chat())


@app.route('/positive', methods=["GET", "POST"])
def positive():
    return render_template("positive.html", entries=database.retrieve_entrie_chat())
if __name__ == '__main__':
    app.run(debug=True)