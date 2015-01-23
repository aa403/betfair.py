# -*- coding: utf-8 -*-

import os
import subprocess
import json
import requests
import itertools
from six.moves import http_client as httplib
from six.moves import urllib_parse as urllib

from . import utils
from . import models
from . import exceptions
from . import bf_logging


IDENTITY_URL = 'https://identitysso.betfair.com/api/'
API_URL = 'https://api.betfair.com/exchange/betting/json-rpc/v1/'


class Betfair(object):
    """Betfair API client.

    :param str app_key: Optional application identifier
    :param str cert_file: Path to self-signed SSL certificate file(s); may be
        a *.pem file or a tuple of (*.crt, *.key) files
    :param str content_type: Response type

    """
    def __init__(self, app_key, cert_file=None, content_type='application/json'):
        self.app_key = app_key
        self.cert_file = cert_file
        self.content_type = content_type
        self.session = requests.Session()
        self.session_token = None

        # used for the interactive login method
        self.keys = {}
        self.login_is_interactive = False

    @property
    def headers(self):
        return {
            'X-Application': self.app_key,
            'X-Authentication': self.session_token,
            'Content-Type': self.content_type,
            'Accept': 'application/json',
        }

    def make_auth_request(self, method):
        response = self.session.post(
            os.path.join(IDENTITY_URL, method),
            headers=self.headers,
        )
        utils.check_status_code(response)
        data = response.json()
        if data.get('status') != 'SUCCESS':
            raise exceptions.BetfairAuthError(response, data)

    def make_api_request(self, method, params, codes=None, model=None):
        payload = utils.make_payload(method, params)
        bf_logging.bf_logger.debug('make_api_request:\t%s\t%s'%(method,payload))
        response = self.session.post(
            API_URL,
            data=json.dumps(payload),
            headers=self.headers,
        )
        utils.check_status_code(response, codes=codes)
        result = utils.result_or_error(response)
        bf_logging.bf_logger.debug('completed make_api_request:\t%-10s ... '%(result))
        return utils.process_result(result, model)

    # Authentication methods

    def login(self, username, password):
        """Log in to Betfair. Sets `session_token` if successful.

        :param str username: Username
        :param str password: Password
        :raises: BetfairLoginError

        """
        response = self.session.post(
            os.path.join(IDENTITY_URL, 'certlogin'),
            cert=self.cert_file,
            data=urllib.urlencode({
                'username': username,
                'password': password,
            }),
            headers={
                'X-Application': self.app_key,
                'Content-Type': 'application/x-www-form-urlencoded',
            },
        )
        utils.check_status_code(response, [httplib.OK])
        data = response.json()
        if data.get('loginStatus') != 'SUCCESS':
            raise exceptions.BetfairLoginError(response, data)
        self.session_token = data['sessionToken']

    def interactive_login(self, username, password):
        """Log in to Betfair using interactive API endpoint.
        Sets `session_token` if successful.

        :param str username: Username
        :param str password: Password
        :raises: BetfairInteractiveLoginError

        """
        bf_logging.bf_logger.info('starting interactive login')
        call_bf_tok = subprocess.Popen(['curl',
            '-k','-i',
            '-H', "Accept: application/json",
            '-H', "X-Application: %s" % self.app_key,
            '-X','POST',
            '-d','username=%s&password=%s'%(username,password),
            os.path.join(IDENTITY_URL, 'login')],
        stdout=subprocess.PIPE,
        )

        bf_tok_value = json.loads(call_bf_tok.communicate()[0].split('\n')[-1])
        bf_logging.bf_logger.info('login call returned status:\t%s' % bf_tok_value['status'])

        if bf_tok_value['status'] not in ['FAIL', 'LOGIN_RESTRICTED']:
            self.session_token = str(bf_tok_value['token'])

            # bf_logging.bf_logger.info('token:\t%s' % self.session_token)

            #todo: start a timer to call keep_alive
            self.login_is_interactive = True
            self.keys.update({'username':username,'password':password})

        else:
            bf_logging.bf_logger.error('login failed with status:\t%s' % bf_tok_value['status'])
            # login_error = bf_tok_value['error']
            # exceptions.auth_logger.error('error message:\t%s' % login_error)
            raise exceptions.BetfairInteractiveLoginError(bf_tok_value)


    @utils.requires_login
    def keep_alive(self):
        """Reset session timeout.

        :raises: BetfairAuthError

        """
        if self.login_is_interactive is True:
            bf_logging.bf_logger.info('doing interactive keep alive')
            keep_alive = subprocess.Popen(['curl', '-k', '-i', '-H', "Accept: application/json",
                    '-H', "X-Authentication: %s" % self.session_token,
                    '-H', "X-Application: %s" % self.app_key,
                    '-X', 'POST',
                    '-d','username=%s&password=%s'%(self.keys['username'],self.keys['password']),
                    os.path.join(IDENTITY_URL, 'keepAlive')],
                stdout=subprocess.PIPE,
                )

            keep_alive_value = json.loads(keep_alive.communicate()[0].split('\n')[-1])

            keep_alive_status = keep_alive_value['status']

            if keep_alive_status in ['SUCCESS']:
                token_match = str(keep_alive_value['token']) == self.session_token

                if token_match is False: #something fishy going on ...
                    bf_logging.bf_logger.error('Keep_alive succeeded but tokens do not match')
                    bf_logging.bf_logger.error('original token:\t %s' % self.session_token)
                    bf_logging.bf_logger.error('new token:\t %s' % str(keep_alive_value['token']))
                    self.logout()

                else: # all is well
                    bf_logging.bf_logger.info('keep_alive succeeded')
                    # bf_logging.bf_logger.info(keep_alive_value)
                    #todo: add some call to reset keep alive clock

            else: # keep_alive fails
                bf_logging.bf_logger.error('keep_alive call fails with error message:\t%s' % keep_alive_value)
                self.logout()
                raise exceptions.BetfairInteractiveLoginError(keep_alive_value)

        else:
            self.make_auth_request('keepAlive')

    @utils.requires_login
    def logout(self):
        """Log out and clear `session_token`.

        :raises: BetfairAuthError

        """
        self.make_auth_request('logout')
        self.keys = {}
        self.session_token = None
        self.login_is_interactive = False

    # Bet query methods

    @utils.requires_login
    def list_event_types(self, filter, locale=None):
        """

        returns a list of event_type based on the applied market filter

        :param MarketFilter filter:
        :param str locale:

        """
        return self.make_api_request(
            'listEventTypes',
            utils.get_kwargs(locals()),
            model=models.EventTypeResult,
        )

    @utils.requires_login
    def list_competitions(self, filter, locale=None):
        """

        returns a list of competitions based on the applied market filter

        :param MarketFilter filter:
        :param str locale:

        """
        return self.make_api_request(
            'listCompetitions',
            utils.get_kwargs(locals()),
            model=models.CompetitionResult,
        )

    @utils.requires_login
    def list_time_ranges(self, filter, granularity):
        """

        :param MarketFilter filter:
        :param TimeGranularity granularity:

        """
        return self.make_api_request(
            'listTimeRanges',
            utils.get_kwargs(locals()),
            model=models.TimeRangeResult,
        )

    @utils.requires_login
    def list_events(self, filter, locale=None):
        """

        :param MarketFilter filter:
        :param str locale:

        """
        return self.make_api_request(
            'listEvents',
            utils.get_kwargs(locals()),
            model=models.EventResult,
        )

    @utils.requires_login
    def list_market_types(self, filter, locale=None):
        """

        :param MarketFilter filter:
        :param str locale:

        """
        return self.make_api_request(
            'listMarketTypes',
            utils.get_kwargs(locals()),
            model=models.MarketTypeResult,
        )

    @utils.requires_login
    def list_countries(self, filter, locale=None):
        """

        :param MarketFilter filter:
        :param str locale:

        """
        return self.make_api_request(
            'listCountries',
            utils.get_kwargs(locals()),
            model=models.CountryCodeResult,
        )

    @utils.requires_login
    def list_venues(self, filter, locale=None):
        """

        :param MarketFilter filter:
        :param str locale:

        """
        return self.make_api_request(
            'listCountries',
            utils.get_kwargs(locals()),
            model=models.VenueResult,
        )

    @utils.requires_login
    def list_market_catalogue(
            self, filter, max_results=100, market_projection=None, locale=None,
            sort=None):
        """

        :param MarketFilter filter:
        :param int max_results:
        :param list market_projection:
        :param MarketSort sort:
        :param str locale:

        """
        return self.make_api_request(
            'listMarketCatalogue',
            utils.get_kwargs(locals()),
            model=models.MarketCatalogue,
        )

    @utils.requires_login
    def list_market_book(
            self, market_ids, price_projection=None, order_projection=None,
            match_projection=None, currency_code=None, locale=None):
        """

        :param list market_ids: List of market IDs
        :param PriceProjection price_projection:
        :param OrderProjection order_projection:
        :param MatchProjection match_projection:
        :param str currency_code:
        :param str locale:

        """
        return self.make_api_request(
            'listMarketBook',
            utils.get_kwargs(locals()),
            model=models.MarketBook,
        )

    @utils.requires_login
    def list_market_profit_and_loss(
            self, market_ids, include_settled_bets=False,
            include_bsp_bets=None, net_of_commission=None):
        """Retrieve profit and loss for a given list of markets.

        :param list market_ids: List of markets to calculate profit and loss
        :param bool include_settled_bets: Option to include settled bets
        :param bool include_bsp_bets: Option to include BSP bets
        :param bool net_of_commission: Option to return profit and loss net of
            users current commission rate for this market including any special
            tariffs

        """
        return self.make_api_request(
            'listMarketProfitAndLoss',
            utils.get_kwargs(locals()),
            model=models.MarketProfitAndLoss,
        )

    # Chunked iterators for list methods

    def iter_list_market_book(self, market_ids, chunk_size, **kwargs):
        """Split call to `list_market_book` into separate requests.

        :param list market_ids: List of market IDs
        :param int chunk_size: Number of records per chunk
        :param dict kwargs: Arguments passed to `list_market_book`

        """
        return itertools.chain(*(
            self.list_market_book(market_chunk, **kwargs)
            for market_chunk in utils.get_chunks(market_ids, chunk_size)
        ))

    def iter_list_market_profit_and_loss(
            self, market_ids, chunk_size, **kwargs):
        """Split call to `list_market_profit_and_loss` into separate requests.

        :param list market_ids: List of market IDs
        :param int chunk_size: Number of records per chunk
        :param dict kwargs: Arguments passed to `list_market_profit_and_loss`

        """
        return itertools.chain(*(
            self.list_market_profit_and_loss(market_chunk, **kwargs)
            for market_chunk in utils.get_chunks(market_ids, chunk_size)
        ))

    # Betting methods

    @utils.requires_login
    def list_current_orders(
            self, bet_ids, market_ids, order_projection, date_range, order_by,
            sort_dir, from_record, record_count):
        """

        :param bet_ids:
        :param market_ids:
        :param order_projection:
        :param date_range:
        :param order_by:
        :param sort_dir:
        :param from_record:
        :param record_count:

        """
        return self.make_api_request(
            'listCurrentOrders',
            utils.get_kwargs(locals()),
            model=models.CurrentOrderSummaryReport,
        )

    @utils.requires_login
    def list_cleared_orders(
            self, bet_status, event_type_ids, event_ids, market_ids,
            runner_ids, bet_ids, side, settled_date_range, group_by,
            include_item_description, locale, from_record, record_count):
        """

        :param bet_status:
        :param event_type_ids:
        :param event_ids:
        :param market_ids:
        :param runner_ids:
        :param bet_ids:
        :param side:
        :param settled_date_range:
        :param group_by:
        :param include_item_description:
        :param locale:
        :param from_record:
        :param record_count:

        """
        return self.make_api_request(
            'listClearedOrders',
            utils.get_kwargs(locals()),
            model=models.ClearedOrderSummaryReport,
        )

    @utils.requires_login
    def place_orders(self, market_id, instructions, customer_ref=None):
        """Place new orders into market. This operation is atomic in that all
        orders will be placed or none will be placed.

        :param str market_id: The market id these orders are to be placed on
        :param list instructions: List of `PlaceInstruction` objects
        :param str customer_ref: Optional order identifier string

        """
        return self.make_api_request(
            'placeOrders',
            utils.get_kwargs(locals()),
            model=models.PlaceExecutionReport,
        )

    @utils.requires_login
    def cancel_orders(self, market_id, instructions, customer_ref=None):
        """Cancel all bets OR cancel all bets on a market OR fully or
        partially cancel particular orders on a market.

        :param str market_id: If not supplied all bets are cancelled
        :param list instructions: List of `CancelInstruction` objects
        :param str customer_ref: Optional order identifier string

        """
        return self.make_api_request(
            'cancelOrders',
            utils.get_kwargs(locals()),
            model=models.CancelInstructionReport,
        )

    @utils.requires_login
    def replace_orders(self, market_id, instructions, customer_ref=None):
        """This operation is logically a bulk cancel followed by a bulk place.
        The cancel is completed first then the new orders are placed.

        :param str market_id: The market id these orders are to be placed on
        :param list instructions: List of `ReplaceInstruction` objects
        :param str customer_ref: Optional order identifier string

        """
        return self.make_api_request(
            'replaceOrders',
            utils.get_kwargs(locals()),
            model=models.ReplaceExecutionReport,
        )

    @utils.requires_login
    def update_orders(self, market_id, instructions, customer_ref=None):
        """Update non-exposure changing fields.

        :param str market_id: The market id these orders are to be placed on
        :param list instructions: List of `UpdateInstruction` objects
        :param str customer_ref: Optional order identifier string

        """
        return self.make_api_request(
            'updateOrders',
            utils.get_kwargs(locals()),
            model=models.UpdateExecutionReport,
        )

