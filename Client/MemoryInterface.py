 
import time,xmlrpclib,FileSystem,pickle,socket,collections, ServerOps
import time, Memory,datetime

#HANDLE FOR MEMORY OPERATIONS
filesystem = Memory.Operations()
time_delay=0
not_func_servers=[]
read_servers=[]

def time_func(time_t):
        global time_delay
        time_delay=time_t
        

#REQUEST TO BOOT THE FILE SYSTEM
def Initialize_MFS():
    print("File System Initializing......")
    time.sleep(2)
    state = Memory.Initialize()
    print("File System Initialized!")



dicton=collections.OrderedDict()       #dicton- dictonary that stores server numbers as keys and corresponding server instance as the value                                    
no_writing_blocks=0
servers=[]                               #servers- list that holds server names

'''Init- CALLS "Initialize_Servers" FOR REQUESTED NUMBER OF SERVERS, CREATES SERVER INSTANCES USING server-number,server-name, server-handler and server-state.'''
def Init(num_of_servers,port_num):                  #Init- function that updates servernames and port number to initialize servers
    server_name="server1.py"                        #First server name

    for i in range(0,num_of_servers):               #for number of servers requested by the user
        servers.append(server_name)                 #append first server name to 'servers'
        
        server_proxy = Initialize_Servers(server_name,port_num)                #call Initialize_Servers with each server name and port number and get server 
                                                                               #handler for the server
        print "\nConnection established from "+str(server_name)
        server_instance=ServerOps.Server_Init(i+1,server_name,server_proxy,1)   #create server instance for each server using server number,name,server handler 
                                                                                #and state
        dicton[i+1]=server_instance                                                                   
        server_name=server_name.replace(str(i+1),str(i+2))                      #change the server name to next server name
        port_num+=1                                                             #increment the port number and repeat the process for each server


'''Initialize_Servers- INITIALIZES SERVERS, CHECKS THE STATE OF THE SERVERS AND RETURNS THE SERVER PROXY IF SERVER IS ACTIVE.'''
def Initialize_Servers(server_name,port_num):
    server_proxy=""

    server_proxy=xmlrpclib.ServerProxy("http://localhost:"+str(port_num)+"/") #create server handler using port number

    Server_State_Init(server_proxy,server_name)             #call Server_State_Init to establish connection with the servers
   
    return server_proxy                                     #return server handler only if the server is active


'''Server_State_Init- CALLS THE FUNCTION 'Server_State' IN THE RESPECTIVE SERVER TO CHECK THE SERVER STATE. RETURNS ONLY WHEN THE SERVER IS ACTIVE. THIS FUNCTION 
IS ONLY USED THE FIRST TIME A CONNECTION IS TO BE ESTABLISHED WITH THE SERVER'''

def Server_State_Init(server_proxy,server_name):
    A=0
    while A!=1:
        try:
            A=server_proxy.Server_State()                   #call the function in the server to check its state
            return A                                        #if the server is active => A=1 and return 1
        except:                                             #if the server is no active, catch the error
            print "\nWaiting for : "+server_name              #show which server the execution is waiting for
            time.sleep(3)                                   #try to contact the server again after 3 seconds
            Server_State_Init(server_proxy,server_name)     #keep calling itself till the server is active

'''Server_Sate_WR- USED TO CHECK THE SERVER STATE ONLY DURING READ AND WRITES. CALLS 'Server-State' IN THE RESPECTIVE SERVER USING THE SERVER HANDLER AND RETURNS
1 IF THE SERVER IS ACTIVE AND 0 IF THE SERVER IS NOT ACTIVE.'''
def Server_State_WR(server_proxy,server_name):
    try:
        server_proxy.Server_State()                         #call the function in the server to check its state
        return 1                                            #if the server is active return 1
    except:                                                 #if the server is no active, catch the error
        return 0                                            ##if the server is not active return 0    

'''Server_Ack- CALLS Server_State_WR IN CASE OF WRITES AND READS TO CHECK THE SERVER STATE AND BASED ON THE STATE UPDATE THE SERVER INSTANCE WITH 
server_state =0/1.'''
def Server_Ack(server_proxy,server_name):
    RV=Server_State_WR(server_proxy,server_name)            #call the Server_State_WR to check the state. RV=1 if server is active or else 0
    if RV==0:                                               #if the server is not active
        pos=servers.index(server_name)+1                    #get the server number using the server name
        server_inst=dicton.get(pos)                         #get the server instance using the server number
        server_inst.state=0                                 #set the server instance state to 0
    return 1                                                #if server is activerreturn 1

