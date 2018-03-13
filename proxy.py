import socket  # for sockets
import sys  # for exit
import threading
import pymysql
import random
from DBUtils.PooledDB import PooledDB
import getopt





def excuteSql(s):
    conn = pool.connection()
    cur = conn.cursor()
    SQL = s
    r = cur.execute(SQL)
    conn.commit()
    r = cur.fetchall()
    cur.close()
    conn.close()
    return r

def getHttpsIP(delay):
    sql1='select count(*) from ip where isHTTPS=1 AND delay<'+str(delay)
    print(sql1)
    result=excuteSql(sql1)

    sql2='select * from ip where isHTTPS=1 AND delay<'+str(delay)+' limit '+str(random.randint(0, (int(result[0][0])-1)))+',1'
    print(sql2)
    result=excuteSql(sql2)

    newIP=result[0][0]
    return newIP

def getHttpIP(delay):
    sql1='select count(*) from ip WHERE delay< '+str(delay)
    print(sql1)
    excuteSql(sql1)
    result=excuteSql(sql1)

    if result[0][0]==0:
        print('delay wrong')
        return None
    else:
        sql2='select * from ip  WHERE delay< '+str(delay)+' '+'  limit '+str(random.randint(0, result[0][0]-1))+',1'

        result=excuteSql(sql2)
        newIP=result[0][0]
        return newIP


def copy(connect1, connect2):
    # 待完善 异常等等
    try:
        while True:
            data = connect1.recv(4096)
            connect2.send(data)
    except ConnectionResetError:
        pass
    except BrokenPipeError:
        pass
    except ConnectionAbortedError:
        pass


def handle_request(client, address):


    #获取浏览器新请求，解析请求
    buf = client.recv(4096)
    ip = None
    try:
        req=buf.decode('utf-8')
        print(str(address) + ': 请求数据包-------\r\n' + buf.decode('utf-8'))
    except UnicodeDecodeError:
        print("非文本信息-加密数据")
        ip=getHttpsIP(delay)
    else:
        if req[0:8] == 'CONNECT ':
            ip = getHttpsIP(delay)
            print('use https ip' + str(ip) + '................')
        else:
            ip = getHttpIP(delay)
            print('use  ip' + str(ip) + '\r\n')


    print('wrong:'+str(type(ip)))
    print(ip)
    ip = ip.split(':')
    host = str(ip[0])
    port = int(ip[1])

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    # 将数据发送至代理服务器
    s.sendall(buf)

    # 盲转 浏览器 -> 服务器    服务器 -> 浏览器
    t1 = threading.Thread(target=copy, args=(s, client))
    t2 = threading.Thread(target=copy, args=(client, s))
    t1.start()
    t2.start()

if __name__ == '__main__':

    opts, args = getopt.getopt(sys.argv[1:], "t:u:p:d:")
    for op, v in opts:
        if op == '-t':
            global port
            port = v

        if op == '-u':
            global u
            u = v

        if op == '-p':
            global p
            p = v

        if op == '-d':
            global delay
            delay = v

    pool = PooledDB(pymysql, 5, host='localhost', user=u, passwd=p, db='ip', port=3306, blocking=True)
    sockServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sockServer.bind(('0.0.0.0', int(port)))
    sockServer.listen(500)
    try:
        while True:

            # 每一个新连接，建立一个线程
            connection, address = sockServer.accept()
            print("新连接：" + str(address))
            t = threading.Thread(target=handle_request, args=(connection, address))
            t.start()

    except KeyError:
        sockServer.close()
        sys.exit(0)




