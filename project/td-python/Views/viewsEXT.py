"""
SudoMagic | sudomagic.com
Authors | Matthew Ragan, Ian Shelanskey
Contact | contact@sudomagic.com
"""

import logging
import Lookup

class Views:
    """Views Class
    """

    def __init__(self, myOp):
        self.My_op = myOp
        logging.info(f"VIEWS 🪟 | Views Init from {myOp}")

    def Touch_start(self):
        logging.info(f"VIEWS 🪟 | Touch_start")