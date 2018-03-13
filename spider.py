import requests
import re
import queue
import threading
import getopt
import sys
import pymysql
import time
from bs4 import BeautifulSoup
from check.checkall import checkall
from check.checkHttps import checkHttps
from DBUtils.PooledDB import PooledDB

class spider(object):
      def __init__(self, t, u, p):
            self.MyIp=''
            self.Queue = queue.Queue()
            self.QueueGN=queue.Queue()
            self.QueuePT=queue.Queue()
            self.Threds=t
            self.pool = PooledDB(pymysql, 5, host='localhost', user=u, passwd=p, db='ip', port=3306, blocking=True)
            self.I=0

      def getMyIp(self):
            r=requests.get("http://2017.ip138.com/ic.asp")
            self.MyIp= re.findall('\d{0,4}\.\d{0,4}\.\d{0,4}\.\d{0,4}', r.text)[0]

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


      def check(self):
            global cur
            while self.Queue.empty()==False:
                  ip=self.Queue.get()
                  #print(ip)
                  host = ip.split(":")[0]
                  proxies = {
                        # "http": "http://60.215.194.73:8888",
                        # "https": "http://10.10.1.10:1080",
                        "http": "http://" + ip
                  }
                  try:
                        r = requests.get('http://2017.ip138.com/ic.asp',timeout=10, proxies=proxies)
                        r.encoding = "gb2312"
                        delay=round(r.elapsed.total_seconds(),2)

                  except:
                        continue
                        print('ip:' + ip + '不可用')
                  else:
                        if re.findall('\d{0,4}\.\d{0,4}\.\d{0,4}\.\d{0,4}', r.text)==[]:
                              continue
                        elif re.findall('\d{0,4}\.\d{0,4}\.\d{0,4}\.\d{0,4}', r.text)[0]==host:
                              try:
                                    print('高匿ip:' + ip + '  delay:' + str(delay) + 's')
                                    sql = "INSERT INTO ip VALUE('" + ip + "',TRUE,"+str(delay)+",0,0) "
                                    self.excuteSql(sql)
                              except Exception as e:
                                    print('ip重复:' + ip+str(e))
                                    continue



                        elif re.findall('\d{0,4}\.\d{0,4}\.\d{0,4}\.\d{0,4}', r.text)[0]==self.MyIp:
                              try:

                                    print('普通ip:' + ip + '  delay:' + str(delay) + 's')
                                    sql = "INSERT INTO ip VALUE('" + ip + "',FALSE," + str(delay) + ",0,0) "
                                    self.excuteSql(sql)

                              except:
                                    #没加这个就卡了
                                    print('ip重复:'+ip)
                                    continue


      def getIP(self):
            try:
                  #url1
                  print('正在获取ip')

                  rIP = requests.get('http://www.89ip.cn/apijk/?&tqsl=100000&sxa=&sxb=&tta=&ports=&ktip=&cf=1')
                  rIP.encoding = "gb2312"
                  IPs=re.findall('\d{0,4}\.\d{0,4}\.\d{0,4}\.\d{0,4}:\d{1,5}', rIP.text)
                  for i in range(len(IPs)):

                        self.I=self.I+1
                        self.Queue.put(IPs[i])
                  print('url1获取ip：'+str(self.I))
            except:
                  print('url1获取ip失败')

            try:
                  #url2
                  p = {'http': '127.0.0.1:8080'}
                  headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:56.0) Gecko/20100101 Firefox/56.0'
                        , 'Host': 'www.66ip.cn'
                             }
                  rIP = requests.get(
                        'http://www.66ip.cn/nmtq.php?getnum=999900&isp=0&anonymoustype=0&start=&ports=&export=&ipaddress=&area=0&proxytype=2&api=66ip',
                         headers=headers,timeout=10)

                  IPs = re.findall('\d{0,4}\.\d{0,4}\.\d{0,4}\.\d{0,4}:\d{1,5}', rIP.text)
                  count=0
                  for i in range(len(IPs)):
                        self.I += 1
                        count=count+1
                        self.Queue.put(IPs[i])

                  print('url2获取ip：' + str(count))
                  count = 0
            except:
                  print('url2获取ip失败')

            try:
            #url3
                  url1 = "http://www.xicidaili.com/nn/"
                  header = {'Connection': 'keep-alive',
                            'Cache-Control': 'max-age=0',
                            'Upgrade-Insecure-Requests': '1',
                            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko)',
                            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                            'Accept-Encoding': 'gzip, deflate, sdch',
                            'Accept-Language': 'zh-CN,zh;q=0.8',
                            }
                  for i in range(1, 10):
                        rurl = url1 + str(i)
                        html = requests.get(rurl, headers=header).text
                        soup = BeautifulSoup(html, 'html.parser')
                        tags = soup.select('#ip_list')[0].select('tr')
                        for tag in tags:
                              try:
                                    ip = tag.select('td')[1].string+":"+tag.select('td')[2].string
                                    self.I += 1
                                    self.Queue.put(ip)
                                    count +=1
                                    #sum += 1
                              except IndexError:
                                    pass
                  print('url3获取ip：' + str(count))
                  count=0
            except:
                  print('url3获取ip失败')



            try:
                  #url4
                  url4 = "http://www.kuaidaili.com/free/inha/"
                  header = {'Host': 'www.kuaidaili.com',
                            'Cache-Control': 'max-age=0',
                            'Upgrade-Insecure-Requests': '1',
                            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
                            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                            'Accept-Encoding': 'gzip, deflate, sdch',
                            'Accept-Language': 'zh-CN,zh;q=0.8',
                            'Cookie': 'yd_cookie=edf7538f-6e8f-42a6f381178111fa513b62651a51827dc817; _ydclearance=a46bb1ff737a3ffaf93464b4-f7f3-484d-b800-fd9da69f7504-1513701173; _gat=1; channelid=0; sid=1513692518622292; _ga=GA1.2.1184806693.1513693989; _gid=GA1.2.91565562.1513693989'
                            }
                  for i in range(1, 6):
                        rurl = url4 + str(i)
                        html = requests.get(rurl, headers=header).text
                        iplist = re.findall(
                              '\d{0,4}\.\d{0,4}\.\d{0,4}\.\d{0,4}</td>\n                    <td data-title="PORT">\d{0,6}',
                              html)
                        for ip in iplist:
                              self.Queue.put(str(ip.replace('</td>\n                    <td data-title="PORT">', ':')))
                              self.I+=1
                              count += 1
                  print('url4获取ip:'+str(count))
            except Exception as e:
                  print('url4获取ip失败:'+str(e))

            print('.........get ip finished all:' + str(self.I))


      def start(self):
            self.getMyIp()
            print('MyIp:' + self.MyIp)

            self.getIP()

            # 检测ip是否可用
            for i in range(int(self.Threds)):
                  t = threading.Thread(target=self.check)
                  threadslist.append(t)
                  t.start()
            for i in threadslist:
                  i.join()



if __name__=='__main__':


      t1=time.time()
      threadslist=[]
      opts, args = getopt.getopt(sys.argv[1:], "t:u:p:")
      for op, v in opts:
            if op == '-t':
                  global Threds
                  Threds = v

            if op == '-u':
                  global u
                  u = v

            if op == '-p':
                  global p
                  p = v

      # delete
      checkall = checkall(Threds,u,p)
      checkall.start()

      #spider
      spider=spider(Threds,u,p)
      spider.start()



      #在检测一次
      checkall.start()

      #检测https
      checkHttps=checkHttps(Threds,u,p)
      checkHttps.start()

      t2 = time.time()

      print('the end'+str(t2-t1)+'s  '+'all:'+str(spider.I))





