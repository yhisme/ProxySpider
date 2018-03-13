import time, os
import sys
import getopt


def re_exe(cmd, inc=500):
    while True:
        print(cmd)
        os.system(cmd)
        time.sleep(inc)


opts, args = getopt.getopt(sys.argv[1:], "t:d:u:p:")
for op, v in opts:
    if op == '-t':
          global Threds
          Threds=v
    if op== '-d':
        global d
        d=v
    if op== '-u':
        global u
        u=v

    if op == '-p':
        global p
        p = v
        #py -3 start.py -t 1000 -d 1000 -u root -p root
re_exe("py -3 spider.py -t "+str(Threds)+" -u "+str(u) +" -p "+str(p) ,int(d))
