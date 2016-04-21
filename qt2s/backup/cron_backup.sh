DB_NAME= "QT2S"
COLLECTION_AR_NON_TRAFFIC_NAME=  "non_traffic_arabic_tweets"
COLLECTION_ENG_NON_TRAFFIC_NAME=  "non_traffic_tweets"
COLLECTION_AR_NON_LOCATED_TRAFFIC_NAME= "non_located_arabic_traffic_tweets"
COLLECTION_ENG_NON_LOCATED_TRAFFIC_NAME= "non_located_traffic_tweets"
COLLECTION_ENG_LOCATED_TRAFFIC_QA_NAME= "located_traffic_tweets_qa"
COLLECTION_AR_LOCATED_TRAFFIC_QA_NAME= "located_arabic_traffic_tweets_qa"
COLLECTION_ENG_LOCATED_TRAFFIC_WORLDWIDE_NAME= "located_arabic_traffic_tweets_worldwide"


# Most Important collections
mongoexport --db "$DB_NAME" --collection "$COLLECTION_ENG_LOCATED_TRAFFIC_QA_NAME" --out "$COLLECTION_ENG_LOCATED_TRAFFIC_QA_NAME".json


#mongoexport --db $DB_NAME --collection $COLLECTION_AR_LOCATED_TRAFFIC_QA_NAME --out $COLLECTION_AR_LOCATED_TRAFFIC_QA_NAME.json
#mongoexport --db $DB_NAME --collection $COLLECTION_ENG_LOCATED_TRAFFIC_WORLDWIDE_NAME --out $COLLECTION_ENG_LOCATED_TRAFFIC_WORLDWIDE_NAME.json

# mongoexport --db $DB_NAME --collection $COLLECTION_AR_NON_TRAFFIC_NAME --out $COLLECTION_AR_NON_TRAFFIC_NAME.json
# mongoexport --db $DB_NAME --collection $COLLECTION_ENG_NON_TRAFFIC_NAME --out $COLLECTION_ENG_NON_TRAFFIC_NAME.json
# mongoexport --db $DB_NAME --collection $COLLECTION_AR_NON_LOCATED_TRAFFIC_NAME --out $COLLECTION_AR_NON_LOCATED_TRAFFIC_NAME.json
# mongoexport --db $DB_NAME --collection $COLLECTION_ENG_NON_LOCATED_TRAFFIC_NAME --out $COLLECTION_ENG_NON_LOCATED_TRAFFIC_NAME.json









