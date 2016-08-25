import os
import sys
from datetime import timedelta, date, datetime
import calendar
from collections import OrderedDict

data_files_path = '/export/sc/nalemadi/congestion_level/data'
reports_folder = 'reports'
weekly_report_file_name = 'weekly_report.txt'
date_format = '%Y-%m-%d'

class Congestion_Level():
    def __init__(self, path):
        self.list = self.read_records(path)
        self.week_days_list = {"Sunday":0, "Monday":1, "Tuesday":2, "Wednesday":3, "Thursday":4, "Friday":5, "Saturday":6}

    def read_records(self, path):
        list = []
        for file in os.listdir(path):
            if file.endswith(".tsv"):
                trajectory_name = file.split('.')[0]
                aFile = open(path+'/'+file)
                route_dict = dict()
                route_details_list = []
                for line in aFile:
                    broken = line.split('\t')
                    route_details = {}
                    route_details['date'] = broken[0].strip()
                    route_details['timestamp'] = float(broken[1].strip())
                    route_details['distance'] = broken[2].strip()
                    route_details['duration'] = float(broken[3].strip())
                    route_details_list.append(route_details)
                route_dict[trajectory_name] = route_details_list
                list.append(route_dict)
                aFile.close()
        trajectories_dict = {}
        trajectories_dict['routes'] = list
        return trajectories_dict

    def daterange(self, start_date, end_date):
        """
        :param start_date: start date
        :param end_date: last date
        :return: range of dates
        """
        for n in range(int ((end_date - start_date).days)):
            yield start_date + timedelta(n)

    def get_weekly_report(self):
        """
        This function create a week report of congestion_level data by hour from collected date (Google directions API)
        :return: week list
        """
        self.avg_week_dict = {}
        trajectories = self.list['routes']
        for trajectory in trajectories:
            trajectory_name = trajectory.keys()[0]
            t_start_date = date.fromtimestamp(trajectory[trajectory_name][0]['timestamp'])
            t_last_date = date.fromtimestamp(trajectory[trajectory_name][len(trajectory[trajectory_name])-1]['timestamp'])+timedelta(days=1)
            #print trajectory_name, t_start_date, t_last_date
            dates_record = trajectory.itervalues().next()
            first_day_name = calendar.day_name[date.fromtimestamp(dates_record[0]['timestamp']).weekday()]
            if first_day_name != 'Sunday':
                #TODO: handle if first day is not Sunday
                print 'start day is not Sunday:', first_day_name
                break
            else:
                day_count = -1
                week_count = 7
                week_list = []
                week_dict = {}
                week_key = t_start_date

                for r_date in self.daterange(t_start_date, t_last_date):
                    day_count += 1
                    if day_count < 7:
                        day_list = self.process_day_record_by_hour(r_date, dates_record)
                        week_list.append(day_list)
                    else:
                        week_dict[str(week_key)] = week_list
                        # new week
                        start_week_date = t_start_date+timedelta(days=week_count)
                        week_key = start_week_date
                        week_list = []
                        week_count += 7
                        day_count = 0
                        day_list = self.process_day_record_by_hour(r_date, dates_record)
                        week_list.append(day_list)

            # append last week days
            self.last_week_key = str(week_key)
            week_dict[str(week_key)] = week_list
            # order the dictionary
            week_dict = OrderedDict(sorted(week_dict.items()))
            self.get_avg(week_dict)
        self.write_weekly_report_to_txt_file()

    def get_avg(self, week_dict):
        # for each trajectory
        if len(self.avg_week_dict.keys()) == 0:
            for week_key, week_list in week_dict.items():
                avg_week_list = []
                for day in week_list:
                    full_day = {}
                    for day_hour, avg_value in day.items():
                        avg_values = []
                        avg_values.append(avg_value)
                        full_day[day_hour] = avg_values
                    full_day = OrderedDict(sorted(full_day.items()))
                    avg_week_list.append(full_day)
                self.avg_week_dict[week_key] = avg_week_list
        else: # fill the dictionary
            for week_key, week_list in week_dict.items():
                for i, day in enumerate(week_list):
                    for day_hour, avg_value in day.items():
                        avg_values_list = self.avg_week_dict[week_key][i][day_hour]
                        avg_values_list.append(avg_value)

    def process_day_record_by_hour(self, r_date, routes):
        # get minimum duration of a day
        min_duration_in_date = self.get_min_duration(r_date, routes)

        record_day = calendar.day_name[r_date.weekday()]
        day_key = self.week_days_list[record_day]
        day_dict_list = []
        day_hour_dict = {}
        for hour in range(0, 24, 1):
            duration_avg_in_hour = -1
            duration_list = []
            for record in routes:
                record_timestamp = record['timestamp']
                record_date = date.fromtimestamp(record_timestamp)
                record_datetime = datetime.fromtimestamp(record_timestamp)
                if record_date == r_date: # same day
                    if record_datetime.hour == hour:
                        duration_list.append(record['duration'])

            #remove -1 from duration list (for missing data in a date)
            duration_list = filter(lambda a: a != -1, duration_list)
            if len(duration_list) != 0:
                #divid avg by min duration in a date
                duration_avg = sum(duration_list)/len(duration_list)
                duration_avg_in_hour = duration_avg/min_duration_in_date


            day_key = '%02d' % (int(day_key),)
            hour = '%02d' % (hour,)
            day_hour_key = str(day_key)+','+str(hour)
            #print day_hour_key
            day_hour_dict[day_hour_key] = round(duration_avg_in_hour,2)
            day_dict_list.append(day_hour_dict)

        day_hour_dict = OrderedDict(sorted(day_hour_dict.items()))
        return day_hour_dict

    def get_min_duration(self, r_date, routes):
        # get minimum duration of a day
        total_duration = []
        for record in routes:
            record_timestamp = record['timestamp']
            record_date = date.fromtimestamp(record_timestamp)
            if record_date == r_date:
                total_duration.append(record['duration'])
        if len(total_duration) != 0:
            # remove -1 from duration list
            total_duration = filter(lambda a: a != -1, total_duration)
            min_duration_in_date = min(total_duration)
        else: # handle if records of a date are missing
            min_duration_in_date = -1
        return min_duration_in_date

    def write_weekly_report_to_txt_file(self):
        weekly_report_file = open(reports_folder+'/'+weekly_report_file_name, 'ab+')
        ####
        self.avg_week_dict = OrderedDict(sorted(self.avg_week_dict.items()))
        for week_key, week_list in self.avg_week_dict.items():
            #weekly_report_file.write(week_key)
            current_date = datetime.strptime(week_key, date_format).date()
            day_count = 0
            for i, day in enumerate(week_list):
                weekly_report_file.write(str(current_date)+':')
                if len(week_list) < 7 and i == len(week_list)-1:
                    print 'last day'
                    hour_count = 0
                    for day_hour_key, avg_durations_list in day.items():
                        avg_durations_list = filter(lambda a: a != -1, avg_durations_list)
                        if len(avg_durations_list) !=0:
                            avg_duration = sum(avg_durations_list)/len(avg_durations_list)
                            weekly_report_file.write(str(round(avg_duration,2)))
                            if hour_count < 23:
                                weekly_report_file.write(',')
                            else:
                                weekly_report_file.write(';')
                        if hour_count < 23:
                            hour_count += 1
                        else:
                            hour_count = 0
                else:
                    hour_count = 0
                    for day_hour_key, avg_durations_list in day.items():
                        avg_durations_list = filter(lambda a: a != -1, avg_durations_list)
                        avg_duration = 0
                        if len(avg_durations_list) !=0:
                            avg_duration = sum(avg_durations_list)/len(avg_durations_list)
                        else:
                            avg_duration = -1

                        if hour_count < 23:
                            weekly_report_file.write(str(round(avg_duration,2))+',')
                            hour_count += 1
                        else:
                            weekly_report_file.write(str(round(avg_duration,2)))
                            hour_count = 0
                        #hour_count += 1
                        #weekly_report_file.write(','+str(round(avg_duration,2)))
                    if day_count < 6:
                        weekly_report_file.write(';')
                        day_count += 1
                    else:
                        day_count = 0
                        weekly_report_file.write('\n')
                current_date = current_date+timedelta(days=1)
            #weekly_report_file.write('\n')
        weekly_report_file.close()

    def get_avg_duration(self, n_date, n_hour):
        all_avg_durations = []
        for file in os.listdir(data_files_path):
            if file.endswith(".tsv"):
                #trajectory_name = file.split('.')[0]
                aFile = open(data_files_path+'/'+file)
                duration_list = []
                total_duration_list = []
                for line in reversed(aFile.readlines()):
                    broken = line.split('\t')
                    n_timestamp = float(broken[1].strip())
                    record_datatime = datetime.fromtimestamp(n_timestamp)
                    record_date = date.fromtimestamp(n_timestamp)
                    record_hour = record_datatime.hour
                    if record_date == n_date:
                        duration = float(broken[3].strip())
                        total_duration_list.append(duration)
                        if record_hour == n_hour:
                            duration_list.append(duration)

                total_duration_list = filter(lambda a: a != -1, total_duration_list)
                duration_list = filter(lambda a: a != -1, duration_list)
                min_duration = -1
                if len(total_duration_list) != 0:
                    # get min duration of a date for a trajectory
                    min_duration = min(total_duration_list)
                avg_duration_in_hour = -1
                if len(duration_list) != 0:
                    # calculate avg duration of n_hour for a trajectory
                    avg_duration = sum(duration_list)/len(duration_list)
                    avg_duration_in_hour = avg_duration/min_duration
                all_avg_durations.append(avg_duration_in_hour)
                aFile.close()
        hour_avg = round(sum(all_avg_durations)/len(all_avg_durations),2)
        return hour_avg

    def get_date_hour(self):
        with open(reports_folder+'/'+weekly_report_file_name,'rb') as weeks_file:
            last_line =''
            for line in weeks_file:
                last_line = line
        days = last_line.split(';')
        last_day = days[len(days)-1]
        broken = last_day.split(':')
        last_date = broken[0]
        print last_date
        hours = broken[1].split(',')
        last_hour = len(hours)-1
        day_no = len(days)-1
        return last_date, day_no, last_hour

    def update_weekly_report(self, hour_avg, last_date, last_hour, day_no):
        next_date = last_date+timedelta(days=1)
        with open(reports_folder+'/'+weekly_report_file_name, 'ab+') as weekly_file:
            weekly_file.write(str(hour_avg))
            if last_hour < 23:
                weekly_file.write(',')
            else: # end of the day
                weekly_file.write(';')
                # add following date
                weekly_file.write(str(next_date)+':')
            if day_no == 6 and last_hour == 23:
                weekly_file.write('\n')
                weekly_file.write(str(next_date)+':')
        weekly_file.close()

if __name__ == '__main__':
    if len(sys.argv) > 1:
        path = path = sys.argv[1]
    else:
        path = data_files_path
    cl = Congestion_Level(path)
    # if weekly report file dosn't exist
    if not os.path.isfile(reports_folder+'/'+weekly_report_file_name):
        if not os.path.exists(reports_folder):
            os.makedirs(reports_folder)
            print 'reports folder does not exist, create one'
        print 'weekly reports not exist'
        print datetime.now()
        cl.get_weekly_report()
        print datetime.now()
    else: # else read the new ones only
        print 'weekly report exists'
        info_tuple = cl.get_date_hour()
        last_date = datetime.strptime(info_tuple[0], date_format).date()
        last_hour = int(info_tuple[2])
        day_no = int(info_tuple[1])
        hour_avg =  cl.get_avg_duration(last_date, last_hour)
        cl.update_weekly_report(hour_avg, last_date, last_hour, day_no)