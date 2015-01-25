import base64
import numpy as np
import re
from collections import OrderedDict
from operator import itemgetter, attrgetter
from datetime import datetime, date
from decimal import Decimal

try:
    import simplejson as json
except ImportError:
    import json

# from smcore.enums import general_enums
from . import datetime_tools

def cumulative(iterable):
    return [sum(iterable[:i+1]) for i in xrange(len(iterable))]

def extent(iterable):
    return (float(min(iterable)),float(max(iterable)))

def domain_to_range(val, domain, codomain):
    """
    maps val from domain to range
    @param val: float
    @param domain: if number, converted to range, if list, take extent
    @param codomain: (a.k.a range) if number, converted to range, if list, take extent
    @return:
    """

    def get_range(v):
        if isinstance(v, (int, float)):
            v = extent((0,v))
        elif isinstance(v, (list,tuple)):
            v = extent(v)
        return v

    val = float(val)

    domain = get_range(domain)
    domain_len = domain[1] - domain[0]

    codomain = get_range(codomain)
    codomain_len = codomain[1] - codomain[0]

    scale = float(codomain_len) / domain_len

    return ((val - domain[0]) * scale) + codomain[0]


def tuples_to_lists(tuples):
    """ Turns all of the tuples in any structure of tuples and lists into lists """
    return list(map(tuples_to_lists(), tuples)) if isinstance(tuples, (list, tuple)) else tuples


def get_ordered_list_by_key(list, key_string, reverse=False):
    """ Sorts a list by a specified key_string"""
    try:
        return sorted(list, key=itemgetter(key_string), reverse=reverse)
    except:
        return sorted(list, key=attrgetter(key_string), reverse=reverse)


def ordered_set(original_list):
    """
    Takes original_list, creates an ordered dict, then converts back to list

    """
    return list(OrderedDict.fromkeys(original_list))


def find_in_tuple(tuple_list, lookup, lookup_col=0, search_col=1):
    """
    Find value in list or tuple of tuples. Very similar to excel VLOOKUP()
    the 'lookup' argument is matched in the lookup_col, and
    the appropriate value in the search_col is returned
    """
    zipped_tuple = zip(*tuple_list)

    try:
        return zipped_tuple[search_col][zipped_tuple[lookup_col].index(lookup)]

    except ValueError:
        return {'error_code': 0, 'error_value': 'nothing found'}  # maybe this should be False?


def ordered_set_from_list_of_pairs(originalList):
    new_rels = []

    keys = zip(*originalList)[0]

    pairVals = zip(*originalList)[1]

    for counter, x in enumerate(keys):
        if new_rels == []:
            new_rels.append([x, pairVals[counter]])

        elif x not in zip(*new_rels)[0]:
            new_rels.append([x, pairVals[counter]])

    return new_rels

def as_json(input, indent=0):
    """ Will convert a Python dictionary into a JSON object.
        Conversion is first attempted using simplejson, if this does not work then json will be used.

        INPUTS: <Python dict>
        OUTPUTS: <JSON object>

    """
    # if isinstance(input, dict):
    return json.dumps(json_clean_item(input), indent=indent, sort_keys=True)
    # elif isinstance(input, list):
    # 	return_list = []
    # 	for item in input:
    # 		return_list.append(as_json(item))
    # 	return json.dumps(return_list)#, indent=indent)

def convert_datetimes_in_dictionary(input):

    # if isinstance(input_param, list):
    # dictionary = {"temp_key":input_param}
    if isinstance(input, dict):
        for k, v in input.iteritems():
            input[k] = json_clean_item(v)

        return input

    else:
        return json_clean_item(input)

def json_clean_item(item):
    if isinstance(item, dict):
        for k, val in item.iteritems():
            item[k] = json_clean_item(val)
        return item

        # return convert_datetimes_in_dictionary(v)
    elif isinstance(item, (list, tuple)):
        return [json_clean_item(i) for i in item]

        # temp_dict = {}

        # for i in xrange(len(item)):
        # 	temp_dict.setdefault(i, item[i])

        # temp_dict = json_clean_item(temp_dict)

        # return [temp_dict[key] for key in xrange(len(item))]

    elif isinstance(item, (date, datetime)):
        return datetime_tools.datetime_to_string(item, split=True, easy=False, reverse=False)

    elif isinstance(item, Decimal):
        return float(item)

    elif isinstance(item, (float, long, int, basestring, unicode, bool)):
        return item

    elif item == None:
        return item

    elif isinstance(item, object):
        try:
            return str(item.__unicode__())
        except:
            return str(item.__class__) + " object without unicode"
    else:
        return "could not JSON object"


