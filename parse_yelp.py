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
import os
import shutil
from nltk.tokenize import RegexpTokenizer
import math

tokenizer = RegexpTokenizer(r'\w+')

gmaps_api_key = "AIzaSyD0NjY0LahJtl_iHFVaXhY3tDqp85VefP4"
yelp_api_key = "-98K6QF0oXTngBc9k0Viq4OQZvvOI7s38VB5HTjcWWW_7xZuvlzgpTBYyiDyVoWAZpJTUBzi_EzwywszUfxg1vv9zTrEtNiz6IN3Xt2tFvedSUgGNyVx8U2fj2IaXnYx"
yelp_headers = {
        'Authorization': 'Bearer %s' % yelp_api_key,
    }

client = vision.ImageAnnotatorClient()
stable_url = "https://www.yelp.com"
yelp_api = "https://api.yelp.com/v3/businesses/search"

gps_list = [(38.9224714,-77.2223935), (38.902286, -77.017414), (29.731746, -95.417742)]
# Baked & Wired, a baked joint, pepper twins

def clean_string(string):
    return "".join([c for c in string if c.isalpha() or c.isdigit() or c == ' ' or c == '/']).rstrip()


for gps_coords in gps_list:
    gmaps = googlemaps.Client(key=gmaps_api_key)
    # reverse_geocode_result = gmaps.reverse_geocode(gps_coords)
    # place_id = reverse_geocode_result[0]["place_id"]
    google_places = GooglePlaces(gmaps_api_key)

    lat_this, long_this = gps_coords
    # query_result1 = google_places.nearby_search(
    #     lat_lng={'lat': lat_this, 'lng': long_this},
    #     types=[types.TYPE_FOOD],
    #     rankby='distance').places
    query_result2 = google_places.nearby_search(
        lat_lng={'lat': lat_this, 'lng': long_this},
        types=[types.TYPE_RESTAURANT],
        rankby='distance').places
    query_result3 = google_places.nearby_search(
        lat_lng={'lat': lat_this, 'lng': long_this},
        types=[types.TYPE_CAFE],
        rankby='distance').places

    lda = lambda x,y: math.sqrt(math.pow(float(x)-lat_this, 2) + math.pow(float(y)-long_this, 2))
    #query_result1.extend(query_result2)
    query_result2.extend(query_result3)
    all_sorted = sorted(query_result2, key=lambda x: lda(x.geo_location["lat"],x.geo_location["lng"]))
    top_result = all_sorted[0]
    #if "Cushman" in top_result.name: top_result = query_result[1]
    business_name = top_result.name
    business_name_tokenized = tokenizer.tokenize(top_result.name)
    print("Business name: %s"%business_name_tokenized)
    print(lat_this, long_this)
    print({"latitude": top_result.geo_location["lat"], "longtitude": top_result.geo_location["lng"]})
    business_link = requests.get(yelp_api,
                                 headers=yelp_headers, params={"latitude": top_result.geo_location["lat"], "longitude": top_result.geo_location["lng"],
                                                               "limit": 5,
                                                               "sort_by": "distance", "categories":"restaurants,food"})
    print(business_link.json())
    business_alias = ""
    top_businesses = business_link.json()["businesses"]
    try:
        for business in top_businesses:
            print(business)
            if tokenizer.tokenize(business["name"]) == business_name_tokenized:
                business_alias = business["alias"]
                break

    except Exception as e:
        print(e)
        print("No restaurants nearby")
        continue
    else:
        if len(business_alias) == 0: #picks the top result from Yelp
            business_alias = top_businesses[0]["alias"]
            business_name = top_businesses[0]["name"]

    print(business_alias)
    r = requests.get("https://www.yelp.com/menu/" + business_alias)
    if r.status_code != 200: continue
    soup = BeautifulSoup(r.content, features="html.parser")
    all_h4 = soup.find_all('h4')
    if len(all_h4) == 0: continue
    for line in all_h4:
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
                    folder_path = clean_string('Pictures/'+business_name+'/'+str(formal_label))#path for all the images of a restaurant
                    print(folder_path)
                    pathlib.Path(folder_path).mkdir(parents=True, exist_ok=True)
                    image_file_path = folder_path+"/"+short_label+str(index)+".jpg"
                    urllib.request.urlretrieve(image_source, image_file_path)
                    with open(image_file_path, 'rb') as img: response = client.label_detection(img)
                    food_label = [str(flabel) for flabel in response.label_annotations if "food" in str(flabel).lower()]
                    try:
                        labels = food_label[0]
                        score = float(re.findall("score:(.*)", labels)[0]) #turns string into float
                        if score <= 0.95: os.remove(image_file_path) #if it's less confident
                    except: # couldn't find any food in the image
                        os.remove(image_file_path)
                        print("No food found in photo" + image_file_path)

    #for folder in folder_path_containing_business_name
    base_path = "./Pictures/"+business_name + "/" # main business
    bucket_base_path = "gs://shehacks-1578767594591-vcm/"
    path, dirs, files = next(os.walk(base_path))
    #bucket name = gs://shehacks-1578767594591-vcm/Restaurant/imagename.jpg
    with open(business_name + " Model Data.csv", "w") as csv_file:
        csv_writer = csv.writer(csv_file)
        for dir in dirs: # all its foods
            print(base_path+dir)
            path2, dir2, files2 = next(os.walk(base_path+dir))
            if len(files2) < 5:
                shutil.rmtree(path2)
                continue
            for file in files2:
                csv_writer.writerow([path2.replace("./Pictures/", bucket_base_path) + "/" + file, dir[:31]])
                #labels are max 32 characters


        #path, dirs, files = next(os.walk("./Pictures/" + business_name))
    #if the folder has less than 10 pictures, delete it

# for folder in a-baked-joint: if the folder < 10 images, remove the image