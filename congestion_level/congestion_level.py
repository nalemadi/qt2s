import os
import sys
import json
from datetime import timedelta, date, datetime
import calendar
from collections import defaultdict

class Congestion_Level:
    #TODO:remove unnecessary functions
    def __init__(self):
        path = sys.argv[1]
        list = []
        for file in os.listdir(path):
            if file.endswith(".tsv"):
                route_name = file.split('.')
                aFile = open(path+'/'+file)
                route_dict = dict()
                route_details_list = []
                for line in aFile:
                    broken = line.split('\t')
                    route_details = {}
                    route_details['date'] = broken[0].strip()
                    route_details['timestamp'] = float(broken[1].strip())
                    route_details['distance'] = broken[2].strip()
                    route_details['duration'] = int(broken[3].strip())
                    route_details_list.append(route_details)
                route_dict[route_name[0]] = route_details_list
                #print route_dict
                list.append(route_dict)
        routes_dict = {}
        routes_dict['routes'] = list
        list_tmp = json.dumps(routes_dict)
        self.list = json.loads(list_tmp)
        #self.week_days = {"SUNDAY":06, "MONDAY":00, "TUESDAY":01, "WEDNESDAY":02, "THURSDAY":03, "FRIDAY":04, "SATURDAY":05}
        self.week_days_list = {"Sunday":0, "Monday":1, "Tuesday":2, "Wednesday":3, "Thursday":4, "Friday":5, "Saturday":6}

    # TODO: measure waste time for each route (time/min Time)
    def get_waste_time(self, route):
        print 'get_waste_time'

    def get_routes_on_date(self, r_date):
        print 'get_routes_on_date function'
        routes = []
        if r_date is None:
            return None

        for route in self.list['routes']:
            for records in route:
                #print "key: %s" % (records)
                new_rec_dict = {}
                record_list = []
                for record in route[records]:
                    #print record
                    if record['date'] == r_date:
                        record_list.append(record)
                new_rec_dict[records] = record_list
                routes.append(new_rec_dict)
        return routes

    def get_routes_on_day(self, day):
        print 'get_routes_on_day'
        week_day = self.week_days[day]
        routes = []
        if day is None:
            return None
        for route in self.list['routes']:
            for records in route:
                new_rec_dict = {}
                record_list = []
                for record in route[records]:
                    record_day = datetime.fromtimestamp(record['timestamp'])
                    current_week_day = record_day.weekday()
                    if current_week_day == week_day:
                        #print record_day, current_week_day, day
                        record_list.append(record)
                new_rec_dict[records] = record_list
                routes.append(new_rec_dict)
        return routes

    def daterange(self, start_date, end_date):
        for n in range(int ((end_date - start_date).days)):
            yield start_date + timedelta(n)

    def time_series_of_week_hourly(self):
        """
        This function is not used
        1 time series: 7 days for 24 hours for each day and calculate average
        :return:
        """
        # TODO: need to be changes to random key
        ahmed_bin_ali_route = self.list['routes'][0]['Ahmed_Bin_Ali_Str']
        first_timestamp = ahmed_bin_ali_route[0]['timestamp']
        start_date = date.fromtimestamp(first_timestamp)
        last_timestamp = ahmed_bin_ali_route[len(ahmed_bin_ali_route)-1]['timestamp']
        last_date = date.fromtimestamp(last_timestamp)+timedelta(days=1)

        print start_date, last_date
        count = 0
        time_series = []

        for i in self.daterange(start_date, last_date):
            date_str = i.strftime('%Y-%m-%d')
            if count <= 6:
                count += 1
                time_series_dict = {}
                day_records = self.process_data(i)
                time_series_dict[date_str] = day_records
                time_series.append(time_series_dict)
            else:
                print 'new week, reset count'
                time_series_dict = {}
                day_records = self.process_data(i)
                time_series_dict[date_str] = day_records
                time_series.append(time_series_dict)
                count = 0
        return time_series

    def process_data(self, i):
        """
        this function is not used
        :param i:
        :return:
        """
        #print (i)
        records_list = []
        for route in self.list['routes']:
            for records in route:
                #print records
                record_dict = {}
                dates = []
                for record in route[records]:
                    record_timestamp = record['timestamp']
                    record_date = date.fromtimestamp(record_timestamp)
                    if record_date == i:
                        record_datetime = datetime.fromtimestamp(record_timestamp)
                        record_datetime_str = record_datetime.strftime('%Y-%m-%d %H:%M:%S')
                        #print record_datetime
                        dates.append(record_datetime_str)
                print records, len(dates)
                record_dict[records] = dates
                records_list.append(record_dict)
        return records_list

    def get_weekly_report(self):
        """
        this function create a week report of congestion_level data by hour
        :return: week list
        """
        #TODO: write week report to file
        routes = self.list['routes']
        for route in routes:
            trajectory_name = route.keys()[0]
            t_start_date = date.fromtimestamp(route[trajectory_name][0]['timestamp'])
            t_last_date = date.fromtimestamp(route[trajectory_name][len(route[trajectory_name])-1]['timestamp'])+timedelta(days=1)
            print trajectory_name, t_start_date, t_last_date
            dates_record = route.itervalues().next()
            first_dayname = calendar.day_name[date.fromtimestamp(dates_record[0]['timestamp']).weekday()]
            if first_dayname != 'Sunday':
                #TODO: handle if first day is not Sunday
                print 'start day is not Sunday:', first_dayname
                break
            else:
                day_count = -1
                week_count = 7
                total_weeks_list = []
                week_list = []
                week_dict = {}
                week_key = 'week%s'%t_start_date
                #print week_key
                for r_date in self.daterange(t_start_date, t_last_date):
                    day_count += 1
                    if day_count < 7:
                       week_list.append(self.process_day_record_by_hour(r_date, dates_record))
                    else:
                        print week_key
                        week_dict[week_key] = week_list
                        total_weeks_list.append(week_dict)
                        # new week
                        start_week_date = t_start_date+timedelta(days=week_count)
                        week_key = 'week%s'%start_week_date
                        week_list = []
                        week_count += 7
                        day_count = 0
                        week_list.append(self.process_day_record_by_hour(r_date, dates_record))
                print len(total_weeks_list)
                # shoulld be removed, for testing only
                #break
        return None

    def process_day_record_by_hour(self, r_date, dates_record):
        record_day = calendar.day_name[r_date.weekday()]
        print record_day, r_date
        day_key = self.week_days_list[record_day]
        day_dict_list = []
        for hour in range(0, 24, 1):
            duration_list = []
            duration_avg = 0
            day_hour_dict = defaultdict(int)
            for record in dates_record:
                record_timestamp = record['timestamp']
                record_date = date.fromtimestamp(record_timestamp)
                record_datetime = datetime.fromtimestamp(record_timestamp)
                #print record_datetime
                if record_date == r_date: # same day
                    if record_datetime.hour == hour:
                        #print 'match', hour
                        duration_list.append(record['duration'])
            if len(duration_list) != 0:
                #TODO divid sum by min duration
                duration_avg = sum(duration_list)/len(duration_list)
            day_hour_dict[day_key,hour] = duration_avg
            day_dict_list.append(day_hour_dict)
        #print day_dict_list
        return day_dict_list

if __name__ == '__main__':
    congestion_level = Congestion_Level()
    congestion_level.get_weekly_report()
    #print congestion_level.list
    #print congestion_level.get_routes_on_date(None)
    #print congestion_level.get_routes_on_day("SUNDAY")
    #print json.dumps(congestion_level.time_series_of_week_hourly())