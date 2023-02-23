"""
SudoMagic | sudomagic.com
Authors | Matthew Ragan, Ian Shelanskey
Contact | contact@sudomagic.com
"""

import logging
import Lookup

import CibicObjects

class Data(CibicObjects.data_controller.DataController):
	"""Data

	The Data class is responsible for...
	"""
	def __init__(self, myOp):
		super().__init__()
		self.My_op = myOp
		logging.info(f'DATA 🧮 | Data Init from {myOp}')

	def Touch_start(self):
		self.My_op.unstore("*")
		self.Read_from_caches()
		logging.info(f'DATA 🧮 | Touch_start()')

	def Read_from_caches(self):
		cache_directory = ipar.Settings.Cachedirectory.eval()

		if cache_directory != "":
			# A cache directory exists

			self.Load_from_cache(cache_directory)
			Lookup.DATA.store("User_Map", self.User_Map)
			Lookup.DATA.store("Flow_Map", self.Flow_Map)
			Lookup.DATA.store("Pod_Map", self.Pod_Map)
			Lookup.DATA.store("User_IDs", self.User_IDs)
			Lookup.DATA.store("Ride_IDs", self.Ride_IDs)
			Lookup.DATA.store("Flow_IDs", self.Flow_IDs)
			Lookup.DATA.store("Pod_IDs", self.Pod_IDs)



	
