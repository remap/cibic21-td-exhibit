# me - this DAT
# 
# frame - the current frame
# state - True if the timeline is paused
# 
# Make sure the corresponding toggle is enabled in the Execute DAT.

import sys
import logging

def onStart():
	check_deps()
	op.Log.Logger.info('TouchDesigner onStart')
	if var('DEV').upper() == "FALSE":
		op.PROJECT.Touch_start()
		return 
	op.PROJECT.Touch_start_dev()
	return

def onCreate():
	return

def onExit():
	return

def onFrameStart(frame):
	return

def onFrameEnd(frame):
	return

def onPlayStateChange(state):
	return

def onDeviceChange():
	return

def onProjectPreSave():
	return

def onProjectPostSave():
	return


def check_deps():
	python_libs_path = f"{me.var('PUBLIC')}\\python-libs"
	if python_libs_path not in sys.path:
		sys.path.append(python_libs_path)
	else:
		pass
	
	#sanity check for python libs
	logging.info("- - - - - 🐍 PYTHON PATHS 🐍 - - - - -")
	
	for each in sys.path:
		logging.info(f"PYTHON PATH | {each}")
	
	logging.info("- - - - - 🐍 PYTHON PATHS 🐍 - - - - -")
