# -*- coding: utf-8 -*-。
import socket  # for sockets
import sys  # for exit
import threading
import pymysql
import random
import queue
import requests
import re
import time

class checkall(object):
    def __init__(self,t,u,p):
        self.Queue=queue.Queue()
        self.MyIp=''
        self.conn = pymysql.connect(host="127.0.0.1", port=3306, user=u, passwd=p, db="ip", charset="utf8")
        self.cur=self.conn.cursor()
        self.I=0;
        self.lock = threading.Lock()
        self.t=t
        self.getMyIp()

    def getMyIp(self):
        r = requests.get("http://2017.ip138.com/ic.asp")
        self.MyIp = re.findall('\d{0,4}\.\d{0,4}\.\d{0,4}\.\d{0,4}', r.text)[0]


    def check(self):
        while self.Queue.empty() == False:
            ip = self.Queue.get()
            host=ip.split(":")[0]
            #print(host)
            proxies = {
                # "http": "http://60.215.194.73:8888",
                # "https": "http://10.10.1.10:1080",
                "http": "http://" + ip
            }
            try:
                    r = requests.get('http://2017.ip138.com/ic.asp', timeout=60, proxies=proxies)
                    r.encoding = "gb2312"
                    delay = round(r.elapsed.total_seconds(), 2)


            #出现异常不可用
            except:
                print('ip:' + ip + '不可用')
                sqldelete='delete from ip where ip=''\''+ip+'\''
                #print(sqldelete)
                #if self.lock.acquire():
                self.cur.execute(sqldelete)
                    #self.lock.release()


                #找不到不可用
            else:
                #print('a:'+re.findall('\d{0,4}\.\d{0,4}\.\d{0,4}\.\d{0,4}', r.text)[0])
                #print('b:'+self.MyIp)
                #print('c:'+ip)
                if re.findall('\d{0,4}\.\d{0,4}\.\d{0,4}\.\d{0,4}', r.text) == False:
                    print('ip1:' + ip + '不可用')
                    sqldelete = 'delete from ip where ip=''\'' + ip + '\''
                    print(sqldelete)
                    #if self.lock.acquire():
                    #self.cur.execute(sqldelete)
                        #self.lock.release()
                elif re.findall('\d{0,4}\.\d{0,4}\.\d{0,4}\.\d{0,4}', r.text)[0] == host:
                    sqlUpdata='UPDATE ip SET delay='+str(delay) +' WHERE ip=\''+ip+'\''
                    self.cur.execute(sqlUpdata)
                    self.conn.commit()
                    print('高匿ip:' + ip+'  delay:'+str(delay)+'s')
                    self.I = self.I + 1

                elif re.findall('\d{0,4}\.\d{0,4}\.\d{0,4}\.\d{0,4}', r.text)[0] == self.MyIp:
                    sqlUpdata = 'UPDATE ip SET delay=' + str(delay) + ' WHERE ip=\'' + ip + '\''
                    self.cur.execute(sqlUpdata)
                    self.conn.commit()
                    print('普通ip:' + ip + '  delay:' + str(delay) + 's')
                    self.I = self.I + 1


                else:
                    print('ip2:' + ip + '不可用')
                    sqldelete = 'delete from ip where ip=''\'' + ip + '\''
                    print(sqldelete)
                    #if self.lock.acquire():
                    self.cur.execute(sqldelete)
                        #self.lock.release()





    def start(self):
        sql1='select * from ip'
        self.cur.execute(sql1)
        result=self.cur.fetchall()
        count=0
        self.I = 0;
        for ip in result:
            count=count+1
            print(str(count)+':'+ip[0])
            self.Queue.put(ip[0])

        threadslist=[]
        for i in range(int(self.t)):
            t = threading.Thread(target=self.check)
            threadslist.append(t)
            t.start()

        for t in threadslist:
            t.join()

        #加这个不报异常
        self.cur.close()
        print('all:'+str(count)+'/'+str(self.I))


if __name__=='__main__':
        checkall=checkall(1000,'root','root')
        checkall.start()
