# -*- coding: utf-8 -*-
__author__ = 'Ammar Akhtar'

"""
simple logging for betfair.py

heavily inspired by
	https://docs.python.org/2/howto/logging-cookbook.html,
	http://pymotw.com/2/logging/

"""


import logging
import logging.handlers

LOG_FILENAME = 'logs/logs.out'

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name) - 12s %(levelname) - 8s %(message)s',
                    datefmt='%d-%m %H:%M:%S',
                    # filename=LOG_FILENAME,
                    # filemode='a')
					)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')


# define file outputs
fh = logging.handlers.RotatingFileHandler(LOG_FILENAME, maxBytes=200000, backupCount=5)
fh.setFormatter(formatter)
# fh.setLevel(logging.DEBUG)

# define console outputs
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
# ch.setFormatter(formatter)

logging.getLogger('').addHandler(fh)
# logging.getLogger('').addHandler(ch)

# create loggers
bf_logger = logging.getLogger('betfair.Betfair')
# bf_logger.addHandler(fh)
# bf_logger.addHandler(ch)