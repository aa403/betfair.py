# -*- coding: utf-8 -*-
__author__ = 'ammarorama'

# print sys.argv[1]
# client = bf('VCfgMr8NqHwbSK74', ('certs/betfair.crt','certs/betfair.key'))
# client.login('ammarorama',sys.argv[1])

#
import logging
from betfair import bf_logging
from betfair import Betfair, constants as bf_c
from betfair.models import MarketFilter
from bot.bot_methods import implied_percentage

bf_logging.main_logger.setLevel(logging.INFO)


APP_KEY = {'DELAYED':'VCfgMr8NqHwbSK74', 'LIVE':'z1O1dbO6cqxoFBhj'}
CERTS = ('certs/betfair.crt', 'certs/betfair.key')

client = Betfair('z1O1dbO6cqxoFBhj',CERTS)
# client = Betfair('VCfgMr8NqHwbSK74', CERTS)
client.login('ammarorama', 'bonzer2K')
# create a cached timestamp, or something


def get_all_market_projections():
    return [x.name for x in bf_c.MarketProjection]


event_types = client.list_event_types(
    MarketFilter(text_query='soccer')
)

competitions = client.list_competitions(
    MarketFilter(text_query='barclays',)
    # MarketFilter(event_ids=['2022802'])
    # MarketFilter(event_type_ids=[event_types[0].event_type.id], text_query='premier')
)

markets = client.list_market_catalogue(
    MarketFilter(text_query='winner', competition_ids=['31'], event_ids=['2022802']),
        # event_type_ids=[event_types[0].event_type.id], competition_ids=['31']),
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
    MarketFilter(event_type_ids=['1'], text_query='barclays') #competition_ids=['31'] )
)


xx = client.list_market_book([markets[0].market_id],
                             price_projection={
                                 'priceData':['EX_BEST_OFFERS'],
                                 # 'exBestOffersOverrides':{"bestPricesDepth":3},
                                 'virtualise':False},
)

# 1 in 10 should be this
xxx = client.list_market_book([markets[0].market_id],
                             price_projection={
                                 'priceData':['EX_ALL_OFFERS'],
                                 'virtualise':False},
)

# if change in BBO, then call this to get latest traded volume and change to executions
yy = client.list_market_book([markets[0].market_id],
                             price_projection={
                                 'priceData':['EX_TRADED'],
                                 # 'exBestOffersOverrides':{"bestPricesDepth":2},
                                 'virtualise':False},
                             match_projection='ROLLED_UP_BY_AVG_PRICE',
)


# if bet is placed, then make call for latest orders
zz = client.list_market_book([markets[0].market_id],
                             order_projection='EXECUTABLE',
)

yy[0].serialize()


# todo - needs to be called every 12 hours; use Sched
# client.session.cookies._now + 3600*4
client.keep_alive()