def from_json(input):
    """ Will convert a JSON object into a Python dictionary .
        Conversion is first attempted using simplejson, if this does not work then json will be used.

        INPUTS: <JSON object>
        OUTPUTS: <Python dict>

    """
    try:
        return json.load(input)
    except:
        return json.loads(input)


# def bool_to_english(bool_value):
#     """ Converts the bool True into the string "Yes" and the bool False, into the string "No".
#         In this instance bool includes any boolean string variable from enums.BOOL_TRUES.
#
#         Any null or non-boolean/enums.BOOL_TRUES value will produce a "No".
#
#         INPUTS: <boolean or enums.BOOL_TRUES>
#         OUTPUT: <string "Yes" or "No">
#     """
#     if bool_value in general_enums.BOOL_TRUES:
#         return "Yes"
#
#     else:
#         return "No"


def underscores_to_spaces(word_with_underscores):
    """
    This function removes underscores from a word and replaces them with spaces:
    the_test_Word_IS__this -> the test Word IS  this
    with no other changes involved
    """
    return re.sub('_', r' ', word_with_underscores)


def spaces_to_underscores(word_with_underscores):
    """
    This function removes underscores from a word and replaces them with spaces:
    the_test_Word_IS__this -> the test Word IS  this
    with no other changes involved
    """
    return re.sub(' ', r'_', word_with_underscores)


def remove_spaces(name):
    """ returns value of string with underscores replaced with spaces """
    return name.replace(' ', '')


def str_to_number(number, dp=None):
    """
    Take a string and try to turn it into a float, then an int. If successful at either step return the float or int value.
     Use dp to set number or
    """

    numType = 'str'

    try:
        float(number)
        numType = 'fl'

    except ValueError:
        return str(number)

    except TypeError:
        return None

    if numType == 'fl':
        try:
            int(number)
            return int(number)

        except ValueError:
            if dp:
                return round(float(number), dp)
            else:
                return float(number)

    else:
        return {'error': 'numType = str'}


def encode_list_or_array(data):
    if isinstance(data, list):
        data = np.array(data)

    return base64.b64encode(data.astype(np.float64))


def decode_to_array(data):
    return np.frombuffer(base64.decodestring(data), dtype=np.float64)


from django.utils.encoding import smart_str


def _smart_key(key):
    return smart_str(''.join([c for c in key if ord(c) > 32 and ord(c) != 127]))


def make_key(key, key_prefix='', version=''):
    "Truncate all keys to 250 or less and remove control characters"
    return ':'.join([key_prefix, str(version), _smart_key(key)])[:250]

def aggregate_coordinates_with_weighting(anchor_locations_list):
        """
            coords should be a list of coordinates each set of which should be a tuple of the form:
            self.anchor_locations_list = [(latitude, longitude, weighting),...]
        """

        if len(anchor_locations_list) > 0:
            total_weight = sum(zip(*anchor_locations_list)[2]) # sum([c[2] for c in self.anchor_locations_list])
            if total_weight != 0:

                latitude, longitude = 0, 0

                for c in anchor_locations_list:

                    latitude += c[0] * float(c[2])/total_weight

                    longitude += c[1] * float(c[2])/total_weight

                return (latitude, longitude)
            else:
                return None

        else:
            return None

# CRW: AWESOME!!! really cool little pair of functions that find every unique combination (not permutation, so these 
#      combinations are equal [1,2] = [2,1]), of more than 2 elements, of elements in list, e.g. for the list [1,2,3] 
#      they return: [[1,2,3],[1,2],[1,3],[2,3]] 
def clean_all_combinations(my_list):
    """
    Hit this function first. It cleans the list of combinations that return from the all_combinations
    function to get rid of duplicates and single-element combinations (e.g. [1] is removed).

    INPUT: [list]
    RETURN: [list of [list]]
    """
    list_to_clean = all_combinations( my_list )
    clean_list = []
    clean_list.append( my_list )
    for element in list_to_clean:
        if element not in clean_list and len(element) > 0:
            clean_list.append( element )
    return clean_list

def all_combinations(my_list):
    """
    Passed a list, this function will return a list of lists of every combination of every element from
    the original list. NOTE: It does this using recursion.

    INPUT: [list]
    RETURN: [list of [list]]
    """
    return_lists = []
    for element in my_list:
        list_to_add = []
        for a_different_element in my_list:
            if a_different_element != element:
                list_to_add.append(a_different_element)
        return_lists.append( list_to_add )
        if len(list_to_add) < 2:
            pass
        else:
            return_lists.extend(all_combinations( list_to_add ))
    return return_lists
