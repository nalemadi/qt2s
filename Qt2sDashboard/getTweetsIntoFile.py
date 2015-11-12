__author__ = 'sofiane'
import yaml
import redis
import json


with open("[REDACTED]qt2s/Qt2sDashboard/resources/remote_apiconfig.yml",'r') as f:
	cfg = yaml.load(f)
redis_host = cfg['redis']['host']
redis_port = cfg['redis']['port']
redis_hostname = cfg['redis']['hostname']
redis_located_en_channel = cfg['redis']['channels']['located_tweets']
redis_located_ar_channel = cfg['redis']['channels']['located_arabic_traffic_tweets']
redis_db = redis.Redis(host=redis_host, port=redis_port)
redis_located_en_tweets_channel = '{0}:{1}'.format(redis_hostname,redis_located_en_channel)
redis_located_ar_tweets_channel = '{0}:{1}'.format(redis_hostname,redis_located_ar_channel)

def get_tweets(count, language):
	""" retrieve a list of tweets
	:rtype : list of tweets
	"""
	tweets = []
	if language == 'en':
		tweets = [json.loads(tw) for tw in redis_db.lrange(redis_located_en_tweets_channel, -count, -1)]
	elif language == 'ar':
		tweets = [json.loads(tw) for tw in redis_db.lrange(redis_located_ar_tweets_channel, -count, -1)]
	return tweets

tweets = get_tweets(3000, 'en')
outfile = open('[REDACTED]qt2s/Qt2sDashboard/data/tweets_en.txt', 'w')
for tw in tweets:
	outfile.write(json.dumps(tw)+'\n')
outfile.close()
