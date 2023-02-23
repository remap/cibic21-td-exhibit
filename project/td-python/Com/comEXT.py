"""
SudoMagic | sudomagic.com
Authors | Matthew Ragan, Ian Shelanskey
Contact | contact@sudomagic.com
"""

import logging
import Lookup

class Com:
    """Communication

    The Com class is responsible for...
    """

    def __init__(self, myOp):
        self.My_op = myOp
        logging.info(f"COM 📠 | Output Init")

    def Touch_start(self):
        logging.info(f"COM 📠 | Touch_start")
