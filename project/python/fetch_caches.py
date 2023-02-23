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


today = datetime.datetime.today()

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


start = today - datetime.timedelta(days=today.weekday())
end = start + datetime.timedelta(days=6)

startTime = start.replace(tzinfo=datetime.timezone.utc)
endTime = end.replace(tzinfo=datetime.timezone.utc)


f'{startTime.strftime("%Y_%m_%d")}-{endTime.strftime("%Y_%m_%d")}.pickle'

DataController = CibicObjects.data_controller.DataController()
DataController.Run(start=startTime, end=endTime, to_bin=True, path=cache_folder)
