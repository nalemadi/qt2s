__author__ = 'noora'

import redis
import json

REDIS_NAMESPACE = 'QMIC'
REDIS_QATAR_BASED_TWEETS = 'qatar_based_tweets'
REDIS_DB = redis.Redis()

# check qatar BB