import matplotlib.pyplot as plt
import matplotlib.dates as md
import dateutil
import time
from datetime import datetime
import calendar 
import csv
a=0
#将时间戳规范为10位时间戳
def timestamp_to_timestamp10(time_stamp):
    time_stamp = int (time_stamp* (10 ** (10-len(str(time_stamp)))))
    return time_stamp

#将10位时间戳转换为时间字符串，默认为2021-01-01 00:00:00格式
def timestamp_to_date(time_stamp, format_string="%Y-%m-%d %H:%M:%S"):
    time_array = time.localtime(time_stamp)
    str_date = time.strftime(format_string, time_array)
    return str_date
timestamps=[]
y=[]
my_file = open('pingdata.csv', "rt")
data = csv.reader(my_file)
for row in data:
    # if a%450==0:
    # timestamps.append(row[0])
    # timestamps.append(eval(timestamp_to_timestamp10(int(row[0]))
        # timestamps.append(timestamp_to_date(int(row[0])))
    timestamps.append(row[1])
    # print(timestamps)
    y.append(row[2])
    #     a=a+1
    # else:
    #     a=a+1

plt.plot(timestamps, y)
plt.xticks(rotation=90) # 横坐标每个值旋转90度
plt.xlabel('time')
plt.ylabel('ms')
plt.title('rtt time')
plt.show()