'''Read_Data_Servers: FINDS OUT ON WHCIH SERVERS DOES THE FILE DAT EXIST AND BASED ON WHICH SERVER IS ACTIVE, DATA WILL BE READ FROM'''
def Read_Data_Servers(servernumber):    
    global read_servers                                     #read_servers holds the server names which hold the data and are active currently
    servers_read=[]                                         #list of servers data is to be read from
    ser_num={}
    server_inst= dicton.get(servernumber)                   #get the server instance based on server number

    '''if either one replica is active or both replicas are active, add them to read_servers'''
    '''if the server is not active,add its replicas name to read_servers because at a time one will be active atleat'''
   
    if server_inst.state==1:                                #if the server is active
        read_servers.append(server_inst.name)               #add the server name to the read_servers
        if servernumber%2!=0:                                #if the server is active and is the odd numbered server
            if(dicton.get(servernumber+1).state ==1):                       #if the replica of the server is also active
                read_servers.append(dicton.get(servernumber+1).name)        #add the replic's server name to read_servers
    else:                                                       #if the server is not active
        read_servers.append(dicton.get(servernumber+1).name)    #add the name of the server's replica because at a time the other replica wil be active
    
    '''arrange the server names in read_servers based on increasing server numbers '''
    for i in range(0,len(read_servers)):                    #for all the server names in read_servers
        pos=servers.index(read_servers[i])                  #get the server numbers based ono position og the server name in servers
        ser_num[pos+1]=read_servers[i]                      #save server number as key and server name as value in ser_num{}
    ser_num=sorted(ser_num.items(), key=lambda kv: kv[1])   #sort ser_num{} based on server numbers
    for key,value in ser_num:                               #for every key,value pair in ser_num{}
        servers_read.append(value)                          #add server names to servers_read
    return servers_read                                     #return the ordered list of server identities on whcih data exists 


'''Read_Server_Ack- CHECKS SERVER STATE BEFORE READING FROM THE SERVER AND SHOW IF THE SERVERS ACKNOWLEDGE AND CAN BE READ FROM  '''
def Read_Server_Ack(read_servers):
    time.sleep(time_delay)                                              #delay before read server acknowledgement
    setted_ser_numbers=[]
    '''for all the servers in which data resides, get the server numbers and store in setted_ser_numbers'''
    for i in range(0,len(read_servers)):
        pos=servers.index(read_servers[i])
        setted_ser_numbers.append(pos+1)
    '''for all the server numbers from which data is to be read,get the server handler and server name and call Server_State_WR to check the server state '''
    for i in range(0, len(setted_ser_numbers)):
        server_proxy=dicton.get(setted_ser_numbers[i]).server_proxy     #get the server handler using server intance using server number
        server_name=servers[setted_ser_numbers[i]-1]                    #get the server name using server number
        RV=Server_State_WR(server_proxy,server_name)                    #check if that server is active
        if RV==1:                                                       #if server is active show the acknowledgement
            print ("\nAcknowledgement recieved from "),server_name
        if RV==0:                                                       #if the server is not active show the it is not alive
            pos=servers.index(server_name)+1                            #get  the server number
            server_inst=dicton.get(pos)                                 #get the server instcane
            server_inst.state=0                                         #and set the server state to 0
            print ("\nServer "+server_name+(" not alive"))
        time.sleep(time_delay)                                          #delay before read


