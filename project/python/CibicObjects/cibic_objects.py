from datetime import datetime, timezone
from dateutil import parser
import json
from typing import Type


import urllib

#import TDFunctions

class Ride:
	"""An object describing a ride in the CiBiC system.
	
	Args:
		raw_data (dict): a dict of data from database structures

	Attributes:
		raw_data (dict): a dict of data from database structures
		geo_JSON (dict): the geoJSON structure for the ride
		journaled_data (Reflection): the Reflection cibic object matched to this ride
		user_id (str): the userId of a cibic user
		ride_id (str): the id of this cibic ride
		flow_id (str): the id of the flow this ride is part of
		start_time (datetime): the time this ride started
		end_time (datetime): the time this ride ended
		role (str): the role of the use taking this ride.
	"""
	def __init__(self, raw_data:dict):
		self.raw_data: dict = raw_data
		self.geo_JSON: dict = raw_data
		self.journaled_data: 'Reflection' = None
		self.flow: 'Flow' = None
		self.user_id: str = raw_data['properties']['userId']
		self.ride_id: str = raw_data['properties']['rideId']
		self.flow_id: str = raw_data['properties']['flow']
		self.pod_id: str = raw_data['properties']['pod']
		self.flow_name: str = raw_data['properties']['flowName']
		self.pod_name: str = raw_data['properties']['podName']
		self.to_work: bool = raw_data['properties']['flowIsToWork']
		self.start_time: datetime = parser.parse(raw_data['properties']['startTime']).astimezone(tz=timezone.utc)
		self.end_time: datetime = parser.parse(raw_data['properties']['endTime']).astimezone(tz=timezone.utc)
		self.role: str = raw_data['properties']['role']
		self.region: str = raw_data['properties']['region']
		pass

	@property
	def Geo_JSON_Obj(self):
		"""`dict` containing the GeoJSON for the ride"""
		return self.geo_JSON

	@property
	def Geo_JSON_Path_Only_Obj(self):
		"""`dict` containing the GeoJSON for the path of the ride"""
		return next(feature for feature in self.geo_JSON['features'] if feature['geometry']['type'] =="LineString")

	@property
	def Geo_JSON_Path_Coords(self):
		"""`list` of coordinates and times for this ride"""
		return self.Geo_JSON_Path_Only_Obj['geometry']['coordinates']

	@property
	def Geo_JSON_String(self):
		"""`str` a stringified GeoJSON of the ride"""
		return json.dumps(self.geo_JSON)

	@property
	def Reflection_data(self):
		"""`Reflection` or `None` the matched reflection data for the ride"""
		return self.journaled_data

	@property
	def Flow_id(self):
		"""`str` the flow id for the ride"""
		return self.flow_id

	@property
	def Flow(self):
		"""`str` the flow for the ride"""
		return self.flow
	
	def __str__(self):
		return f"<Ride ride_id={self.ride_id} user_id={self.user_id} flow_id={self.flow_id} {'m' if self.journaled_data is not None else 'u'}>"

	def __repr__(self):
		return f"<Ride ride_id={self.ride_id} user_id={self.user_id} flow_id={self.flow_id} {'m' if self.journaled_data is not None else 'u'}>"

	def AddReflection(self, reflection: 'Reflection'):
		self.journaled_data = reflection

class Flow:
	'''An object describing a flow in the CiBiC system'''
	def __init__(self, flow_id:str):
		self.flow_id: str = flow_id
		self.name = None
		self.rides: RideList = RideList()
		self.flow_path = None
		self.all_paths = []
		self.meta: str = ""
		pass

	@property
	def Rides(self):
		return self.rides

	@property
	def Paths(self):
		return self.all_paths

	def AddRide(self, ride:Ride):
		self.rides.append(ride)
		self.flow_path = ride.Geo_JSON_Obj['properties']['flowPath']
		self.name = ride.Geo_JSON_Obj['properties']['flowName']
		self.all_paths.append( {"flowPath":ride.Geo_JSON_Obj['properties']['flowPath'], "flowJoinPoints":ride.Geo_JSON_Obj['properties']['flowJoinPoints'], "date": ride.start_time} )
		ride.flow = self


class Pod:
	'''An Object describing a pod in the CiBiC System'''
	def __init__(self, pod_id: str, pod_name: str):
		self.pod_id: str = pod_id
		self.pod_name: str = pod_name
		self.users = set()
		pass

	@property
	def Users(self):
		return self.users

	def AddUser(self, user: 'UserProfile'):
		self.users.add(user)
		pass

	# TODO: add Rides for pod

