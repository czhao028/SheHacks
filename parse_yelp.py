import csv
from bs4 import BeautifulSoup
import urllib3
import requests
import os

stable_url = "https://www.yelp.com"
r = requests.get("https://www.yelp.com/menu/a-baked-joint-washington-9")
soup = BeautifulSoup(r.content, features="html.parser")
for line in soup.find_all('h4'):
    for l in line.children:
        if l.name == 'a': #for each of the menu item links
            label = l.contents[0]
            link = l["href"]
            link = stable_url + link.replace("menu", "biz_photos").replace("/item/", "?menu-item=")
            #print(link)
            all_images = requests.get(link)
            soup_images = BeautifulSoup(all_images.content, features="html.parser")
            #for each of the images within a menu item
            for image_tag in soup_images.find_all("a", attrs={"class": "biz-shim js-lightbox-media-link js-analytics-click"}):

