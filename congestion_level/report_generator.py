from datetime import timedelta, datetime
from collections import OrderedDict


class Report_Generator():

    def get_array_from_file(self, file_path):
            array = []
            with open(file_path, 'rb') as r_file:
                for line in r_file:
                    array.append(line.strip())
            r_file.close()
            return array

    def create_frontend_file(self):
        total_weeks_list = self.get_array_from_file('reports/weekly_report.txt')
        ###
        avg_dict = {}
        current_week_list = []
        previous_week_list = []
        first_date = None
        ###
        for day in range(0,7,1):
            for hour in range(0, 24, 1):
                day_hour = '%02d,%02d' % (day,hour)
                avg_dict[day_hour] = []
        avg_dict = OrderedDict(sorted(avg_dict.items()))
        ###
        curr_week = len(total_weeks_list)-1
        pre_week = len(total_weeks_list)-2
        for i,weeks in enumerate(total_weeks_list):
            days = weeks.strip().split(';')
            if i == curr_week:
                # current week
                first_date = datetime.strptime(days[0].split(':')[0],'%Y-%m-%d')
                # remove empty lines
                if '' in days:
                    index = days.index('')
                    del days[index]
                for j in days:
                    day_detail = j.split(':')
                    hour_values = day_detail[1].split(',')
                    current_week_list += map(float, hour_values)
                ###
            elif i == pre_week:
                # previous week
                for j in days:
                    day_detail = j.split(':')
                    hour_values = day_detail[1].split(',')
                    previous_week_list += map(float, hour_values)
            else:
                # avg week
                for day_count, day in enumerate(days):
                    day_detail = day.split(':')
                    hour_values = day_detail[1].split(',')
                    for hour, hour_values in enumerate(hour_values):
                        day_hour = '%02d,%02d' % (day_count,hour)
                        ls = avg_dict[day_hour]
                        ls.append(float(hour_values))

        # prepare avg_week list
        avg_list = []
        for day_hour, duration_list in avg_dict.items():
            # remove -1 from duration_list
            duration_list = filter(lambda a: a != -1, duration_list)
            avg_value = sum(duration_list)/len(duration_list)
            avg_list.append(round(avg_value,2))

        ####
        # write to file, overwrite if exist
        with open('reports/report.txt', 'w') as frontend_file:
            for i in range(0,168,1):
                avg_value = ''
                pre_value = ''
                current_value = ''
                if i < len(current_week_list) and current_week_list[i] != -1.0:
                    current_value = current_week_list[i]
                if previous_week_list[i] != -1.0:
                    pre_value = previous_week_list[i]
                if avg_list[i] != -1.0:
                    avg_value = avg_list[i]

                current_datetime = first_date+timedelta(hours=i)
                frontend_file.write(str(current_datetime)+','+str(current_value)+','+str(pre_value)+','+str(avg_value)+'\n')
        frontend_file.close()
if __name__ == '__main__':
    print 'generating report file'
    rg = Report_Generator()
    rg.create_frontend_file()
    print 'file is generated'