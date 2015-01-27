__author__ = 'Ammar Akhtar'

import getpass
from . import datetime_tools
from .bot_methods import implied_percentage
from betfair import Betfair, constants as bf_c
from betfair.models import MarketFilter
from betfair.bf_logging import bf_stream_logger
from time import sleep, time




class BfDataStream(object):

    def __init__(self, **kwargs):
        """

        :param kwargs: app_key, [market_id_list]
        :return: initialises connection object to betfair API
        """
        app_key = kwargs.get('app_key',None)
        market_id_list = kwargs.get('market_id_list',[])

        if app_key is not None and len(market_id_list) > 0:
            self.client = Betfair(app_key)
            self.market_id_list = market_id_list
            self.latest_odds = {}
            self.last_updated = datetime_tools.epoch_to_datetime(time())
            self.odds_have_indeed_changed = False
            bf_stream_logger.info('Data stream created')
        elif app_key is None:
            bf_stream_logger.error('No app_key provided')
        else:
            bf_stream_logger.error('No market_id_list provided')



    def interactive_login(self):
        #todo: change to cert method, or create a separate mechanism for interactive login
        self.client.interactive_login(raw_input('username:'), getpass.getpass(prompt='password:\n'))

    def fetch_market_book(self, sleep_interval = 5):

        while True:
            # get data
            latest_market_book = self.client.list_market_book(self.market_id_list,
                                           price_projection={'priceData':['EX_BEST_OFFERS','EX_TRADED'],
                                          'exBestOffersOverrides':{"bestPricesDepth":5},
                                          'virtualise':False},
                        )

            # extract odds from market_book_latest
            extracted_odds = self.extract_prices(latest_market_book)

            #todo: this should be per runner, per market, and not for the whole list,
            # so some iterator should be used with extracted_odds
            self.check_odds_have_changed(extracted_odds)

            if self.odds_have_indeed_changed:
                #todo - use iterator on extracted_odds
                self.write_new_odds(extracted_odds)



            sleep(sleep_interval)

    def extract_prices(self, market_book_latest, **kwargs):

        call_res = {}
        for x in market_book_latest:
            mkt_res = {}
            for rd in x.runners.data:
                rd_res = {}

                back_list = rd.ex.available_to_back.data

                for i in xrange(len(back_list)):
                    rd_res.update({'back_price_'+str(i):back_list[i].price})
                    rd_res.update({'back_vol_'+str(i):back_list[i].size})

                lay_list = rd.ex.available_to_lay.data
                for i in xrange(len(lay_list)):
                    rd_res.update({'lay_price_'+str(i):lay_list[i].price})
                    rd_res.update({'lay_vol_'+str(i):lay_list[i].size})

                rd_res.update({'last_price_traded':rd.last_price_traded})

                mkt_res.update({rd.selection_id:rd_res})

            call_res.update({x.market_id:mkt_res})

        return call_res


    def check_odds_have_changed(self, extracted_odds):

        if (self.latest_odds == extracted_odds): # todo, improved check needed
            self.odds_have_indeed_changed = True
            self.latest_odds = extracted_odds
            bf_stream_logger.debug('latest odds have indeed changed')
        else:
            bf_stream_logger.debug('odds have not changed')
            pass

    def write_new_odds(self, **odds):
        bf_stream_logger.debug('moved to write new odds')
        pass