'''No_Writing_Blocks- SHOWS SERVER IDENTITIES ON WHICH DATA WILL BE WRITTEN, CHECKS SERVER STATE, SHOWS THE WRITE SERVER ACKNOWLEDGEMENTS.'''       
def No_Writing_Blocks(no_blocks,inode):
    M=[]                                                    #for every active odd server, holds it even numbered replica
    setted_ser_numbers= list(set(inode.ser_numbers))        #get all the server numbers assigned to the file
    print "\nServers to which data will be written : "
    '''get the server numbers assigned to the file,if first server number is even, add it to the set'''
    for i in range(0,len(setted_ser_numbers)-1):              #for all the servers
        setted_ser_numbers.sort()                           #sort the server numbers
        setted_ser_numbers = setted_ser_numbers[:no_blocks] #get the number of servers in which data will be written based on number of blocks to be written
        pos=i+2                                             #for all the servers
        server_inst=dicton.get(pos)                         #get the server instance
        if server_inst.state==1:                            #check if the server state is 1
            if setted_ser_numbers[i]%2!=0:                  #if the server is an odd server
                M.append(setted_ser_numbers[i]+1)           #add its even numbered replica to M
        else:
            M.append(setted_ser_numbers[i]+1) 
    setted_ser_numbers= list(set(setted_ser_numbers+M))     #join server numbers assigned to the inode+their even numbered replicas
    for i in range(0,len(setted_ser_numbers)):              #for all the server numbers 
        if dicton.get(setted_ser_numbers[i]).state==0:      #if the state of that server is not active
            not_func_servers.append(setted_ser_numbers[i])  #add that server to not_func_servers
    setted_ser_numbers= [x for x in setted_ser_numbers if x not in not_func_servers] #servers that will be written to after removing not funcrional servers
    setted_ser_numbers.sort()
    for i in range(0,len(setted_ser_numbers)):
        server_name=servers[setted_ser_numbers[i]-1]        #get server name from server number
        print server_name                                   #print server name o which data will be written
   
    time.sleep(time_delay)                                  #delay after printing server identities and before server acknowledgments

    '''for all the server numbers on whcih data is to be written, get the server handler and server name, call Server_State_WR to get ackownledgement from the
    servers. set server state as 0 if server is not active'''
    for i in range(0, len(setted_ser_numbers)):
        server_proxy=dicton.get(setted_ser_numbers[i]).server_proxy
        server_name=servers[setted_ser_numbers[i]-1]
        RV=Server_State_WR(server_proxy,server_name)
        if RV==1:
            print ("\nAcknowledgement recieved from "),server_name    
        if RV==0:
            pos=servers.index(server_name)+1
            server_inst=dicton.get(pos)
            server_inst.state=0
            print ("\nServer "+server_name+(" not alive"))
   
    time.sleep(time_delay)                                  #delay before writing

def Initialize_My_FileSystem():
    print("File System Initializing......")
    time.sleep(2) 
    i=0
    for key,value in dicton.items():
        ab=value.server_proxy
        i+=1
        try:
            state = ab.Initialize()
            value.time_accessed = str(datetime.datetime.now())
            print("File System "+ str(i) +" Initialized!")
            socket.setdefaulttimeout(5)
        except socket.error as errno:
            print "\nSERVER ERROR WHILE INITIALIZING FILE SYSTEM "+ str(i)+"." +" ERROR NO : ",errno.errno,"ERROR : ",errno.strerror
            
#REQUEST TO FETCH THE INODE FROM INODE NUMBER FROM LOCAL FILE SYSTEM
def inode_number_to_inode_MFS(inode_number):
    return filesystem.inode_number_to_inode(inode_number)    

#REQUEST TO FETCH THE INODE FROM INODE NUMBER FROM SERVER
'''is called only when the file system is being initialized on the servers'''
def inode_number_to_inode(inode_number):
    data= pickle.dumps(inode_number)
    for key,value in dicton.items():
        ab=value.server_proxy
        try:
            m=(ab.inode_number_to_inode(data))
            socket.setdefaulttimeout(5)
            return pickle.loads(m)
        except socket.error as errno:
            print"\nSERVER ERROR WHILE FETCHING INODE.","ERROR NO : ",errno.errno,"ERROR : ",errno.strerror
            exit(0)
    
