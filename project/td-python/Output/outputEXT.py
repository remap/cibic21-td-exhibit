"""
SudoMagic | sudomagic.com
Authors | Matthew Ragan, Ian Shelanskey
Contact | contact@sudomagic.com
"""

import logging
import Lookup

class Output:
	"""Output

	The Output class is responsible for...
	"""

	def __init__(self, myOp):
		self.My_op = myOp
		logging.info(f"OUTPUT 💠 | Output Init")

	def Touch_start(self):
		logging.info(f"OUTPUT 💠 | Touch_start()")