class Reflection:
	'''An object describing a journal/reflection in the CiBiC system'''
	def __init__(self, raw_data:any):
		self.user_id: str = raw_data['userId']
		self.timestamp: datetime = datetime.fromisoformat(raw_data['created']).replace(microsecond=0)
		self.ride: Ride = None
		self.role: str = raw_data['role']
		self.journal: list = raw_data['journal']
		self.answers: list = raw_data['answers']
		self.media: any = None
		if raw_data['media'] is not None:
			if len(raw_data['media']) > 0:
				tempMedia = []
				if type(raw_data['media']) == list:
					for m in raw_data['media']:
						media_path = 'https://lr0iuavzwl.execute-api.us-west-1.amazonaws.com/prod/get?password=pdJ647HDG4np93nHFxKpT2kT23wY&path=' + urllib.parse.quote(m, safe='')
						tempMedia.append(media_path)
				else:
					media_path = 'https://lr0iuavzwl.execute-api.us-west-1.amazonaws.com/prod/get?password=pdJ647HDG4np93nHFxKpT2kT23wY&path=' + urllib.parse.quote(raw_data['media'], safe='')
					tempMedia.append(media_path)
				self.media = tempMedia
		pass

	#def __str__(self):
	#	return TDFunctions.listToParString(self.answers)

	def __repr__(self):
		return f"<Reflection user_id={self.user_id} timestamp={self.timestamp} {'m' if self.ride is not None else 'u'}>"

class UserProfile:
	'''An object describing a user in the CiBiC system'''
	def __init__(self):
		self.user_id: str = ""
		self.user_data: dict = {}
		self.flows: set = set()
		self.Rides: RideList = RideList()
		self.Reflections: ReflectionList = ReflectionList()
		pass

	def __str__(self):
		return f"<UserProfile user_id={self.user_id} ri/re={len(self.Rides)}/{len(self.Reflections)} flows={len(self.flows)}>"

	def __repr__(self):
		return f"<UserProfile user_id={self.user_id} ri/re={len(self.Rides)}/{len(self.Reflections)} flows={len(self.flows)}>"

	def AddRide(self, ride:Ride):
		"""Adds a Ride / the Flow to the UserProfile"""
		self.flows.add(ride.flow_id)
		self.Rides.append(ride)
	
	def AddReflection(self, journal:Reflection):
		"""Adds a Reflection to the UserProfile"""
		self.Reflections.append(journal)
	
	def Match(self):
		# Sort reflections and rides by time
		self.Reflections.sort(key=lambda ReflectionObject: ReflectionObject.timestamp)
		self.Rides.sort(key=lambda RideObject: RideObject.start_time)

		# Create a shallow copy so we dont mess with our list of rides.
		rides = RideList(self.Rides.copy())

		# We will be popping off the top of the stack, reverse it so its aligned.
		rides.reverse()
		for index, reflection in enumerate(self.Reflections):
			# Assuming there is a ride assocaited with each reflection
			while len(rides) > 0:
				# pop a ride out from the stack
				ride = rides.pop()	
				# check if it could match
				if reflection.timestamp > ride.start_time:
					# this is a potential match...
					self.Reflections[index].ride = ride
					# print(f'c {reflection.timestamp} / {ride.start_time}')
					# continue for one more loop of the while to see if there are any closer rides.
				else: 
					# if ride.start_time is too high for reflection to be counted
					# add it back into the stack
					rides.append(ride)
					break

			# match the reflection back to the ride.
			if self.Reflections[index].ride is not None:
				self.Reflections[index].ride.AddReflection(self.Reflections[index])





class Live:
	'''An object describing a journal/live reflection in the CiBiC system'''
	def __init__(self, raw_data:any):
		self.profile: UserProfile = None
		self.data: any = {}
		self.timestamp: datetime = None
		pass


class RideList(list):
	def __init__(self, *args):
		list.__init__(self, *args)
		for ride in self:
			if not isinstance(ride, Ride):
				raise TypeError('Cannot add type '+type(ride).__name__+' to RideList. Element must be a Ride')
		self.sort(key=lambda ride: ride.start_time)

	def append(self, value):
		if not isinstance(value, Ride):
			raise TypeError('Cannot add type '+type(value).__name__+' to RideList. Element must be a Ride')
		else:
			super().append(value)

	def between(self, start: datetime, end: datetime):
		return RideList([r for r in self if r.start_time >= start and r.end_time <= end])

	def matched(self, isMatched=True):
		return RideList([r for r in self if not ( (r.journaled_data is not None) ^ isMatched)])

	@property
	def coordinate_width(self):
		return max([len(ride.Geo_JSON_Path_Coords) for ride in self])


class ReflectionList(list):
	def __init__(self, *args):
		list.__init__(self, *args)
		for reflection in self:
			if not isinstance(reflection, Reflection):
				raise TypeError('Cannot add type '+type(reflection).__name__+' to Reflection. Element must be a Reflection')
		self.sort(key=lambda reflection: reflection.timestamp)

	def append(self, value):
		if not isinstance(value, Reflection):
			raise TypeError('Cannot add type '+type(value).__name__+' to Reflection. Element must be a Reflection')
		else:
			super().append(value)

	def between(self, start: datetime, end: datetime):
		return ReflectionList([r for r in self if r.timestamp >= start and r.timestamp <= end])

	def matched(self, isMatched=True):
		return ReflectionList([r for r in self if not ( (r.ride is not None) ^ isMatched)])