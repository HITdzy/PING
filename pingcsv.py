#!/usr/bin/env python
import sys
import threading
import ping_imp
import time
import signal
import csv
import matplotlib.pyplot as plt

f = open('pingdata.csv','w',encoding='utf-8',newline="")
csv_writer = csv.writer(f)
csv_writer.writerow(["time","seq","time"])

f1 = open('migration.csv','w',encoding='utf-8',newline="")
csv_writer1 = csv.writer(f1)
csv_writer1.writerow(["migrationtime","zhouqi"])

LOSS_PERIOD_CNT = 10
VALUE_MAX_LEN = 600
PING_INTERVAL_MS = 1000

con = threading.Condition()
stop = False

rtt_index_vec = []
rtt_value_vec = []
loss_index_vec = []
loss_value_vec = []

loss_cnt = 0
total_cnt = 0



def exit(signum, frame):
    # print('stop......')
    global stop,con
    stop = True
    con.acquire()
    con.notify_all()
    con.release()

def get_timestamp_ms():
    t = time.time()
    return (int(round(t * 1000)))

def handle_ping_result(is_timeout, sequence, rtt):
    global rtt_index_vec, rtt_value_vec,loss_index_vec, loss_value_vec, con, loss_cnt, total_cnt
    con.acquire()
    rtt_index_vec.append(sequence)
    rtt_value_vec.append(rtt)
    if is_timeout:
        loss_cnt = loss_cnt + 1
    
    total_cnt = total_cnt + 1
    if total_cnt == LOSS_PERIOD_CNT:
        loss = (loss_cnt * 100) / total_cnt
        loss_index_vec.append(sequence)
        loss_value_vec.append(loss)
        print("%d%% packet loss" % loss)
        total_cnt = 0
        loss_cnt = 0

    if len(rtt_index_vec) == VALUE_MAX_LEN + 1:
        rtt_index_vec = rtt_index_vec[1:]
        rtt_value_vec = rtt_value_vec[1:]
    
    if len(loss_index_vec) == VALUE_MAX_LEN + 1:
        loss_index_vec = loss_index_vec[1:]
        loss_value_vec = loss_value_vec[1:]

    con.notify()
    con.release()

def handle_figure_close(evt):
    exit(None, None)

def do_ping(*target_addr):
    a=0
    temp=0
    while not stop:
        before_timestamp = get_timestamp_ms()
        try:
            valid, sequence, rtt = ping_imp.verbose_ping(target_addr[0])
            date = time.strftime('%Y-%m-%d %X',time.localtime(time.time()))
            #????????????
            csv_writer.writerow([date, sequence, rtt])
            #################################??????csv??????
            if rtt>500:
                rtt=-10
                a=a+1
                print("????????????%d??????:"%(a))
                date1 = time.strftime('%Y-%m-%d %X',time.localtime(time.time()))
                print("??????????????????:%d"%(sequence-temp))
                if sequence-temp<=10:
                    continue
                else:
                    csv_writer1.writerow([date1,sequence-temp])
                temp=sequence
            handle_ping_result(not valid, sequence, rtt)
            after_timestamp = get_timestamp_ms()
            delay = after_timestamp - before_timestamp
            if delay >= PING_INTERVAL_MS:
                continue
            else:
                time.sleep((PING_INTERVAL_MS - delay) / 1000.0)
        except Exception as e:
            # print("error: %s" % e)
            exit(None, None)

def do_display_result():
    plt.ion()
    fig = plt.figure("Network State Monitor")
    fig.canvas.mpl_connect('close_event', handle_figure_close)
    plt.pause(0.01)

    global rtt_index_vec, rtt_value_vec, loss_index_vec, loss_value_vec, con
    while not stop:
        plt.clf()
        plt.subplot(2,1,1)
        con.acquire()
        plt.plot(rtt_index_vec,rtt_value_vec, 'b', label='rtt')
        plt.legend()

        plt.subplot(2,1,2)
        plt.plot(loss_index_vec,loss_value_vec, 'r', label='loss')
        plt.legend()
        con.wait()
        try:
            plt.pause(0.01)
        except:
            None

    plt.clf()
    plt.close()


def main():
    if len(sys.argv) != 2:
        print("Usage: ping_shower.py target_addr")
        sys.exit(1)

    thread_args = (sys.argv[1],)
    thread_ping = threading.Thread(target = do_ping, args = thread_args)
    thread_ping.start()

    signal.signal(signal.SIGINT, exit)
    signal.signal(signal.SIGTERM, exit)

    do_display_result()

    thread_ping.join(10)

if __name__ == '__main__':
    sys.exit(main())
    f.close()
