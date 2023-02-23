from datetime import datetime, timezone, tzinfo
import time
import requests
import cibic_objects
import pickle
import os
import aws_client


class DataController:
	def __init__(self):
		self.fetch_start = 0
		self.fetch_end = 0

		self.raw_rides = []
		self.raw_journals = []
		self.Rides = []
		self.Journals = []

		self._User_Map: dict[str, cibic_objects.UserProfile]= {}
		self._User_IDs:	list[str] = [] 
		self._Ride_IDs:	list[str] = [] 
		self._Flow_Map:	dict[str, cibic_objects.Flow] = {}
		self._Flow_IDs:	list[str] = []
		self._Pod_Map:	dict[str, cibic_objects.Pod] = {}
		self._Pod_IDs:	list[str] = []
		return

	@property
	def User_Map(self):
		"""Provides a fast lookup using User_ID as the key"""
		return self._User_Map

	@property
	def Flow_Map(self):
		"""Provides a fast lookup using Flow_ID as the key"""
		return self._Flow_Map
	
	@property
	def Pod_Map(self):
		"""Provides a fast lookup using Pod_ID as the key"""
		return self._Pod_Map

	@property
	def User_IDs(self):
		"""Provides a list of User_IDs loaded into the system"""
		return self._User_IDs

	@property
	def Ride_IDs(self):
		"""Provides a list of Ride_IDs loaded into the system"""
		return self._Ride_IDs

	@property
	def Flow_IDs(self):
		"""Provides a list of Flow_IDs loaded into the system"""
		return self._Flow_IDs

	@property
	def Pod_IDs(self):
		"""Provides a list of Pod_IDs loaded into the system"""
		return self._Pod_IDs

	
	def Get_Rides_From_Flow_IDs(self, listOfIds: list[str]) -> cibic_objects.RideList:
		"""Retrieves a `<cibic_objects.RideList>` of rides from a list of `str` Flow_IDs
		
		Args:
			`listOfIds` (`list[str]`): a list of ride_ids as str
		Returns 
		 	`RideList`: a list of Rides"""
		selected_flows = [self._Flow_Map[flow_id].Rides for flow_id in listOfIds] 
		return cibic_objects.RideList( sum(selected_flows, []) )
	
	def Get_Reflections_From_Flow_IDs(self, listOfIds: list[str]) -> cibic_objects.ReflectionList:
		"""Retrieves a `<cibic_objects.ReflectionList>` of Reflections from a list of `str` Flow_IDs
		
		Args:
			listOfIds (`list[str]`): a list of Flow_IDs as `str`
		Returns 
		 	`ReflectionList`: a list of Reflections"""
		selected_flows = [self._Flow_Map[flow_id].Rides.matched() for flow_id in listOfIds] 
		return cibic_objects.ReflectionList( [r.Reflection for r in sum(selected_flows, [])] )


	def Get_Rides_From_Ride_IDs(self, listOfIds: list[str]) -> cibic_objects.RideList:
		"""Retrieves a `<cibic_objects.RideList>` of Rides from a list of `str` Ride_IDs
		
		Args:
			listOfIds (`list[str]`): a list of Ride_IDs as `str`
		Returns 
		 	`RideList`: a list of Rides"""
		selected_rides = [self._Ride_Map[ride_id] for ride_id in listOfIds] 
		return cibic_objects.RideList( selected_rides )

	def Get_Reflections_From_Ride_IDs(self, listOfIds: list[str]) -> cibic_objects.ReflectionList:
		"""Retrieves a `<cibic_objects.ReflectionList>` of Reflections from a list of `str` Ride_IDs
		
		Args:
			listOfIds (`list[str]`): a list of Ride_IDs as `str`
		Returns 
		 	`ReflectionList`: a list of Reflections"""
		selected_rides = cibic_objects.RideList( [self._Ride_Map[ride_id] for ride_id in listOfIds] )
		return cibic_objects.ReflectionList([r.Reflection for r in selected_rides.matched()])


	def Get_Rides_From_User_IDs(self, listOfIds: list[str]) -> cibic_objects.RideList:
		"""Retrieves a `<cibic_objects.RideList>` of Rides from a list of `str` User_IDs
		
		Args:
			listOfIds (`list[str]`): a list of User_IDs as `str`
		Returns 
		 	`RideList`: a list of Rides"""
		selected_user_rides = [self._User_Map[user_id].Rides for user_id in listOfIds] 
		return cibic_objects.RideList( sum(selected_user_rides, []) )

	def Get_Reflections_From_User_IDs(self, listOfIds: list[str]) -> cibic_objects.ReflectionList:
		"""Retrieves a `<cibic_objects.ReflectionList>` of Reflections from a list of `str` User_IDs
		
		Args:
			listOfIds (`list[str]`): a list of User_IDs as `str`
		Returns 
		 	`ReflectionList`: a list of Reflections"""
		selected_user_reflections = [self._User_Map[user_id].Reflections for user_id in listOfIds] 
		return cibic_objects.ReflectionList( sum(selected_user_reflections, []) )

	def Get_Rides_From_Time_Range(self, start: datetime, end: datetime) -> cibic_objects.RideList:
		"""Retrieves a `<cibic_objects.RideList>` of Rides between a start and end time range
		
		Args:
			start (`datetime`): a timezone aware datetime object for the start of the time range
			end (`datetime`): a timezone aware datetime object for the end of the time range
		Returns 
		 	`RideList`: a list of Rides"""
		selected_rides = cibic_objects.RideList( self.Rides ).between(start, end)
		return selected_rides

	def Get_Reflections_From_Time_Range(self, start: datetime, end: datetime) -> cibic_objects.ReflectionList:
		"""Retrieves a `<cibic_objects.ReflectionList>` of Reflections between a start and end time range
		
		Args:
			start (`datetime`): a timezone aware datetime object for the start of the time range
			end (`datetime`): a timezone aware datetime object for the end of the time range
		Returns 
		 	`ReflectionList`: a list of Reflections"""
		selected_reflections = cibic_objects.ReflectionList( self.Journals ).between(start, end)
		return selected_reflections


	# REMOVE: I dont think this is going to be used
	def _FetchUserProfile(self, user_id:str) -> any:
		# form query using util function in dynamoDB module
		# execute query .. this may hang while we wait.
		return aws_client.GetOneUser(user_id)

	def _FetchRides(self, start:datetime, end:datetime, ids_only:bool=False):
		"""Fetches Rides from UCLA Ride Database endpoint"""
		# create URL for fetch
		url = "https://ceagzl0sq2.execute-api.us-west-1.amazonaws.com/prod/ride/query?"
		url = url + "startTime=" + start.astimezone(tz=timezone.utc).replace(tzinfo=None).isoformat()
		url = url + "&endTime="  + end.astimezone(tz=timezone.utc).replace(tzinfo=None).isoformat()
		if ids_only:
			url = url + "&idsOnly=1"
		return requests.get(url, headers={"x-api-key":"Hu1h6vTxvh5uMGJ7K5j5g3Sxm3oh9klp3gWB4PYA"}).json()

	def _FetchUsersJournalsWithDateTime(self, user_id:str, start:datetime, end:datetime):
		"""Fetches a users Journals from DynamoDB Tables"""
		# form query using util function in dynamoDB module
		# execute query .. this may hang while we wait.
		return aws_client.GetUserReflectionsWithDatetime(user_id, start, end)

	
	def _FetchJournalsWithDateTime(self, start:datetime, end:datetime):
		"""Fetches a users Journals from DynamoDB Tables"""
		# form query using util function in dynamoDB module
		# execute query .. this may hang while we wait.
		return aws_client.GetReflectionsWithDatetime(start, end)

	def _Fetch(self, start:datetime, end:datetime):
		"""Fetches General Visualization data"""
		self.fetch_start = time.time()

		# Fetch Rides from API endpoint
		self.raw_rides = self._FetchRides(start, end)

		# Fetch Rides from DB client
		self.raw_journals = self._FetchJournalsWithDateTime(start, end)

		self.fetch_end = time.time()
		pass
		

	def ProcessData(self, ride_data:list, journal_data:list) -> None:
		# create temp hash map for assigning rides and journals to users
		user_map = {}

		# Create Ride objects out of ride data. This lets us have a nice interface with TD
		self.Rides = [cibic_objects.Ride(ride_item) for ride_item in ride_data]

		# Pre-sort rides by start time
		self.Rides.sort(key=lambda RideObject: RideObject.start_time)

		self._Ride_IDs = [ ride.ride_id for ride in self.Rides ]
		self._Ride_Map = { ride.ride_id: ride for ride in self.Rides }
		
		for ride in self.Rides:
			# Check if the user_map already has this user in it.
			if ride.user_id in user_map:
				# add the ride using the available interface
				user_map[ride.user_id].AddRide(ride)
			else:
				# Create UserProfile
				user_map[ride.user_id] = cibic_objects.UserProfile()
				user_map[ride.user_id].user_id = ride.user_id
				# Add Ride with available interface
				user_map[ride.user_id].AddRide(ride)
		
		# Create Journals objects out of Journal data. This lets us have a nice interface with TD
		self.Journals = [cibic_objects.Reflection(journal_item) for journal_item in journal_data]
		for journal in self.Journals:
			# Check if the user_map already has this user in it.
			if journal.user_id in user_map:
				# add the journal using the available interface
				user_map[journal.user_id].AddReflection(journal)
			else:
				# Create UserProfile
				user_map[journal.user_id] = cibic_objects.UserProfile()
				user_map[journal.user_id].user_id = journal.user_id
				# Add Journal with available interface
				user_map[journal.user_id].AddReflection(journal)
		
		# Make user_map public attribute.
		self._User_Map = user_map
		self._User_IDs = list( self._User_Map.keys() )

		flow_map = {}
		# Create Flow Map
		for ride in self.Rides:
			if ride.flow_id in flow_map:
				flow_map[ride.flow_id].AddRide(ride)
			else: 
				flow_map[ride.flow_id] = cibic_objects.Flow(ride.flow_id)
				flow_map[ride.flow_id].AddRide(ride)
		
		self._Flow_Map = flow_map
		self._Flow_IDs = list( self._Flow_Map.keys() )

		pod_map = {}
		for ride in self.Rides:
			if ride.pod_id in pod_map:
				if ride.user_id in user_map:
					pod_map[ride.pod_id].AddUser(user_map[ride.user_id])
			else:
				pod_map[ride.pod_id] = cibic_objects.Pod(ride.pod_id, ride.pod_name)
				if ride.user_id in user_map:
					pod_map[ride.pod_id].AddUser(user_map[ride.user_id])

		self._Pod_Map = pod_map
		self._Pod_IDs = list( self._Pod_Map.keys() )
		
		return 

	def Run(self, start=datetime(2022, 6, 1), end=datetime(2022, 8, 24), to_bin=False):

		self._Fetch(start, end)
		self.ProcessData(self.raw_rides, self.raw_journals)
		for k, v in self._User_Map.items():
			v.Match()
		if to_bin:
			self.Dump_to_bin(f'exported-data/pickle_jar/{start.strftime("%Y_%m_%d")}-{end.strftime("%Y_%m_%d")}.pickle')
		return

	def Dump_to_bin(self, path):
		structure = {
			"raw_rides": self.raw_rides,
			"raw_journals": self.raw_journals,
		}
		with open(path, 'wb') as f:
			pickle.dump(structure, f)

	def Load_from_bin(self, path):
		with open(path, 'rb') as f:
			data = pickle.load(f)
			return data

	def Load_from_cache(self, directory):
		cache = []
		for filename in os.listdir(directory):
			cache.append( self.Load_from_bin(os.path.join(directory, filename)) )
		
		print(f"found {len(cache)} cached files")
		
		combined = {"raw_rides":[], "raw_journals":[]}
		for cache_selected in cache:
			combined["raw_rides"] = combined["raw_rides"] + cache_selected["raw_rides"]
			combined["raw_journals"] = combined["raw_journals"] + cache_selected["raw_journals"]
		
		self.raw_rides = combined['raw_rides']
		self.raw_journals = combined['raw_journals']
		self.ProcessData(self.raw_rides, self.raw_journals)
		for k, v in self._User_Map.items():
			v.Match()
		return 
