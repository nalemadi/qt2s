
__author__ = 'noora'

import logging

logger = logging.getLogger('__name__')

class AccuracyFilter:
    def __init__(self, blacklisted_locations_file=None):
        if blacklisted_locations_file is None:
            logger.error("You should provide a path to black list file")
            raise Exception("Error: You should provide a path to black list file")
        list = []
        with open(blacklisted_locations_file) as f:
            for line in f:
                bl_location = line.strip().lower()
                list.append(bl_location)
        self.blacklisted_locations = list
        logger.info('New Instance\n Black List locations considered: %s', self.blacklisted_locations)


    def has_black_listed_location(self, text):
        """
        check whether tweet text has a blacklisted location
        :param text:
        :return: boolean value
        """
        text = text.lower()
        is_blacklisted_location = False
        for bl_location in self.blacklisted_locations:
            if bl_location in text:
                is_blacklisted_location = True
                break
        return is_blacklisted_location
"""
if __name__ == '__main__':
    filename = '../data/black_listed_locations.txt'
    af = AccuracyFilter(filename)
    test = af.has_black_listed_location('the road towards pearl is closed')
    print test
    if not test:
        print 'does not contain black list locations'
    else:
        print 'has blacklist location'
"""
