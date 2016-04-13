
# ---------------------------------
# MongoDB Configuration File
# ---------------------------------


MONGODB_HOST = 'localhost'
MONGODB_PORT = 27017
DBS_NAME = 'QT2S'

COLLECTION_AR_TRAFFIC_NAME = 'ar_traffic_tweets'
COLLECTION_ENG_TRAFFIC_NAME = 'en_traffic_tweets'
COLLECTION_AR_NON_TRAFFIC_NAME = 'non_traffic_arabic_tweets'
COLLECTION_ENG_NON_TRAFFIC_NAME= 'non_traffic_tweets'
COLLECTION_AR_NON_LOCATED_TRAFFIC_NAME = 'non_located_arabic_traffic_tweets'
COLLECTION_ENG_NON_LOCATED_TRAFFIC_NAME = 'non_located_traffic_tweets'

COLLECTION_ENG_LOCATED_TRAFFIC_QA_NAME = 'qa_located_traffic_tweets'
COLLECTION_AR_LOCATED_TRAFFIC_QA_NAME = 'qa_located_arabic_traffic_tweets'
COLLECTION_ENG_LOCATED_TRAFFIC_WORLDWIDE_NAME = 'located_traffic_tweets_worldwide'
COLLECTION_ENG_LOCATED_TRAFFIC_WORLDWIDE_NAME = 'located_arabic_traffic_tweets_worldwide'



# ---------------------------------
# Directory for Temporary Files
# ---------------------------------
import os
APP_ROOT = os.path.dirname(os.path.abspath(__file__))   # refers to application_top
APP_STATIC = os.path.join(APP_ROOT)