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
from bot.bot_methods import implied_percentage
from betfair.bf_logging import run_logger
from time import sleep

def wrapper(func, *args, **kwargs):
    def wrapped():
        return func(*args, **kwargs)
    return wrapped


a = {
    'back':2,
    'lay':2.1625,
    'layd':2.1625234,
    'layda':2.1622355,
    'laydh':2.1626585,
    'layh':2.1634525,
    'layj':2.1623455,
    'layc':2.1623455,
    'fail 1':'2',
    'fail 2':'{}'
}

import timeit
wrapped = wrapper(implied_percentage,**a)

# print timeit.timeit(wrapped, number=10000), timeit.timeit(wrapped, number=100000)




def costly_func(lst):
    return map(lambda x: x^2, lst)

print costly_func([2,5,7])


def get_all_market_projections():
    return [x.name for x in bf_c.MarketProjection]


# held in the class
# auth_logger = logging.getLogger('bf_login\t')
# keep_alive_logger = logging.getLogger('bf_keep_alive\t')

IDENTITY_URL = 'https://identitysso.betfair.com/api/'
API_URL = 'https://api.betfair.com/exchange/betting/json-rpc/v1/'

# logging.basicConfig(level=logging.INFO)
# run_logger = logging.getLogger('bf_startup')

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
    max_results=50,
    market_projection=[
        'COMPETITION',
        'EVENT',
        'EVENT_TYPE',
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

xx = client.list_market_book([markets[9].market_id,markets[33].market_id,markets[40].market_id,markets[35].market_id],
                        price_projection={'priceData':['EX_BEST_OFFERS','EX_TRADED'],
                                          'exBestOffersOverrides':{"bestPricesDepth":4},
                                          'virtualise':False},
                        # order_projection='ALL',
                        # match_projection='ROLLED_UP_BY_PRICE'

)

for i in xrange(len(xx)):
    xx[i] = xx[i].serialize()

event_types[0].__str__()

client.keep_alive()


print event_types

#
# {"priceProjection":{"exBestOffersOverrides":{"bestPricesDepth":1},
#                     "priceData":["EX_BEST_OFFERS"],"virtualise":false},
#  "matchProjection":"ROLLED_UP_BY_AVG_PRICE","orderProject
# ion":"ALL","marketIds":["1.114267385"]}



ids = [markets[9].market_id,markets[33].market_id,markets[40].market_id,markets[35].market_id]

while True:
    resp = client.list_market_book(ids,
        price_projection={'priceData':['EX_BEST_OFFERS','EX_TRADED'],
                                          'exBestOffersOverrides':{"bestPricesDepth":4},
                                          'virtualise':False},
                        # order_projection='ALL',
                        # match_projection='ROLLED_UP_BY_PRICE'
                        )

    print resp[0]
    sleep(1)
