__author__ = 'Noora'

import logging
import json
import re

from resources.resources import clean_text

logger = logging.getLogger('__name__')

class IncidentClassifier:
    def __init__(self, categories_dictionary_file=None):
        if categories_dictionary_file is None:
            logger.error("You should provide a path to the categories dictionary file")
            raise Exception("Error: You should provide a path to the categories dictionary file")
        categories = {}
        with open(categories_dictionary_file) as f:
            for line in f:
                if len(line.strip()) == 0:
                    continue
                all_categories = json.loads(line)
                for category_key in all_categories:
                    for category in all_categories[category_key]:
                        categories[clean_text(category.lower())] = category_key

		self.categories = categories
        logger.info('New Instance\n Categories considered: %s', self.categories)

    def get_tweet_category(self, text):
        category_name = 'Others'
        text = clean_text(text.lower())
        for category in self.categories.keys():
            category_len = len(category.split(' '))
            ngrams_list = self.ngrams(text, category_len)
            for ngram in ngrams_list:
                if category == ngram:
                    category_name = self.categories[category]
        return category_name

    def getWords(self, text):
        """
		clean tweet text
		:param text: body of the tweet
		:return: list of words
		"""
        return re.compile('\w+').findall(text)

    def ngrams(self, inputText, n):
		inputText = self.getWords(inputText)
		output = []
		for i in range(len(inputText)-n+1):
			g = ' '.join(inputText[i:i+n])
			output.append(g)
		return output


#if __name__ == '__main__':
#	incidentClassifier = IncidentClassifier(categories_dictionary_file='../data/categories_dict.txt')
#	print incidentClassifier.get_tweet_category("traffic jam becuase of car crash")