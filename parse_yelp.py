import csv
from bs4 import BeautifulSoup
import urllib3
import requests
import os
import urllib.request
import re
import pathlib
from google.cloud import vision
import googlemaps
from googleplaces import GooglePlaces, types, lang

gmaps_api_key = "AIzaSyD0NjY0LahJtl_iHFVaXhY3tDqp85VefP4"
yelp_api_key = "-98K6QF0oXTngBc9k0Viq4OQZvvOI7s38VB5HTjcWWW_7xZuvlzgpTBYyiDyVoWAZpJTUBzi_EzwywszUfxg1vv9zTrEtNiz6IN3Xt2tFvedSUgGNyVx8U2fj2IaXnYx"
yelp_headers = {
        'Authorization': 'Bearer %s' % yelp_api_key,
    }

client = vision.ImageAnnotatorClient()
stable_url = "https://www.yelp.com"
yelp_api = "https://api.yelp.com/v3/businesses/search"

gps_coords = (38.9023134,-77.0171418)
gmaps = googlemaps.Client(key=gmaps_api_key)
reverse_geocode_result = gmaps.reverse_geocode(gps_coords)
place_id = reverse_geocode_result[0]["place_id"]
google_places = GooglePlaces(gmaps_api_key)
business_name = google_places.get_place(place_id).name

business_link = requests.get(yelp_api,
                             headers=yelp_headers, params={"latitude": gps_coords[0], "longtitude": gps_coords[1], "location": business_name, "limit": 1})
business_alias = business_link.json()["businesses"][0]["alias"]
r = requests.get("https://www.yelp.com/menu/" + business_link["alias"])
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
            for index, image_div in enumerate\
                        (soup_images.find_all("div", attrs={"class":
                                                              "photo-box photo-box--interactive"})):
                image_source = image_div.img["src"]
                folder_path = './Pictures/'+business_name+'/'+str(formal_label) #path for all the images of a restaurant
                pathlib.Path(folder_path).mkdir(parents=True, exist_ok=True)
                image_file_path = folder_path+"/"+short_label+str(index)+".jpg"
                urllib.request.urlretrieve(image_source, image_file_path)
                with open(image_file_path, 'rb') as img: response = client.label_detection(img)
                labels = str(response.label_annotations[0])
                score = float(re.findall("score:(.*)", labels)[0]) #turns string into float
                if score <= 0.95: os.remove(image_file_path)
# for folder in a-baked-joint: if the folder < 10 images, remove the image