#REQUEST THE DATA FROM THE SERVER
def get_data_block(block_number,servernumber):
    for j in range(1,len(dicton)+1):                                #check which servers are active
        Server_Ack(dicton.get(j).server_proxy,dicton.get(j).name)
    data= pickle.dumps(block_number)                                #pickle the data to be sent over the network
    server_inst= dicton.get(servernumber)                           #get the server instance
    if server_inst.state==1:                                        #if the server is still active
        if(servernumber%2!=0):                                      #if the server is an odd numbered server
            if(dicton.get(servernumber+1).state==1):                #and the replica of the server is also active
                if (server_inst.read_time_accessed<dicton.get(servernumber+1).read_time_accessed): #check if the server was accessed before the replica
                    
                    ab=server_inst.server_proxy                     #if yes then get server instance in ab
                    server_inst.read_time_accessed=str(datetime.datetime.now())
                    reading_from=server_inst.name
                else:                                               #if the replica was used before the server
                    ab=dicton.get(servernumber+1).server_proxy      #get server instance of the replica in ab
                    dicton.get(servernumber+1).read_time_accessed=str(datetime.datetime.now())
                    reading_from=dicton.get(servernumber+1).name
            else:                                                   #if the server is active but the replica isnt active
                ab=server_inst.server_proxy                         #get server instance in ab
                server_inst.read_time_accessed=str(datetime.datetime.now())
                reading_from=server_inst.name
        else:                                                       #if it is an even numbered server
                ab=server_inst.server_proxy                         #implies that its replica is not active, get server instance in ab
                server_inst.read_time_accessed=str(datetime.datetime.now())
                reading_from=server_inst.name
    else:                                                           #if the server is not active
        ab=dicton.get(servernumber+1).server_proxy                  #get server instance of the replica in ab
        dicton.get(servernumber+1).read_time_accessed=str(datetime.datetime.now())
        reading_from=dicton.get(servernumber+1).name
    try:
        print ("Reading from: "),reading_from
        m=pickle.loads(ab.get_data_block(data))                     #call the get_data_block function on the server specified by ab
        socket.setdefaulttimeout(5)                                 #wait for 5 seconds if no reply from the server
        return_value=m[0]
        return_message=m[1]
        if return_value==-1:
            print return_message
        else:
            return ''.join(return_value)
    except socket.error as errno:
        print"\nSERVER ERROR WHILE GETTING BLOCK DATA.","ERROR NO :  ",errno.errno,"ERROR : ",errno.strerror
        exit(0)


#REQUESTS THE VALID BLOCK NUMBER FROM THE SERVER 
def get_valid_data_block():
    blocks=[]
    mini={}
    i=1
    for j in range(1,len(dicton)+1):                            #for all servers to which the connection was established
        Server_Ack(dicton.get(j).server_proxy,dicton.get(j).name) #check the server state
    for y in range(0,len(dicton)/2):                            #for every alternate server  
        
        if dicton.get(i).state==1:                              #if the server is active
            mini[i]=dicton.get(i).time_accessed                 #add the server number as value and server time modified as key  in mini{}
            i+=2                                                #every alternate odd number server to whcih connection was established
        else:                                                   #if the server is not active
            mini[i+1]=dicton.get(i+1).time_accessed             #add the server number of the repica as value and its modification time as key in mini{}
            i+=2   
    lru=min(mini.keys(), key=(lambda k: mini[k]))               #find the last modification time server number
    val=dicton.get(lru)                                         #get server instance from the serevr number
    ab=val.server_proxy                                         #get the server handler in ab
    try:      
        m=pickle.loads(ab.get_valid_data_block() )
    
        val.time_accessed=str(datetime.datetime.now())                           
        socket.setdefaulttimeout(5)
        return_value=m[0]
        return_message=m[1]
        if return_value==-1:
            print return_message
        else:
            blocks.append(return_value)
            blocks.append(val.number)
            return blocks   
    except socket.error as errno:
        print"\nSERVER ERROR WHILE GETTING VALID DATA BLOCK.","ERROR NO : ",errno.errno,"ERROR : ",errno.strerror
        exit(0)


def free_data_block_MFS(block_number):
    filesystem.free_data_block((block_number))          
    
#REQUEST TO MAKE BLOCKS RESUABLE AGAIN FROM SERVER
def free_data_block(block_number,server_number):
    data= pickle.dumps(block_number)                            #pickle the data to eb sent over the network
    for j in range(1,len(dicton)+1):                            #check which servers are active
        Server_Ack(dicton.get(j).server_proxy,dicton.get(j).name)
    for i in range(0,2):                                        #for get server intance of the server identified by server_number
        server_inst= dicton.get(server_number+i)                # and of its replica
   
        if server_inst.state==1:                                #if the server/replica is active
            ab=server_inst.server_proxy                         #get its server handler in ab
            try:
                ab.free_data_block(data)                        #call the function using the server handler
                if(server_number%2==0):                         #if its even number server, no need to go to the replica since even number servers are only added if
                    break                                       #the odd numbered server is not active
            except socket.error as errno:
                print"\nSERVER ERROR WHILE FREEING DATA BLOCK.","ERROR NO : ",errno.errno,"ERROR : ",errno.strerror
                exit(0)
 
