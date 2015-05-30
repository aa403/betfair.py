__author__ = 'Ammar Akhtar'

import getpass
from . import datetime_tools
from .bot_methods import implied_percentage
from betfair import Betfair, constants as bf_c
from betfair.models import MarketFilter
from betfair.bf_logging import main_logger as bf_stream_logger
from time import sleep, time


class BfDataStream(object):
    LONG_SHORT_INTERVAL_SCALE = 10
    SHORT_INTERVAL = 5
    LONG_INTERVAL = LONG_SHORT_INTERVAL_SCALE * SHORT_INTERVAL

    def __init__(self, **kwargs):
        """

        :param kwargs: app_key, [market_id_list]
        :return: initialises connection object to betfair API
        """
        app_key = kwargs.get('app_key', None)
        market_id_list = kwargs.get('market_id_list', [])

        if app_key is not None and len(market_id_list) > 0:
            self.client = Betfair(app_key)
            self.market_id_list = market_id_list
            self.latest_odds = {}
            self.last_updated = int(time())
            # self.odds_have_indeed_changed = False
            bf_stream_logger.info('Data stream created')

        elif app_key is None:
            bf_stream_logger.exception('No app_key provided')
            raise ValueError

        else:
            bf_stream_logger.exception('No market_id_list provided')
            raise ValueError

    def login(self, **kwargs):
        self.client.login(kwargs.get('username', ''), kwargs.get('password', ''))

    def fetch_market_book(self):
        sleep_interval = self.SHORT_INTERVAL
        ctr = 1

        while True: # loop forever until an outside force stops this.
            if ctr == 10:
                offer_option = 'EX_ALL_OFFERS'
                ctr=1
            else:
                offer_option = 'EX_BEST_OFFERS'

            # get data
            latest_market_book = self.client.list_market_book(
                self.market_id_list,
                price_projection={
                    'priceData': [offer_option],
                    'virtualise': False},
            )

            # extract odds from market_book_latest
            extracted_odds = self.extract_prices(latest_market_book)

            # todo: this should be per runner, per market, and not for the whole list,
            # so some iterator should be used with extracted_odds
            self.check_latest_prices(extracted_odds)

            # if self.odds_have_indeed_changed:
            #     #todo - use iterator on extracted_odds
            #     self.write_new_odds(extracted_odds)
            ctr+=1

            bf_stream_logger.debug('sleeping for %s' % (sleep_interval))
            sleep(sleep_interval)

    def extract_prices(self, market_book_latest, **kwargs):

        call_res = {}

        for x in market_book_latest:
            mkt_res = {}

            for rd in x.runners.data:
                rd_res = {}

                back_list = rd.ex.available_to_back.data

                for i in xrange(len(back_list)):
                    rd_res.update({'back_price_' + str(i): back_list[i].price})
                    rd_res.update({'back_vol_' + str(i): back_list[i].size})

                lay_list = rd.ex.available_to_lay.data

                for i in xrange(len(lay_list)):
                    rd_res.update({'lay_price_' + str(i): lay_list[i].price})
                    rd_res.update({'lay_vol_' + str(i): lay_list[i].size})

                rd_res.update({'last_price_traded': rd.last_price_traded})

                mkt_res.update({rd.selection_id: rd_res})

            call_res.update({x.market_id: mkt_res})

        return call_res

    def write_new_odds(self, **odds):
        bf_stream_logger.debug('moved to write new odds')

        # todo: psycopg2 or pg wrap needs to be set up

        pass

    def check_latest_prices(self, odds_received):

        for market in odds_received:

            # ensure there is a key in place for this market
            if not self.latest_odds.get(market, None):
                self.latest_odds.update({market: {}})

            # then iterate thru the market_price response
            for runner in odds_received[market]:

                # as above, ensure that a key is in place
                if not self.latest_odds[market].get(runner, None):
                    self.latest_odds[market].update({runner: {}})

                runner_price_data = odds_received[market][runner]

                # straight forward dict comparison
                if runner_price_data != self.latest_odds[market][runner]:
                    bf_stream_logger.debug('new data received for market %s, runner %s' % (market, runner))

                    # db commit
                    self.write_new_odds(**runner_price_data)

                    # update in-mem odds
                    self.latest_odds[market][runner] = runner_price_data

                else:
                    bf_stream_logger.debug('data not changed for market %s, runner %s' % (market, runner))

        pass
