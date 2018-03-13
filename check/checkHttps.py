import socket  # for sockets
import sys  # for exit
import threading
import pymysql
import random
import queue
import requests
import re
import time
from DBUtils.PooledDB import PooledDB
class checkHttps(object):
    def __init__(self,t,u,p):
        self.Queue=queue.Queue()
        self.MyIp=''
        self.pool = PooledDB(pymysql, 5, host='localhost', user=u, passwd=p, db='ip', port=3306,blocking=True)  # 5为连接池里的最少连接数
        self.I=0;
        self.lock = threading.Lock()
        self.t=t
        self.semaphore = threading.BoundedSemaphore(1)

    def excuteSql(self, s):
        conn = self.pool.connection()
        cur = conn.cursor()
        SQL = s
        r = cur.execute(SQL)
        conn.commit()
        r = cur.fetchall()

        cur.close()
        conn.close()
        return r


    def check(self):
        while self.Queue.empty() == False:
            ip = self.Queue.get()
            host=ip.split(":")[0]
            #print(host)
            proxies = {
                # "http": "http://60.215.194.73:8888",
                # "https": "http://10.10.1.10:1080",
                "https": ip
            }
            try:
                for i in range(2):
                    r = requests.get('https://www.baidu.com/', timeout=60, proxies=proxies)
                    r.encoding = "utf-8"
                    #print(ip+":"+r.text)
                    delay = round(r.elapsed.total_seconds(), 2)

            except Exception as e:
                #print(e)
                print('wrong3:' + ip + 'is not HTTPS')
                sqlUpdata = 'UPDATE ip SET isHTTPS=0' + ' WHERE ip=\''+ip+ '\''
                self.excuteSql(sqlUpdata)

                continue

                    #self.lock.release()


                #找不到不可用
            else:
                if r.status_code==200:
                    print(ip + 'is HTTPS')
                    sqlUpdata = 'UPDATE ip SET isHTTPS=1' + ' WHERE ip=\'' + ip + '\''
                    self.excuteSql(sqlUpdata)
                    self.I=self.I+1
                else:
                    #不是高匿
                    continue





    def start(self):
        sql1='select * from ip'
        result=self.excuteSql(sql1)
        count=0
        self.I = 0;
        for ip in result:
            count=count+1
            print('检测数据库ip是否为https:'+str(count)+':'+ip[0])
            self.Queue.put(ip[0])

        threadslist=[]
        for i in range(int(self.t)):
            t = threading.Thread(target=self.check)
            threadslist.append(t)
            t.start()

        for t in threadslist:
            t.join()
        print('all:'+str(count)+'/'+str(self.I))



if __name__=='__main__':
        checkHttps=checkHttps(1000,'root','root')
        checkHttps.start()
        checkHttps.start()

