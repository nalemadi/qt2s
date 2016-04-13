__author__ = 'sofiane'

import hashlib
import random
import base64
from database import db


class Client(db.Model):
	__tablename__ = 'clients'
	name = db.Column(db.String(32), primary_key=True)
	key = db.Column(db.String(64))

	def __init__(self, name=None):
		self.name = name

	def generate_key(self):
		""" Gererates a random Key.
		:return: a 43 character string.
		"""
		self.key = base64.b64encode(hashlib.sha256(str(random.getrandbits(256))).digest(),
							random.choice(['sA', 'hZ', 'mG', 'rH', 'fG', 'aR', 'SS'])).rstrip('==')



