__author__ = 'ammarorama'

from datetime import datetime
from bot import datetime_tools as dtt
from bot import bot_methods as bm




dtt.get_month(datetime.strptime("29 May 2015", "%d %b %Y"))
dtt.get_weekday(datetime.strptime("29 May 2015", "%d %b %Y"))


def test_get_month():
    assert dtt.get_month(datetime.strptime("29 May 2015", "%d %b %Y")) == 'May'


def test_get_weekday():
    assert dtt.get_weekday(datetime.strptime("29 May 2015", "%d %b %Y")) == 'Friday'

def test_implied_percentage():
    dat = {'a':1, 'b':2, 'c':1000, 'd':3.2, 'e':0, 'f':0.5, 'g':1.7}
    res = {'a': 0.0, 'b': 0.5, 'c': 0.001, 'd': 0.3125, 'e': 0.0, 'f': 0.0, 'g': 0.58824}
    assert bm.implied_percentage(**dat) == res
