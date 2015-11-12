__author__ = 'sofiane'
import urllib2, urllib, json, httplib, logging

class FtAPI:
	def __init__(self, client_secret_file=None,tokens_file=None):
		# TODO redefine the way we populate different class attributes
		self.logger = logging.getLogger(__name__)
		if client_secret_file:
			sec = json.load(open(client_secret_file))
			sec = sec['installed']
			self.client_id = sec['client_id']
			self.client_secret = sec['client_secret']
			self.redirect_uri = sec['redirect_uris'][0]
			self.api_key = "[REDACTED]"
		else:
			raise("Please provide your client_secret file")

		if tokens_file:
			sec = json.load(open(tokens_file))
			self.access_token = sec['access_token']
			self.refresh_token = sec['refresh_token']
		else:
			self.get_tokens()

	def _persist_tokens(self):
		basepath = '[REDACTED]qt2s/Qt2sDashboard/'

		with open(basepath+'resources/tokens.json', 'w') as g:
			json.dump({'access_token': self.access_token, 'refresh_token': self.refresh_token}, g)

	def get_tokens(self):
		print 'GET TOKENS'
		print 'Visit the URL below in a browser to authorize'
		print
		print '%s?client_id=%s&redirect_uri=%s&scope=%s&response_type=code' % \
			  ('https://accounts.google.com/o/oauth2/auth', self.client_id, self.redirect_uri,
			   'https://www.googleapis.com/auth/fusiontables')
		print

		auth_code = raw_input('Enter authorization code ("code" parameter of URL): ')

		data = urllib.urlencode({
			'code': auth_code,
			'client_id': self.client_id,
			'client_secret': self.client_secret,
			'redirect_uri': self.redirect_uri,
			'grant_type': 'authorization_code'
		})
		request = urllib2.Request(
			url='https://accounts.google.com/o/oauth2/token',
			data=data)
		request_open = urllib2.urlopen(request)

		response = request_open.read()
		tokens = json.loads(response)
		self.access_token = tokens['access_token']
		self.refresh_token = tokens['refresh_token']
		self._persist_tokens()

	def get_new_token(self):
		print 'REFRESHING TOKENS'
		data = urllib.urlencode({
			'client_id': self.client_id,
			'client_secret': self.client_secret,
			'refresh_token': self.refresh_token,
			'grant_type': 'refresh_token'})
		request = urllib2.Request(
			url='https://accounts.google.com/o/oauth2/token', data=data)
		request_open = urllib2.urlopen(request)
		response = request_open.read()
		request_open.close()
		tokens = json.loads(response)
		self.access_token = tokens['access_token']
		self._persist_tokens()

	def get_tables(self):
		print "LIST TABLES"
		url = 'https://www.googleapis.com/fusiontables/v2/tables?%s' % \
			  (urllib.urlencode({'access_token': self.access_token, 'key': self.api_key}))
		return self.run_request(url)

	def desc(self, tableid):
		# url = 'https://www.googleapis.com/fusiontables/v2/tables/%s?%s' % \
		# 	  (tableid, urllib.urlencode({'access_token': self.access_token}))
		url = 'https://www.googleapis.com/fusiontables/v2/tables/%s?' % tableid
		return self.run_request(url)

	def create_table(self, schema):
		#url = 'https://www.googleapis.com/fusiontables/v2/tables?%s' % \
		#	  (urllib.urlencode({'access_token': self.access_token, 'key': self.api_key}))
		url = 'https://www.googleapis.com/fusiontables/v2/tables?'

		headers = {'Content-Type': 'application/json'}
		return self.run_request(url, json.dumps(schema), headers)

	def query(self, sql):
		print 'QUERY'
		#url = 'https://www.googleapis.com/fusiontables/v2/query?%s' % \
		#	  (urllib.urlencode({'access_token': self.access_token, 'key': self.api_key, 'sql': sql}))
		url = 'https://www.googleapis.com/fusiontables/v2/query?%s&' % urllib.urlencode({'sql': sql})
		return self.run_request(url)

	def import_rows(self, tableid, data):
		#url = 'https://www.googleapis.com/upload/fusiontables/v2/tables/%s/import?%s' % \
		#	  (tableid, urllib.urlencode({'access_token': self.access_token}))
		url = 'https://www.googleapis.com/upload/fusiontables/v2/tables/%s/import?' % tableid

		headers = {'Content-Type': 'application/octet-stream; charset=utf-8'}
		return self.run_request(url,data,headers)
		#return self.runrequest('POST',url,data,headers)

	def run_request(self, url, data=None, headers=None):
		url_new = url + urllib.urlencode({'access_token': self.access_token, 'key': self.api_key})
		if data and headers:
			request = urllib2.Request(url_new, data, headers)
		elif data:
			request = urllib2.Request(url_new, data)
		else:
			request = urllib2.Request(url_new)
		try:
			request_open = urllib2.urlopen(request)
			response = request_open.read()
			request_open.close()
			return json.loads(response)
		except urllib2.HTTPError as e:
			if e.code == 401 and e.reason == 'Unauthorized':
				print '%s: %s - Needs to generate new tokens' % (e.code, e.reason)
				self.get_new_token()
				self.logger.info('Expired Token, generated a new one and re run the request')
				url_new = url + urllib.urlencode({'access_token': self.access_token, 'key': self.api_key})
				if data and headers:
					request = urllib2.Request(url_new, data, headers)
				elif data:
					request = urllib2.Request(url_new, data)
				else:
					request = urllib2.Request(url_new)
				try:
					# resend the query
					request_open = urllib2.urlopen(request)
					response = request_open.read()
					request_open.close()
					return json.loads(response)
				except urllib2.HTTPError as e:
					if e.code == 401 and e.reason == 'Unauthorized':
						self.logger.info('Tried to replay with the new generated tokens without success.')
			else:
				print '%s: %s - Need to handle this error' % (e.code, e.reason)
			return None

	def runrequest(self, method, url, data=None, headers=None):
		request = httplib.HTTPSConnection("www.googleapis.com")
		if data and headers: request.request(method, url, data, headers)
		else: request.request(method, url)
		response = request.getresponse()
		response = response.read()
		return json.loads(response)

	def format_tables(self, tables):
		for table in tables['items']:
			print 'Table Name: %s\t\tTable ID:%s' % (table['name'], table['tableId'])
			cols = []
			for c in table['columns']:
				cols.append(c['name'] + ':' + c['type'])
			print '\t\t Columns:%s' % ','.join(cols)

if __name__ == "__main__":
	basepath = '[REDACTED]qt2s/Qt2sDashboard/'

	api_test = FtAPI(client_secret_file=basepath+'resources/client_secrets.json',
					 tokens_file=basepath+'resources/tokens.json')
	#sql = 'SELECT * FROM ' + tableid
	#tables = api_test.get_tables()
	#if tables:
	#    api_test.format_tables(tables)
	#resultset = api_test.query('hh')
	#if resultset:
	#    print resultset
	#table = api_test.desc(tableid)
	#if table:
	#	print table

	data = {}
	data['name'] = 'testingTable'
	data['columns'] = [{'name':'firsCol', 'type':'STRING'}]
	data['description'] = 'Table created from python'
	data['isExportable'] = True
	response = api_test.create_table(data)
	tableid = response['tableId']
	print tableid
	rows = "Mokrane, abbar, alger, USA\nMebarka, abbar, alger, alger"
	api_test.import_rows(tableid, rows)