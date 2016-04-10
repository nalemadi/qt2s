import json
import time
import pymongo
from datetime import datetime
import time
import re
from itertools import groupby
from bson import json_util
import os

# -------------------------- #
# Utils
# -------------------------- #
def to_datetime(tweet):
	return datetime.strptime(tweet.get('created_at',None),'%a %b %d %H:%M:%S +0000 %Y')

def get_lstFreq(lst):
	return [{k:len(list(group))} for k, g in groupby( sorted(lst) )]


def json_serial(obj):
    if isinstance(obj, datetime):
        serial = obj.isoformat()
        return serial
    raise TypeError ("Type not serializable")

def to_json(fname,data):
	with open(fname, 'w') as fo:
		data  = list(data)
		print len(data)
		fo.write(json.dumps(data, indent=4,  default=json_util.default))

def validate_date(d):
	try:
		datetime.strptime(d, '%Y-%m-%dT%H:%M:%S')
		return True
	except ValueError:
		return False

