import sys
from threading import Thread

from gust_server.web.src import Web_Server
from gust_server.src import Gust_Server

#MOVE TO GUST ROOT DIR TO USE

#pass 1 for web anything else for server
if (sys.argv[1] == '1'):

    web_server = Thread(target = Web_Server.Start_Web_App)
    web_server.setDaemon(True)   
    web_server.start()

else:
    server = Thread(target = Gust_Server.Start_Server)
    server.setDaemon(True)   
    server.start()


while True:
    empty = None