#REQUEST TO WRITE DATA ON THE THE SERVER
def update_data_block(block_number, block_data,server_number):
 
    block_number=pickle.dumps(block_number)
    block_data=pickle.dumps(block_data)
    serv_instance= dicton.get(server_number)
    
    if ( server_number%2==0):                                   #if it is an even numbered server- implied its replica is not active
        ab=serv_instance.server_proxy                           #get the server instance in ab
        print "\nWriting to : ",serv_instance.name
        
        try:
            ab.update_data_block(block_number, block_data)      #write to the server specified by ab
            socket.setdefaulttimeout(5)
        except socket.error as errno:
            print"\nSERVER ERROR WHILE UPDATING DATA BLOCK.","ERROR NO : ",errno.errno,"ERROR : ",errno.strerror
            exit(0)
    else:                                                       #if it is a odd numbered server
        if(serv_instance.state==0):                             #and it is not active
            print "\nWriting to : ",dicton.get(server_number+1).name 
            ab=dicton.get(server_number+1).server_proxy         #get the server instance of the replica in ab
           
            try:
                ab.update_data_block(block_number, block_data)  #write to the server specified by ab
                socket.setdefaulttimeout(5)
            except socket.error as errno:
                print"\nSERVER ERROR WHILE UPDATING DATA BLOCK.","ERROR NO : ",errno.errno,"ERROR : ",errno.strerror
                exit(0)
        if(serv_instance.state==1):                             #if the server is odd numbered and active
            ab=serv_instance.server_proxy                       #get server instance in av
            print "\nWriting to : ",serv_instance.name        
            try:         
                ab.update_data_block(block_number, block_data)  #write to the server specified by ab
                socket.setdefaulttimeout(5)
            except socket.error as errno:
                print"\nSERVER ERROR WHILE UPDATING DATA BLOCK.","ERROR NO : ",errno.errno,"ERROR : ",errno.strerror
                exit(0)
            if(dicton.get(server_number+1).state==1):           #if the replica is also active
                ab=dicton.get(server_number+1).server_proxy     #get server instance of replica in ab
                print "\nWaiting to write to the replica : ",dicton.get(server_number+1).name
                time.sleep(time_delay)
                Server_Ack(dicton.get(server_number+1).server_proxy,dicton.get(server_number+1).name) #check all servers states before writing
                if(dicton.get(server_number+1).state==1):       #check the replica state again
                    try:
                        print "\nWriting to the replica : ",dicton.get(server_number+1).name
                        ab.update_data_block(block_number, block_data) #write to the server specified by ab
                        socket.setdefaulttimeout(5)
                    except socket.error as errno:
                      
                        print"\nSERVER ERROR WHILE UPDATING DATA BLOCK.","ERROR NO : ",errno.errno,"ERROR : ",errno.strerror
                        exit(0)
                else:                                           #if replica is not active  
                    print "\nReplica not active : ",dicton.get(server_number+1).name

def update_inode_table_MFS(inode, inode_number):
    filesystem.update_inode_table(inode, inode_number)

#REQUEST TO UPDATE THE UPDATED INODE IN THE INODE TABLE FROM SERVER
def update_inode_table(inode, inode_number):
    ab=''
    inode=pickle.dumps(inode)
    inode_number=pickle.dumps(inode_number)
    for key,value in dicton.items():
        ab=value.server_proxy
        try: 
            ab.update_inode_table(inode, inode_number)
            socket.setdefaulttimeout(5)
        except socket.error as errno:
            print"\nSERVER ERROR WHILE UPDATING INODE TABLE.","ERROR NO : ",errno.errno,"ERROR : ",errno.strerror
            exit(0)

#status_MFS- SHOW THE STATUS OF DIRECTORIES/FILES
def status_MFS():
    return filesystem.status()

#REQUEST FOR THE STATUS OF FILE SYSTEM FROM SERVER
def status():
    server_number=input("\nEnter server number for which status is to be shown : ")
    server_inst= dicton.get(server_number)
    ab=server_inst.server_proxy
    try:
        stat=pickle.loads(ab.status())
        return stat
        socket.setdefaulttimeout(5)          
    except socket.error as errno:         
        return "\nSERVER ERROR WHILE FETCHING STATUS.","ERROR NO : ",errno.errno,"ERROR : ",errno.strerror
    