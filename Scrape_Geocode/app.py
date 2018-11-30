#This file contains the flask application
#methods from scrape.py are used to scrape

from flask import Flask, render_template, redirect
from flask_pymongo import PyMongo
# from scrape import scrape
from bs4 import BeautifulSoup as bs
from splinter import Browser
from selenium import webdriver

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

    ########This returns a graph from mongo database#######

    #1) store reference of mongoDB-collection as coll
    coll = mongo.db.data_analyst_job
    coll2 = mongo.db.data_scientist_job

    #2) store the contents of the collection (as a cursor) into pull_coll
    pull_coll = coll.find()
    pull_coll2 = coll2.find()

    #3) iterate and store as a list the pymongo cursor to make any use of the collection
    list_coll = [doc for doc in pull_coll]
    list_coll2 = [doc for doc in pull_coll2]

    #4) make a list of the skills list
    list_skills_list = [doc['properties']['Skills_List'] for doc in list_coll]
    list_skills_list2 = [doc['properties']['Skills_List'] for doc in list_coll2]

    #5)render the list of skills to index.html
    return render_template("index.html", list_coll = list_skills_list, list_coll2 = list_skills_list2)


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
        results[classification] = scrape(url,4,skills_dict)

    data_analyst_list = results['data_analyst']
    data_scientist_list = results['data_scientist']

    collec = mongo.db.data_analyst_job
    collec.insert_many(data_analyst_list)

    collec = mongo.db.data_scientist_job
    collec.insert_many(data_scientist_list)

    return redirect("/", code=302)


if __name__ == "__main__":
    app.run(debug=True)