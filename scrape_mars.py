import pandas as pd
import time
import pymongo
import requests
from bs4 import BeautifulSoup
from splinter import Browser

def init_browser():
    executable_path = {"executable_path": "chromedriver.exe"}
    return Browser("chrome", **executable_path, headless=False)

def scrape():
    browser = init_browser()
    mars_dict ={}

    news_url = "https://mars.nasa.gov/news/"
    browser.visit(news_url)
 
    html = browser.html
    soup = BeautifulSoup(html, 'html.parser')
    slide_elem = soup.select_one("ul.item_list li.slide")
    news_title = slide_elem.find('div', class_='content_title').text
    news_p = slide_elem.find('div', class_="article_teaser_body").text

    
    image_url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(image_url)
    browser.find_by_id('full_image').click()
    browser.find_link_by_partial_text('more info').click()
    img_soup = BeautifulSoup(browser.html,'html.parser')
    
    img_url_rel = img_soup.select_one('figure.lede a img').get('src')
    img_url = f'https://jpl.nasa.gov{img_url_rel}'


    facts_url = 'https://space-facts.com/mars/'
    tables = pd.read_html(facts_url)
    marsfacts = tables[0]
    marsfacts.columns = ["Description", "Value"]
    marsfacts_html = marsfacts.to_html()
    marsfacts_html.replace('\n', '')
    
    
    hemispheres_url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(hemispheres_url)
    hemispheres_html = browser.html
    hemispheres_soup = BeautifulSoup(hemispheres_html, 'html.parser')
    
    all_mars_hemispheres = hemispheres_soup.find('div', class_='collapsible results')
    mars_hemispheres = all_mars_hemispheres.find_all('div', class_='item')
    hemisphere_image_urls = []
    
    for i in mars_hemispheres:
        
        hemisphere = i.find('div', class_="description")
        title = hemisphere.h3.text        
        
        hemisphere_link = hemisphere.a["href"]    
        browser.visit(hemispheres_url)        
        image_html = browser.html
        image_soup = BeautifulSoup(image_html, 'html.parser')        
        image_link = image_soup.find('div', class_='downloads')
        image_url = image_link.find('li').a['href']
        
        image_dict = {}
        image_dict['title'] = title
        image_dict['img_url'] = image_url        
        hemisphere_image_urls.append(image_dict)

   
    mars_dict = {
        "news_title": news_title,
        "news_p": news_p,
        "featured_image_url": image_url,
        "fact_table": str(marsfacts_html),
        "hemisphere_images": hemisphere_image_urls
    }

    return mars_dict