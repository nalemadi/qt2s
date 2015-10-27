__author__ = 'sofiane'


import logging
from os import listdir
from os.path import isfile, join

logger = logging.getLogger('__name__')


class TwitterPersister:

	def __init__(self, persister_folder=None, file_size=100000):
		if persister_folder is None:
			raise Exception("Please provide a folder in which files will be stored")
		self.folder = persister_folder
		self.max_size = file_size
		self.current_file_size = 0
		self.current_file = self._get_current_file_name()

	def _get_current_file_name(self):
		""" This method is only called on instantiation to make sure we always start with the right file,
		even after a crash.
		Reads file names, gets the higher index: part_index
		:return: higher indexed file name if this one has less than file_size lines, part_index+1 otherwise.
		"""
		files = sorted([f for f in listdir(self.folder) if isfile(join(self.folder, f))], reverse=True)
		if len(files) == 0:
			return "part_0000"
		else:
			with open(join(self.folder, files[0])) as f:
				for i, l in enumerate(f):
					pass
			if i+1 < self.max_size:
				self.current_file_size = i+1
				return files[0]
			else:
				index = str(int(files[0].split('_')[1]) + 1)
				for _ in range(4-len(index)):
					index = '0' + index
				self.current_file_size = 0
				return 'part_'+index

	def _get_next_file_name(self):
		"""
		Reads file names, gets the higher index: part_index
		:return: the name of the new file: part_index+1.
		"""
		files = sorted([f for f in listdir(self.folder) if isfile(join(self.folder, f))], reverse=True)
		if len(files) == 0:
			return "part_0000"
		else:
			index = str(int(files[0].split('_')[1]) + 1)
			for _ in range(4-len(index)):
				index = '0' + index
		return 'part_'+index

	def append_tweet(self, tweet):
		if self.current_file_size >= self.max_size:
			self.current_file = self._get_next_file_name()
			self.current_file_size = 0
			logger.info("Created a new file: {}".format(self.current_file))
		else:
			with open(join(self.folder, self.current_file), 'a') as f:
				f.write(tweet+'\n')
				self.current_file_size += 1






