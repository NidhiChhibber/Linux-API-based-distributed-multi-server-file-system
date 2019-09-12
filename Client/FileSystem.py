import MemoryInterface, AbsolutePathNameLayer,FileNameLayer,xmlrpclib, collections,os,time,datetime

def Initialize_My_FileSystem():
    MemoryInterface.Initialize_My_FileSystem()
    AbsolutePathNameLayer.AbsolutePathNameLayer().new_entry('/', 1)
def Initialize_My_FileSystem_MFS():
    MemoryInterface.Initialize_MFS()
    AbsolutePathNameLayer.AbsolutePathNameLayer().new_entry_MFS('/', 1)

#HANDLE TO ABSOLUTE PATH NAME LAYER
interface = AbsolutePathNameLayer.AbsolutePathNameLayer()
l=FileNameLayer.FileNameLayer()

class FileSystemOperations():

    #MAKES NEW DIRECTORY
    def mkdir(self, path):
        interface.new_entry_MFS(path, 1)

    #CREATE FILE
    def create(self, path):
        interface.new_entry_MFS(path, 0)
        

    #WRITE TO FILE
    def write(self, path, data, offset):
        interface.write(path, offset, data)
        
      

    #READ
    def read(self, path, offset=0, size=-1):
        read_buffer = interface.read(path, offset, size)
        if read_buffer != -1: print(path + " : " + read_buffer)
    
    #DELETE
    def rm(self, path):
        interface.unlink(path)


    #MOVING FILE
    def mv(self, old_path, new_path):
        interface.mv(old_path, new_path)


    #CHECK STATUS
    def status(self):
        option=input("Enter 1 for Local File System status, 2 for Server status: ")
        if option==1:
            print"\n",(MemoryInterface.status_MFS())
        else:
            print"\n",(MemoryInterface.status())

    
            
            


if __name__ == '__main__':
    #DO NOT MODIFY THIS
    
    my_object = FileSystemOperations()
    

    
    num_of_servers= input("Enter the number of servers: ")
    #for i in range (0,num_of_servers):
        #os.system("gnome-terminal -e 'bash -c \"/media/sf_share/server"+str(i+1)+"/ServerStub"+str(i+1)+".py; exec bash\"'")
        
        
    time_t=input("Enter time t in seconds: ")
    MemoryInterface.time_func(time_t)
    
    port_num=input("Enter the first port number: ")
    
    MemoryInterface.Init(num_of_servers,port_num)
    
    Initialize_My_FileSystem()
    Initialize_My_FileSystem_MFS()
    text=[]
    while text!= "exit":
        text= raw_input("\nEnter input command: \nTo create a directory: 'mkdir PATH' \nTo create a file: 'create PATH' \nTo write to a file: 'write'\nTo read froma file: 'read' \nTo move a file from oldpath to newpath: 'mv OLDPATH NEWPATH' \nTo remove a file: 'rm PATH' \nTo see the status: 'status' \nTo quit: 'exit'  \n$")
        text1=text.split(' ')
        print text
        if len(text1) >1:
            check=text1[1]
        if text1[0]=="mkdir":

            my_object.mkdir(check)
        if text1[0]=="create":

            my_object.create(check)
        if text1[0]=="mv":
    
            my_object.mv(text1[1],text1[2])
        if text1[0]=="read":
            path=raw_input("Enter the path: ")
            offset=input("Enter the offset: ")
            length=input("Enter the length: ")
            my_object.read(path,offset,length)
        
        if text1[0]=="write":
            path=raw_input("Enter the path: ")
            data= raw_input("Enter the data: ")
            offset = input("Enter the offset: ")
            my_object.write(path,data*1024,offset)
        
        if text1[0]=="status":
        
            my_object.status()
        if text1[0]=="rm":
    
            my_object.rm(check)
        if text1[0]=="unlink":
            interface.unlink(text1[1])
    
        
