import logging
from datetime import datetime
import os

def create_logger():
    logdir = os.path.join(os.path.expanduser('~'), 'reversilogs')
	logname = "reversi_{}.log".format(datetime.now().strftime('%Y-%m-%d_%H:%M:%S')) 
	logfile = os.path.join(logdir, logname)

	# See https://wingware.com/psupport/python-manual/2.3/lib/node304.html
	logger = logging.getLogger('reversi')
	hdlr = logging.FileHandler(logfile)
	# formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
	formatter = logging.Formatter('%(message)s')
	hdlr.setFormatter(formatter)
	logger.addHandler(hdlr) 
	logger.setLevel(logging.DEBUG)
	return logger
