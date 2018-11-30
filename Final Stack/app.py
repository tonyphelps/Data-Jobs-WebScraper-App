#This file contains the flask application
#methods from scrape.py are used to scrape

from flask import Flask, render_template, redirect
from flask_pymongo import PyMongo
# from scrape import scrape
from bs4 import BeautifulSoup as bs
from splinter import Browser
from selenium import webdriver
import json
from bson import json_util

#initiate flask and flask_pymongo
app=Flask(__name__)

#connent pymongo to test_scrape_db within monog server
app.config['MONGO_URI'] = 'mongodb://localhost:27017/test_scrape_db'
mongo = PyMongo(app)

#url dictionary that contains indeed scraping material
url_dict = {"data_scientist":"https://www.indeed.com/jobs?as_and=data+scientist&as_phr=&as_any=&as_not=&as_ttl=data+scientist&as_cmp=&jt=all&st=&as_src=&salary=&radius=0&l=CA&fromage=any&limit=50&sort=date&psf=advsrch",
            "data_analyst":"https://www.indeed.com/jobs?as_and=data+analyst&as_phr=&as_any=&as_not=&as_ttl=data+analyst&as_cmp=&jt=all&st=&as_src=&salary=&radius=0&l=CA&fromage=any&limit=50&sort=date&psf=advsrch"}


@app.route('/')
def index():


    ##Code for donughts:
     #1) store reference of mongoDB-collection as coll
    coll = mongo.db.data_analyst_job
    coll2 = mongo.db.data_scientist_job

    #2) store the contents of the collection (as a cursor) into pull_coll
    pull_coll = coll.find()
    pull_coll2 = coll2.find()

    #3) iterate and store as a list the pymongo cursor to make any use of the collection
    list_coll = [doc for doc in pull_coll]
    list_coll2 = [doc for doc in pull_coll2]

    ##code for returning  a dictionary with the count
    analyst_comp =[doc['properties']['Company'] for doc in list_coll]
    scientist_comp =[doc['properties']['Company'] for doc in list_coll2]


#add two donuts, one for count 1s and one for one or more
    count_comp_analyst = {}
    for company in analyst_comp:
        if company in count_comp_analyst:
            count_comp_analyst[company] +=1
        else:
            count_comp_analyst[company] =1

    count_comp_scientist = {}
    for company in scientist_comp:
        if company in count_comp_scientist:
            count_comp_scientist[company] +=1
        else:
            count_comp_scientist[company] =1


    #final)render the list of skills to index.html
    return render_template("index.html", comp_analyst = count_comp_analyst, comp_scientist = count_comp_scientist)

@app.route('/leaflet-analyst')
def leafAnalyst():

    ########This returns a graph from mongo database#######
    #1) store reference of mongoDB-collection as coll
    coll = mongo.db.data_analyst_job

    #2) store the contents of the collection (as a cursor) into pull_coll
    pull_coll = coll.find({}, {'_id': False})

    #3) iterate and store as a list the pymongo cursor to make any use of the collection
    list_coll = [doc for doc in pull_coll]

    #5)render the list of skills to index.html
    # return render_template("index.html", list_coll = list_coll)
    return json.dumps(list_coll, default=json_util.default)

@app.route('/leaflet-scientist')
def leafScientist():

    ########This returns a graph from mongo database#######
    #1) store reference of mongoDB-collection as coll
    coll2 = mongo.db.data_scientist_job

    #2) store the contents of the collection (as a cursor) into pull_coll
    pull_coll2 = coll2.find({}, {'_id': False})

    #3) iterate and store as a list the pymongo cursor to make any use of the collection
    list_coll2 = [doc for doc in pull_coll2]

    #5)render the list of skills to index.html
    # return render_template("index.html", list_coll2 = list_coll2)
    return json.dumps(list_coll2, default=json_util.default)


@app.route('/scrape')
def scrape_please():

    from scrape import scrape

    #drop the collection thats already in the database
    mongo.db.drop_collection("data_analyst_job")
    mongo.db.drop_collection("data_scientist_job")


    #pre definined skills dictionary that are sought for and their written variations
    skills_dict = {
        'Excel' : ['Excel','MSExcel','excel','msexcel','EXCEL'],
        'SQL': [' SQL ',' sql ',' Sql '],
        'mySQL' : ['mysql', 'mySQL'],
        'Python': ['python','Python','PYTHON'],
        'JavaScript':['JS','JavaScript','javascript'],
        'Java':['Java', 'java','JAVA'],
        'pandas': ['Pandas','pandas','PANDAS'],
        'html':['html','Html','HTML'],
        'MongoDB':['Mongo','MongoDB',],
        'CSS':['css','Css','CSS'],
        'Leaflet':['Leafelet','leaflet','LEAFLET'],
        'Numpy':['numpy','Numpy','NUMPY'],
        'VBA':['vba','VBA','Vba'],
        'd3':['d3','D3'],
        'matplotlib':['Matplotlib','matplotlib'],
        'Plotly': ['Plotly','PlotLy'],
        'Tableau':['Tableau','tableau','TABLEAU'],
        'Machine Learning':['Machine Learning','Machine learning','machine learning'],
        'R':[' r ',' R ','RStudio','Rstudio','rstudio','R studio','R Studio'],
        'Bachelors':['Bachelors',"Bachelor's", 'bachelors',"bachelor's"],
        'Masters':['Masters','masters'],
        'PhD':['PhD','phd','PHD']
    }
    #initiate scraping for urls
    results = {}
    for classification, url in url_dict.items():
        results[classification] = scrape(url,1,skills_dict)

    data_analyst_list = results['data_analyst']
    data_scientist_list = results['data_scientist']

    collec = mongo.db.data_analyst_job
    collec.insert_many(data_analyst_list)

    collec = mongo.db.data_scientist_job
    collec.insert_many(data_scientist_list)

    return redirect("/", code=302)


if __name__ == "__main__":
    app.run(debug=True)