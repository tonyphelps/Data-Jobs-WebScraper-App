#import dependencies
from bs4 import BeautifulSoup as bs
from splinter import Browser
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import datetime
from config import gkey
import requests


#Scrape function parameters include:
#--1) Indeed url to scrape from
#--2) browser
#--3) amount of search result pages from indeed to scrape
#--4) a dictionary with the skills sought out for
def scrape_indeed(url,pages, skills_dict):


    def init_browser(): 
        #PC Chrome Driver
        #executable_path = {'executable_path':'chromedriver.exe'}
        #Mac Chrome Driver
        executable_path = {'executable_path':'./chromedriver'}
        return Browser('chrome',**executable_path, headless=False)

    browser = init_browser()
    #browser.driver.maximize_window()
    browser.driver.set_window_size(1680, 1050)
    
    #initialize finction for counting skills
    def count_skills(skills_dict, text):
        skills_count = []
        for skill, variations in skills_dict.items():
            for variation in variations:
                if variation in text:
                    skills_count.append(skill)
                    break
        return skills_count

    #inititalizing empty list for future documents
    features = []
    
    #Visit the url and soup the page 
    browser.visit(url)
    html= browser.html
    soup = bs(html, "html.parser")
    
    #Begining of scraping for pagination links
    #find the div that contains all the pagination elements and get all the href
    #Store all the hrefs in a list which will be used to go through as many pages as dictated by the parament "pages"
    div_pagination = soup.find('div', {'class':'pagination'})
    pagination_links = div_pagination.find_all('a')

    pagination_a_tags = []
    for a_tag in pagination_links:
        a = a_tag.get('href')
        pagination_a_tags.append(a)
    
    #start the scraping N number of pages
    for page in range(0, pages):
        
        #after each page loads, sleep for 2 seconds to allow loading
        time.sleep(2)
    
        #pop up may spawn: this try/except closes them if they appear
        try:
            browser.find_by_id('popover-close-link').click()
        except:
            print('no popup over foreground found')

        #for each page, gather the soup and collect all the divs that contain the row result clickcads
        html= browser.html
        soup = bs(html, "html.parser")
        div_results = soup.find_all('div', {'class':'row result clickcard'})
        
        # for each of these divs, find the a tags
        a_tags = []
        for div in div_results:
            aa = div.a.get('href')
            a_tags.append(aa)
        print(f"Total amount of postings on page {page}, {len(a_tags)}, for url {url[:55]}")

        counter = 0

        for tag in a_tags:
            
             #pop up may spawn: this try/except closes them if they appear
            try:
                browser.find_by_id('popover-close-link').click()
                print('there was a popup')
            except:
                print('no random popup')
            
            #initiate an empty dictionary
            job_feature = {
                "type": "Feature",
                "geometry":{ 
                    "type": "Point",
                    "coordinates" : [],    
                },
                "properties":{        
                }
            }
             
            browser.find_link_by_partial_href(tag).click()
            time.sleep(0.2)
            soup2 = bs(browser.html, "html.parser")
            try:
                
                job_description = soup2.find('div', {'id':'vjs-tab-job'}).get_text()

                target_city = soup2.find('span', {'id':'vjs-loc'}).get_text().split(" - ")[1].split(",")[0]
                
                target_url = "https://maps.googleapis.com/maps/api/geocode/json?" \
                "address=%s&key=%s" % (target_city, gkey)
                req = requests.get(target_url)
                res = req.json()
                result = res['results'][0]

                result_long = result['geometry']['location']['lng']
                result_lat = result['geometry']['location']['lat']

                job_feature['geometry']['coordinates'] = [result_long,result_lat]

                

                job_feature['properties']['Website'] = "Indeed"
                job_feature['properties']['Job_Title'] = soup2.find('div', {'id':'vjs-jobtitle'}).get_text()
                job_feature['properties']['Job_Description'] = job_description
                job_feature['properties']['Company'] = soup2.find('span', {'id':'vjs-cn'}).get_text()
                job_feature['properties']['Location'] = soup2.find('span', {'id':'vjs-loc'}).get_text().split(" - ")[1].split(",")[0]
                job_feature['properties']['Skills_List'] = count_skills(skills_dict, job_description)
                job_feature['properties']['Job_Posting_URL'] = url+tag
                job_feature['properties']['Job_Scrape_Date'] = datetime.datetime.now()
                job_feature['properties']['Posted_Days_Ago'] = soup2.find('div', {'id':'vjs-footer'}).span.get_text()
                features.append(job_feature)
                
            except:
                print(f"-----------------Error at {counter}----------------")
                
            counter += 1
            print(f"Current page: {page}, current listing {counter} out of {len(a_tags)}, current url {url[:55]}")
            print(job_feature['geometry']['coordinates'])
        browser.find_link_by_partial_href(pagination_a_tags[page]).click()
        
    
    return features

