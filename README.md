# ProxySpider
一款python开发的代理池，及动态代理
# 依赖库：
        requests:pip install requests
        bs4:pip install bs4
        pymysql:pip install pymsql
        PooledDB:pip install PooledDB
       
# Easy start:
## 1.代理池
        py -3 start.py -t 10 -d 1000 -u root -p root
        （-t 线程数 -d 每隔多少时间爬取一次ip -u 数据库账号 -p 数据库密码)
        
## 2.动态代理
        py -3 proxy.py -t 8080 -d 1.0 -u root -p root
        （-t 监听本地端口 -d 选取数据库延迟低于多少s的代理  -u 数据库账号 -p 数据库密码)
        
  
# what it can :
         1.ProxySpider能够爬取各大代理网站ip，并且对每个ip进行分类验证：1.验证有效性.2.验证是否为https.3.测试代理ip延迟.验证结束后将ip存入数据库。
         2.ProxySpider的proxy.py是一个附加功能，它是一个本地代理，能够从数据库中随机选取一个ip转发https/http报文。也就是能够实现每次使用不同ip访问同一个网站。
         
# 如有问题欢迎issues！
