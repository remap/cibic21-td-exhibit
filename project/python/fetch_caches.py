import datetime
import os
import json
import sys

import CibicObjects

cache_folder = "../_exports/pickle_jar/"
output_folder = "../_outputs/"






def last_day_of_month(any_day):
    # The day 28 exists in every month. 4 days later, it's always next month
    next_month = any_day.replace(day=28) + datetime.timedelta(days=4)
    # subtracting the number of the current day brings us back one month
    return next_month - datetime.timedelta(days=next_month.day)


def last_7_days(any_day):
	list_of_last_7_days = []
	for i in range(7):
		new_day = any_day - datetime.timedelta(days=i)
		new_day.replace(tzinfo=datetime.timezone.utc)
		list_of_last_7_days.append(new_day)
	return list_of_last_7_days

today = datetime.datetime.now()
yesterday = today - datetime.timedelta(days=1)

today.replace(tzinfo=datetime.timezone.utc)
yesterday.replace(tzinfo=datetime.timezone.utc)


args = sys.argv[1:]
if len(args) > 1:
	year = int(args[0])
	month = int(args[1])
	day = int(args[2])
	today = datetime.datetime(year, month, day).replace(tzinfo=datetime.timezone.utc)


default_color = "#BBBBBB"

color_lookup = [
	"#4477AA",
	"#CCBB44",
	"#AA3377",
	"#66CCEE",
	"#228833",
	"#EE0C77",
]




start_days_to_cache = last_7_days(yesterday)
end_days_to_cache = last_7_days(today)

DataController = CibicObjects.data_controller.DataController()
for idx, start_day in enumerate(start_days_to_cache):
	print('updating cache for ', start_day)
	end_day = end_days_to_cache[idx]
	DataController.Run(start=start_day, end=end_day, to_bin=True, path=cache_folder)
