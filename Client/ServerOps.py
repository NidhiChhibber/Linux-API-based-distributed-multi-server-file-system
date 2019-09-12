import datetime


class Server_Init():

    def __init__(self,number,name,serv_proxy,state):
        self.server_proxy=serv_proxy 
        self.name = name
        self.number=number
        self.read_time_accessed = str(datetime.datetime.now())
        self.time_accessed = str(datetime.datetime.now())
        self.time_modified = str(datetime.datetime.now())
        self.time_created = str(datetime.datetime.now())
        self.state=state

       