import socket  # for sockets
import sys  # for exit
import threading
import pymysql
import random
import queue
import requests
import re
import pymysql
import time
from DBUtils.PooledDB import PooledDB


class checkall(object):
    def __init__(self,t,u,p):
        self.Queue=queue.Queue()
        self.MyIp=''
        #self.conn = pymysql.connect(host="127.0.0.1", port=3306, user=u, passwd=p, db="ip", charset="utf8")
        #self.cur=self.conn.cursor()
        self.I=0
        self.lock = threading.Lock()
        self.t=t
        self.getMyIp()
        self.semaphore = threading.BoundedSemaphore(1)
        self.pool = PooledDB(pymysql, 5, host='localhost', user=u, passwd=p, db='ip', port=3306,blocking=True)  # 5为连接池里的最少连接数

    def excuteSql(self,s):
        conn=self.pool.connection()
        cur = conn.cursor()
        SQL = s
        r = cur.execute(SQL)
        conn.commit()
        r = cur.fetchall()
        cur.close()
        conn.close()
        return r

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
                print('wrong3:' + ip + '不可用')
                sqldelete='delete from ip where ip=''\''+ip+'\''
                self.excuteSql(sqldelete)

                    #self.lock.release()
                continue


                #找不到不可用
            else:
                try:
                    rip=re.findall('\d{0,4}\.\d{0,4}\.\d{0,4}\.\d{0,4}', r.text)[0]
                except:
                    print('wrong1:' + ip + '不可用')
                    sqldelete = 'delete from ip where ip=''\'' + ip + '\''
                    self.excuteSql(sqldelete)
                    continue


                if rip == host:
                    tC=str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
                    sqlUpdata='UPDATE ip SET delay='+str(delay) +' ,crawlTime=\''+tC+'\' WHERE ip=\''+ip+'\''
                    self.excuteSql(sqlUpdata)
                    print('高匿ip:' + ip+'  delay:'+str(delay)+'s')
                    self.I = self.I + 1

                elif rip == self.MyIp:
                    tC = str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
                    sqlUpdata = 'UPDATE ip SET delay=' + str(delay) +' ,crawlTime=\''+tC+ '\' WHERE ip=\'' + ip + '\''
                    self.excuteSql(sqlUpdata)
                    print('普通ip:' + ip + '  delay:' + str(delay) + 's')
                    self.I = self.I + 1


                else:
                    print('wrong2:' + ip + '不可用')
                    sqldelete = 'delete from ip where ip=''\'' + ip + '\''
                    self.excuteSql(sqldelete)




    def start(self):
        sql1='select * from ip'
        result=self.excuteSql(sql1)
        count=0
        self.I = 0;
        for ip in result:
            count=count+1
            print('检测数据库ip:'+str(count)+':'+ip[0])
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
        checkall=checkall(1000,'root','root')
        checkall.start()

