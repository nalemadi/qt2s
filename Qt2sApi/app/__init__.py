import os
from flask import Flask
from flask import render_template
from pymongo import MongoClient, errors
import datetime
from config import *

#from app.scrapper.twitter_scrapper import *

# ---------------------------------
# Flask Configuration
# ---------------------------------
app = Flask(__name__,static_url_path='')

# ---------------------------------
# Database Connection
# ---------------------------------

try:
	connection = MongoClient(MONGODB_HOST, MONGODB_PORT, connect=False)
	print "<DEBUG>: Connected to MongoDB successfully!!!"
	# Those two collections are not releavant
	# COLLECTION_AR_TRAFFIC = connection[DBS_NAME][COLLECTION_AR_TRAFFIC_NAME ]
	# COLLECTION_ENG_TRAFFIC = connection[DBS_NAME][COLLECTION_ENG_TRAFFIC_NAME]

	COLLECTION_AR_NON_TRAFFIC = connection[DBS_NAME][COLLECTION_AR_NON_TRAFFIC_NAME]
	COLLECTION_ENG_NON_TRAFFIC = connection[DBS_NAME][COLLECTION_ENG_NON_TRAFFIC_NAME]

	COLLECTION_AR_NON_LOCATED_TRAFFIC = connection[DBS_NAME][COLLECTION_AR_NON_LOCATED_TRAFFIC_NAME]
	COLLECTION_ENG_NON_LOCATED_TRAFFIC = connection[DBS_NAME][COLLECTION_ENG_NON_LOCATED_TRAFFIC_NAME]

	COLLECTION_ENG_LOCATED_TRAFFIC = connection[DBS_NAME][COLLECTION_ENG_LOCATED_TRAFFIC_NAME]
	COLLECTION_AR_LOCATED_TRAFFIC = connection[DBS_NAME][COLLECTION_AR_LOCATED_TRAFFIC_NAME]

except errors.ConnectionFailure, e:
   print "Could not connect to MongoDB: %s" % e



# ---------------------------------
# Scrapping Threads
# ToDo: Ask Souf whether we need to run a cron job or run threads 
# ---------------------------------

# Twitter: Scrapping stream of twitter data 
# twitterListener = Listener()
# twitterListener.start()


# Instagram: Scrapping instagram posts every 60 seconds


from app import views 


