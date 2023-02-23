import datetime
import os
import json
import random
import requests

from PIL import Image, ImageOps
from pillow_heif import register_heif_opener

register_heif_opener()

import CibicObjects

cache_folder = "../_exports/pickle_jar/"
output_folder = "../_outputs/"
process_folder = "../_process/"


def last_day_of_month(any_day):
    # The day 28 exists in every month. 4 days later, it's always next month
    next_month = any_day.replace(day=28) + datetime.timedelta(days=4)
    # subtracting the number of the current day brings us back one month
    return next_month - datetime.timedelta(days=next_month.day)



def hash_name(name):
	name = "".join(name.split(".")[:-1])
	name = "".join([c for c in name if c.isalpha() or c.isdigit()])
	return name

def get_name(url):
	return url.split("&path=")[1]

def make_thumbnail(image_path, output_dir, output_name):
	try:
		im = Image.open(image_path)
		im = ImageOps.exif_transpose(im)
		size = (400,400)
		im.thumbnail(size)
		im.save(output_dir+output_name, "JPEG")
		return output_name
	except Exception as e :
		print(e)
		return None



year = 2022
month = 11

color_lookup = [
	"#0077BB",
	"#33BBEE",
	"#009988",
	"#EE7733",
	"#CC3311",
	"#EE3377",
]


startTime = datetime.datetime(year, month, 1).replace(tzinfo=datetime.timezone.utc)
endTime = last_day_of_month(startTime).replace(tzinfo=datetime.timezone.utc)

viz_window_end = datetime.datetime.now().replace(tzinfo=datetime.timezone.utc)
viz_window_start = viz_window_end - datetime.timedelta(days=30)


DataController = CibicObjects.data_controller.DataController()
#DataController.Run(start=startTime, end=endTime, to_bin=True, path=cache_folder)

DataController.Load_from_cache(cache_folder)

all_geoJSON = []

all_rides = CibicObjects.cibic_objects.RideList(DataController.Rides)

windowed_rides = all_rides.between(viz_window_start, viz_window_end)


for ride in windowed_rides:
	
	ride_color = random.choice(color_lookup)
	geoJSON_for_web = ride.Geo_JSON_Obj
	if geoJSON_for_web['properties']['flow'] is not None:
		del geoJSON_for_web['properties']["displayName"]
		del geoJSON_for_web['properties']["podMember"]
		del geoJSON_for_web['properties']["userId"]

		if ride.journaled_data is not None:
			geoJSON_for_web['properties']["journal"] = ride.journaled_data.journal
			geoJSON_for_web['properties']["answers"] = ride.journaled_data.answers

		geoJSON_for_web['properties']['web_viz_color'] = ride_color 

		all_geoJSON.append(geoJSON_for_web)


print(len(all_geoJSON))

all_photos = []
for ride in windowed_rides:
	if ride.journaled_data is not None:
		if ride.journaled_data.media is not None:
			all_photos.append(ride.journaled_data.media)

print(len(all_photos))






photo_urls = sum(all_photos, [])

photo_names = [get_name(filename) for filename in photo_urls]
photo_hash_names = [hash_name(filename) for filename in photo_names]



photos_for_viz = []

for idx, photo_hash in enumerate(photo_names):
	image_path = process_folder+photo_hash
	if os.path.exists(image_path):
		print("photo already cached")
		photos_for_viz.append( make_thumbnail(image_path, output_folder+"/photos/", photo_hash_names[idx]+".jpg") )
		continue

	url = photo_urls[idx]
	img_data = requests.get(url).content
	with open(image_path, 'wb') as handler:
		handler.write(img_data)
	
	photos_for_viz.append(  make_thumbnail(image_path, output_folder+"/photos/", photo_hash_names[idx]+".jpg") )
	




photos_for_viz = [i for i in photos_for_viz if i is not None]
print(photos_for_viz)




with open(output_folder+"data/gallery.json", 'w') as f:
	
	f.write(json.dumps(photos_for_viz))



with open(output_folder+"data/web_viz.json", 'w') as f:
	
	f.write(json.dumps(all_geoJSON))