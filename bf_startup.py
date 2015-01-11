# -*- coding: utf-8 -*-
__author__ = 'Ammar Akhtar'

import os
import logging
import getpass
import re
import sys
import subprocess,json
from betfair import Betfair
from betfair.models import MarketFilter


# held in the class
# auth_logger = logging.getLogger('bf_login\t')
# keep_alive_logger = logging.getLogger('bf_keep_alive\t')

IDENTITY_URL = 'https://identitysso.betfair.com/api/'
API_URL = 'https://api.betfair.com/exchange/betting/json-rpc/v1/'

logging.basicConfig(level=logging.DEBUG)
run_logger = logging.getLogger('bf_startup')

username = sys.argv[1]
APP_KEY_DELAYED = 'VCfgMr8NqHwbSK74'
APP_KEY = 'z1O1dbO6cqxoFBhj'

try:
    if sys.argv[2] == '-f':
        app_key = APP_KEY
        run_logger.info('using fast key')
    else:
        app_key = APP_KEY_DELAYED
        run_logger.info('using delayed key')
except:
    app_key = APP_KEY_DELAYED
    run_logger.info('using delayed key')

client = Betfair(app_key)

client.interactive_login(username,getpass.getpass(prompt='password:\n'))

event_types = client.list_event_types(
    MarketFilter(text_query='soccer')
)

# competitions = client.list_competitions(
#     MarketFilter(competition_ids='1')
# )

print event_types

client.keep_alive()

event_types = client.list_event_types(
    MarketFilter(text_query='tennic')
)

print event_types