def scrape_monster(url, skills_dict):


    def init_browser(): 
        #PC Chrome Driver
        #executable_path = {'executable_path':'chromedriver.exe'}
        #Mac Chrome Driver
        executable_path = {'executable_path':'./chromedriver'}
        return Browser('chrome',**executable_path, headless=False)

    browser = init_browser()
    #browser.driver.maximize_window()
    browser.driver.set_window_size(1680, 1050)
    
    #initialize finction for counting skills
    def count_skills(skills_dict, text):
        skills_count = []
        for skill, variations in skills_dict.items():
            for variation in variations:
                if variation in text:
                    skills_count.append(skill)
                    break
        return skills_count

    #inititalizing empty list for future documents
    features = []
    
    #Visit the url and soup the page 
    browser.visit(url)
    time.sleep(2)
    button = browser.find_by_id('loadMoreJobs')
    button.click()
    time.sleep(2)
    button.click()
    time.sleep(2)
    button.click()
    time.sleep(2)
    button.click()
    time.sleep(2)
    button.click()
    time.sleep(2)
    button.click()
    time.sleep(2)
    button.click()
    time.sleep(2)

    html= browser.html
    soup = bs(html, "html.parser")
    
    div_results = soup.find_all('div', {'class':'summary'})

    mons_a_tags = []

    for div in div_results:
        a = div.a.get('href')
        mons_a_tags.append(a[:70])

    counter = 0

    for tag in mons_a_tags:

        browser.find_link_by_partial_href(tag).click()
        time.sleep(0.2)
        html2 = browser.html
        soup2 = bs(html2, "html.parser")

                    #initiate an empty dictionary
        job_feature = {
                "type": "Feature",
                "geometry":{ 
                    "type": "Point",
                    "coordinates" : [],    
                },
                "properties":{        
                }
            }

        try: 
    
                
            job_description = soup2.find('div', {'class':'details-content'}).get_text()

            try: 
                target_city = soup2.find('h2', {'class':'subtitle'}).get_text().split(",")[0].split(",")[0]
                target_url = "https://maps.googleapis.com/maps/api/geocode/json?" \
                "address=%s&key=%s" % (target_city, gkey)
                req = requests.get(target_url)
                res = req.json()
                result = res['results'][0]

                result_long = result['geometry']['location']['lng']
                result_lat = result['geometry']['location']['lat']

                job_feature['geometry']['coordinates'] = [result_long,result_lat]
                job_feature['properties']['Location'] = soup2.find('h2', {'class':'subtitle'}).get_text().split(",")[0].split(",")[0]
            except:
                print(f"-----------------Error at {counter}----------------")
    
                print(job_feature['geometry']['coordinates'])
                print(job_feature['properties']['Location'])

            job_feature['properties']['Website'] = "Monster"
            job_feature['properties']['Job_Title'] = soup2.find('h1', {'class':'title'}).get_text().strip()
            job_feature['properties']['Job_Description'] = job_description
            job_feature['properties']['Company'] = "Located in job title"
            
            job_feature['properties']['Skills_List'] = count_skills(skills_dict, job_description)
            job_feature['properties']['Job_Posting_URL'] = url+tag
            job_feature['properties']['Job_Scrape_Date'] = datetime.datetime.now()
            job_feature['properties']['Posted_Days_Ago'] = "xdays ago"
            features.append(job_feature)
                
        except:
            print(f"-----------------Error at {counter}----------------")
                
        counter += 1
        print(f"current listing {counter} out of {len(mons_a_tags)}, current url {url[:55]}")

        
        
    
    return features