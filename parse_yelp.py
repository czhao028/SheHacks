import csv
from bs4 import BeautifulSoup
import urllib3
import requests
import os
import urllib.request
import re
import pathlib


stable_url = "https://www.yelp.com"
r = requests.get("https://www.yelp.com/menu/a-baked-joint-washington-9")
soup = BeautifulSoup(r.content, features="html.parser")
for line in soup.find_all('h4'):
    for l in line.children:
        if l.name == 'a': #for each of the menu item links

            link = l["href"]
            link = stable_url + link.replace("menu", "biz_photos").replace("/item/", "?menu-item=")
            all_images = requests.get(link)
            soup_images = BeautifulSoup(all_images.content, features="html.parser")

            formal_label = l.contents[0]
            short_label = re.findall("menu-item=(.*)", link)[0]

            #for each of the images within a menu item
            for index, image_tag in enumerate\
                        (soup_images.find_all("div", attrs={"class":
                                                              "photo-box photo-box--interactive"})):

                folder_path = './'+str(formal_label) #path for all the images of a restaurant
                pathlib.Path(folder_path).mkdir(parents=True, exist_ok=True)
                urllib.request.urlretrieve(stable_url+image_tag["href"], short_label+str(index)+".jpg")
