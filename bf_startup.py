# -*- coding: utf-8 -*-
__author__ = 'Ammar Akhtar'

import os
import logging
import re
import sys
import subprocess,json
from betfair import Betfair


# held in the class
# auth_logger = logging.getLogger('bf_login\t')
# keep_alive_logger = logging.getLogger('bf_keep_alive\t')

IDENTITY_URL = 'https://identitysso.betfair.com/api/'
API_URL = 'https://api.betfair.com/exchange/betting/json-rpc/v1/'
ACTIVE_SESSION = False





# "curl -k -i -H \"Accept: application/json\" -H \"X-Application: VCfgMr8NqHwbSK74\" -X POST -d 'username=un&password=pw' https://identitysso.betfair.com/api/login"
def bf_interactive_login(username, password):
    auth_logger.info('trying login')
    call_bf_tok = subprocess.Popen(['curl',
            '-k',
            '-i',
            '-H',
            "Accept: application/json",
            '-H',
            "X-Application: %s" % app_key,
            '-X',
            'POST',
            '-d',
            'username=%s&password=%s'%(username,password),
            os.path.join(IDENTITY_URL, 'login')],
        stdout=subprocess.PIPE,
        )

    bf_tok_value = json.loads(call_bf_tok.communicate()[0].split('\n')[-1])
    auth_logger.info('login call returned status:\t%s' % bf_tok_value['status'])

    bf_tok_status = bf_tok_value['status']

    if bf_tok_status not in ['FAIL', 'LOGIN_RESTRICTED']:
        bf_tok = str(bf_tok_value['token'])
        auth_logger.info('token:\t%s' % bf_tok)
        ACTIVE_SESSION = True
        #todo: start a timer to call keep_alive

    else:
        auth_logger.error('login failed with status:\t%s' % bf_tok_status)
        login_error = bf_tok_value['error']
        auth_logger.error('error message:\t%s' % login_error)
        bf_tok = None
        ACTIVE_SESSION = False

    return ACTIVE_SESSION, bf_tok

def bf_keep_alive(bf_tok, app_key):
    keep_alive_logger.info('trying keep alive')
    keep_alive = subprocess.Popen(['curl', '-k', '-i', '-H', "Accept: application/json",
            '-H', "X-Authentication: %s" % bf_tok,
            '-H', "X-Application: %s" % app_key,
            '-X', 'POST',
            '-d', 'username=un&password=',
            os.path.join(IDENTITY_URL, 'keepAlive')],
        stdout=subprocess.PIPE,
        )

    keep_alive_value = json.loads(keep_alive.communicate()[0].split('\n')[-1])

    keep_alive_status = keep_alive_value['status']

    if keep_alive_status in ['SUCCESS']:
        token_match = str(keep_alive_value['token']) == bf_tok

        if token_match is False: #something fishy going on ...
            keep_alive_logger.error('Keep_alive succeeded but tokens do not match')
            keep_alive_logger.error('original token:\t %s' % bf_tok)
            keep_alive_logger.error('new token:\t %s' % str(keep_alive_value['token']))
            ACTIVE_SESSION = False

        else: # all is well
            keep_alive_logger.info('keep_alive succeeded')
            keep_alive_logger.info(keep_alive_value)
            ACTIVE_SESSION = True
        #todo: add some call to reset keep alive clock

    else: # keep_alive fails
        keep_alive_error = keep_alive_value['error']
        keep_alive_logger.error('keep_alive call fails with error message:\t%s' % keep_alive_error)
        ACTIVE_SESSION = False

    return ACTIVE_SESSION


# LOG_FILENAME = 'logs.out'
logging.basicConfig(level=logging.DEBUG)
run_logger = logging.getLogger('bf_startup')

print sys.argv
# should come from the calling function
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

# bf_tok = ''

import getpass

password = getpass.getpass(prompt='password:\n')

# password = sys.argv[2]
# ACTIVE_SESSION, bf_tok = bf_interactive_login()
#
# if ACTIVE_SESSION is True:
# 	ACTIVE_SESSION = bf_keep_alive(bf_tok)
#
# print ACTIVE_SESSION

client = Betfair(app_key)

client.interactive_login(username,password)
from betfair.models import MarketFilter
event_types = client.list_event_types(
    MarketFilter(text_query='soccer')
)

# competitions = client.list_competitions(
#     MarketFilter(competition_ids='1')
# )

print event_types, competitions

client.keep_alive()

# import betfair.exceptions
# raise betfair.exceptions.BetfairLoginError(['list'], {'error':'test'})
