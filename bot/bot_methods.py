__author__ = 'ammarorama'


def implied_percentage(**kwargs):
    r = {}
    for k, v in kwargs.items():

        if isinstance(v, (int, long)):
            v = float(v)

        if v > 1.:
            r.update({k:round(1/v,5)})

        else:
            r.update({k:0.})

    return r


# ensure market is open

# get price w greatest depth on runner
# max(xx[0].serialize()['runners'][1]['ex']['availableToBack'], key=lambda x:x['size'])

# get total traded on runner
# sum([x['size'] for x in yy[0].serialize()['runners'][0]['ex']['tradedVolume']])
# yy[0].serialize()['runners'][0]['totalMatched']


# runner traded % of total traded on market
# yy[0].serialize()['runners'][1]['totalMatched'] / yy[0].serialize()['totalMatched']


# BBO vs last traded price on runner
# spread on runner
# xx[0].serialize()['runners'][1]['lastPriceTraded']
# xx[0].serialize()['runners'][1]['ex']['availableToBack'][0]
# xx[0].serialize()['runners'][1]['ex']['availableToLay'][0]


# time since lastMatchTime on market
import datetime, time, pytz
# print (datetime.datetime.now(tz=pytz.utc) - xx[0].serialize()['lastMatchTime']).total_seconds()
# store the lastMatchTime per market as it changes