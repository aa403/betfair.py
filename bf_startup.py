# -*- coding: utf-8 -*-
__author__ = 'Ammar Akhtar'

import os
import logging
import getpass
import re
import sys
import subprocess,json
from betfair import Betfair, constants as bf_c
from betfair.models import MarketFilter

def get_all_market_projections():
    return [x.name for x in bf_c.MarketProjection]


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

competitions = client.list_competitions(
    MarketFilter(event_ids=['2022802'])
    # MarketFilter(event_type_ids=[event_types[0].event_type.id], text_query='premier')
)

markets = client.list_market_catalogue(
    MarketFilter(event_type_ids=[event_types[0].event_type.id], competition_ids=['31']),
    max_results=20,
    market_projection=[
        'MARKET_DESCRIPTION',
        'RUNNER_METADATA',
        'RUNNER_DESCRIPTION',
        'MARKET_START_TIME',
    ]
    # market_projection=get_all_market_projections()
)

events = client.list_events(
    MarketFilter(event_type_ids=['1'], competition_ids=['31'] )
)

bf_results = [event_types,competitions,markets,events]

#
# for i in xrange(len(event_types)):
#     event_types[i] = event_types[i].serialize()
#
# for i in xrange(len(competitions)):
#     competitions[i] = competitions[i].serialize()
#
for i in xrange(len(markets)):
    markets[i] = markets[i].serialize()

event_types[0].__str__()

client.keep_alive()


print event_types