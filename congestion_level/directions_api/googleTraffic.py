import json
from geocoding import geocoding
import datetime
import time

geo = geocoding()

#f_locations = open('locations.json')
#locations = json.load(f_locations)
#print len(locations)
#print type(locations)
#for line in f_locations:

#f_locations.close()
locations = [{"from": "25.680157,51.496874", "to": "Doha", "fname": "AlKhor_Doha"},
			 {"from": "Ar-Rayyan", "to": "Doha", "fname": "Ar-Rayyan_Doha"},
			 {"from": "Al Wakrah", "to": "Doha", "fname": "AlWakrah_Doha"},
			 {"from": "Mesaieed", "to": "Doha", "fname": "Mesaieed_Doha"},
			 {"from": "Al Gharafa", "to": "Doha", "fname": "AlGharafa_Doha"},
			 {"from": "Al Duhail, Doha", "to": "Doha", "fname": "AlDuhail_Doha"},
			 {"from": "Dukhan", "to": "Doha", "fname": "Dukhan_Doha"},
			 {"from": "Lusail", "to": "Doha", "fname": "Lusail_Doha"},
			 {"from": "Education City, Al Luqta Street, Ar-Rayyan, Al Rayyan", "to": "Doha", "fname": "EducationCity_Doha"},
			 {"from": "Umm Salal Muhammed, Umm Salal", "to": "E Ring Rd, Doha", "fname": "UmmSalalMuhammed_ERing"},
			 {"from": "25.281861,51.524136", "to": "25.2080968,51.4010795", "fname":"SalwaRoad"},
			 {"from": "25.304351,51.517432", "to": "25.232447,51.395358", "fname": "MohanedBinThani_AlwaabST"},
			 {"from": "25.322761,51.535681", "to": "25.284351,51.551602", "fname": "CornicheSt"},
			 {"from": "25.321107,51.514250", "to": "25.274978,51.525150", "fname": "Estiqlal_Jaidah"},
			 {"from": "25.315467,51.495343", "to": "25.296855,51.504227", "fname": "Ahmed_Bin_Ali_Str"}]

while(True):
	for location in locations:
		try:
			now_ts = int(time.time())
			now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
			google_route = geo.get_direction(location['from'], location['to'], departure_time=now_ts)
			fname = 'data/' + location['fname'] + '.tsv'
			with open(fname, 'a') as f:
				distance = geo.get_gdistance(google_route) # distance in meter
				duration_in_traffic = geo.get_gduration_in_traffic(google_route) # duration in seconds
				print '\t'.join([now, str(now_ts), fname, distance, duration_in_traffic])
				f.write('\t'.join([now, str(now_ts), distance, duration_in_traffic]) + '\n')
				# API rate limit
				if duration_in_traffic == '-1':
					print 'Rate limit: switching to the other key'
					active_key = int(open('active_key_index.txt','r').read())
					with open('active_key_index.txt','w') as g:
						g.write(str(1 - active_key))
					geo.set_active_key_index(active_key)

			# Other way around
			now_ts = int(time.time())
			now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
			google_route = geo.get_direction(location['to'], location['from'], departure_time=now_ts)
			fname = 'data/' + location['fname'] + '_reverse.tsv'
			with open(fname, 'a') as g:
				distance = geo.get_gdistance(google_route)
				duration_in_traffic = geo.get_gduration_in_traffic(google_route)
				print '\t'.join([str(geo.active_key_index), now, str(now_ts), fname, distance, duration_in_traffic])
				g.write('\t'.join([now, str(now_ts), distance, duration_in_traffic]) + '\n')
		except:
			print 'ERROR: something wrong happened on: %s', now
			continue
	time.sleep(1020) # sleep for 17 minutes