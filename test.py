import os
import shutil
import csv
business_name = "A Baked Joint"
base_path = "./Pictures/"+business_name+"/" # main business
bucket_base_path = "gs://shehacks-1578767594591-vcm/"
path, dirs, files = next(os.walk(base_path))
#bucket name = gs://shehacks-1578767594591-vcm/Restaurant/imagename.jpg
with open(business_name + " Model Data.csv", "w") as csv_file:
    csv_writer = csv.writer(csv_file)
    for dir in dirs: # all its foods
        path2, dir2, files2 = next(os.walk(base_path+dir))
        if len(files2) < 10:
            shutil.rmtree(path2)
            continue
        for file in files2:
            csv_writer.writerow([bucket_base_path + business_name + "/" + file, dir])