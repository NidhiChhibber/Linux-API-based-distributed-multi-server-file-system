'''
THIS MODULE IS INODE LAYER OF THE FILE SYSTEM. IT INCLUDES THE INODE DEFINITION DECLARATION AND GLOBAL HANDLE OF BLOCK LAYER OF API.
THIS MODULE IS RESPONSIBLE FOR PROVIDING ACTUAL BLOCK NUMBERS SAVED IN INODE ARRAY OF BLOCK NUMBERS TO FETCH DATA FROM BLOCK LAYER.
'''
import datetime, config, BlockLayer, InodeOps, MemoryInterface, copy,InodeNumberLayer, math,time

#HANDLE OF BLOCK LAYER
interface = BlockLayer.BlockLayer()

no_blocks_needed=0

class InodeLayer():

    #RETURNS BLOCK NUMBER FROM RESPECTIVE INODE DIRECTORY
    def INDEX_TO_BLOCK_NUMBER(self, inode, index):
        if index == len(inode.blk_numbers): return -1
        return inode.blk_numbers[index]


    #RETURNS BLOCK DATA FROM INODE
    def INODE_TO_BLOCK(self, inode, offset):
        index = offset / config.BLOCK_SIZE
        block_number = self.INDEX_TO_BLOCK_NUMBER(inode, index)
        if block_number == -1: return ''
        else: return interface.BLOCK_NUMBER_TO_DATA_BLOCK(block_number)


    #MAKES NEW INODE OBJECT
    def new_inode(self, type):
        return InodeOps.Table_Inode(type)


    #FLUSHES ALL THE BLOCKS OF INODES FROM GIVEN INDEX OF MAPPING ARRAY  
    def free_data_block(self, inode, index):
        B=inode.ser_numbers
        for i in range(0, len(inode.blk_numbers)-1):
            interface.free_data_block(inode.blk_numbers[i],B[i])
         
           
            
    def free_data_block_MFS(self, inode, index):
        for i in range(index, len(inode.blk_numbers)):
            interface.free_data_block_MFS(inode.blk_numbers[i])
            inode.blk_numbers[i] = -1


    ''' #IMPLEMENTS WRITE FUNCTIONALITY
    def write(self, inode, offset, data):
        index = offset / config.BLOCK_SIZE         
        last_blk_index = self.INDEX_TO_BLOCK_NUMBER(inode, index)  #FETCHING COMPLETE BLOCK OF GIVEN OFFSET
        
        if last_blk_index == -1: last_blk_index = 0     #IF -1, MEANS DATA IS FRESHLY WRITTEN
        inode, prev_data = self.read(inode, offset - (offset % config.BLOCK_SIZE), offset % config.BLOCK_SIZE)  #TRIMMING DATA ACCORDING TO OFFSET
        if prev_data == -1:         #IF GIVEN OFFSET EXCEEDS THE FILE LENGTH
            print("Error(write) InodeLayer: Offset exceeds the file length")
            return inode
        data = prev_data[: offset % config.BLOCK_SIZE] + data 
        self.free_data_block(inode, index)  #INVALIDIATING ALL BLOCKS INCLUDING AND AFTER OFFSET BLOCK
        
        inode.size = (index * config.BLOCK_SIZE) + len(data) + 1 if last_blk_index != 0 else len(data) + 1#UPDATING SIZE
        blocks = [data[i:i+config.BLOCK_SIZE] for i in range(0, len(data), config.BLOCK_SIZE)] #BREAKING DATA IN BLOCKS
        total_blocks = len(blocks)#check if total data exceeds required length
        
        if total_blocks > len(inode.blk_numbers):  #IF DATA EXCEEDS THE MAXIMUM ALLOCATED SIZE
            print("Error InodeLayer: Data exceeds the given size. Incomplete write!")
            total_blocks = len(inode.blk_numbers)
            inode.size = total_blocks * config.BLOCK_SIZE  #UPDATING SIZE 
        
        for i in range(0, total_blocks):     #WRITING BLOCKS
            new_valid_block_number = interface.get_valid_data_block()
            inode.blk_numbers[i] = new_valid_block_number
            interface.update_data_block(new_valid_block_number, blocks[i])

        inode.time_accessed = datetime.datetime.now()
        inode.time_modified = datetime.datetime.now() 
        return inode  #RETURNS INODE TO INODE NUMBER LAYER TO UPDATE INODE AT SERVER'''


  
         #IMPLEMENTS WRITE FUNCTIONALITY
    def write(self, inode, offset, data):

        no_blocks_needed=self.ceilings(math.ceil(len(data))/config.BLOCK_SIZE)
        B= inode.ser_numbers
        if inode.blk_numbers[0]==-1:
            A=inode.blk_numbers
            
            X=[]
            for i in range(0,len(A)):
                X=interface.get_valid_data_block()
                A[i]=X[0]
                B[i]=X[1]
            
           
  
        '''TYPE ERROR'''

        if(inode.type!=0):
           print "ERROR: Inode type not file"
           return -1

        
        '''OFFSET ERROR'''
        if(offset>inode.size):
            print "ERROR: Offset greater than file size"   
            return -1
        '''OFFSET ERROR'''
        if(offset<0):
            print "ERROR: Offset less than 0"
            return -1


        '''TRUNCATE DATA'''
        mfs=(len(inode.blk_numbers))*config.BLOCK_SIZE
	      
        if(offset>=mfs):
            print "ERROR: Offset greater than inode size"                   #mfs -> Maximum File Size
            return -1
        index=int(offset/config.BLOCK_SIZE)                                 #Index block=Block number with the offset
        block_data=[]                                                       #To get the data of the index block
    
        q=0                                                                 #To store the star
        count=0
        d=mfs-inode.size 
        
        if(index==0):                                                       #If index block is the first block
            if(len(data)-offset>mfs):                                       #If length of data exceeds the maximum file size Data is truncated at the end by the 
                data=data[0:mfs-offset]                                     #remaining space in the file 
                print "Data larger than file size. Data truncated."
                
        else:                                                               #If index block is not the first block
            if(inode.size==mfs):                                            #If inode is filled
                if(offset<mfs):                                             #But offset is lesser than the EOF
                    d=mfs-offset                                            #d stores the space in which new data is to be appended before EOF
                    if(len(data)>d):                                        #if the data is longer than the space in the file after offset
                        data=data[0:d]                                      #Truncates the data by keeping only the length=space available      
                        print "Data larger than file size. Data truncated."  
                
            else:                                                           #If the file is not full,
                d=mfs-inode.size                                            #d stores the space available in the inode
                if(len(data)>d):                                            #If the length of data is more than the space in inode
                    data=data[0:d]                                          #Truncates the data by only keeping the length=space available
                    print "Data larger than file size. Data truncated."
   
        block_data=MemoryInterface.get_data_block(inode.blk_numbers[index],B[index])                 #Gets previous data from the index block
        b_d=[]                                                              #b_d stores the data in the index block
        b_d=block_data.replace('\x00',"") 
       
                                               
        if index==0:                                                        #If the index block is first block
                b_d=b_d[0:offset]+data                                      #data to be written=previous data upto offset+new data
                
        else:
            for i in range(0,index): 
                count+=config.BLOCK_SIZE                                    #If index block is not first block, for number of blocks before index block
                q=offset-count                                              #increment the offset by block size to get new offset
                b_d=b_d[0:q]+data                                           #Data to be written= previous data upto new offset+newdata
            
        if(len(b_d)>config.BLOCK_SIZE):
            no_blocks_needed=self.ceilings(math.ceil(len(b_d))/config.BLOCK_SIZE)
           
        MemoryInterface.No_Writing_Blocks(no_blocks_needed,inode)

        '''WRITING DATA'''
        if len(b_d)>config.BLOCK_SIZE:                                         #If len of data to be written is greater than size of 1 block
           
            interface.free_data_block(inode.blk_numbers [index],B[index])                                #Free the first data block
 
            interface.update_data_block(inode.blk_numbers[index],b_d[0:config.BLOCK_SIZE],B[index])     #Write the first (blocksize) characters of the data to be written
     
            inode.time_accessed=str(datetime.datetime.now())[:19]                #Update access and modification time
            inode.time_modified=str(datetime.datetime.now())[:19]
            a=copy.deepcopy(config.BLOCK_SIZE)                                 #Copy blocksize into a & b without pointing to the same object
            b=copy.deepcopy(config.BLOCK_SIZE)
            x=len(b_d)/8
           
            

            for i in range(1,no_blocks_needed):                  #Executing for the rest of the blocks
                y=b+a      
                                                             
                interface.free_data_block(inode.blk_numbers[index+i],B[index+i])                          #Free all the blocks after index block
                interface.update_data_block(inode.blk_numbers[index+i],b_d[b:y],B[index+i])               #In block after the index bloc, write the data left after first block
                
                inode.time_accessed=str(datetime.datetime.now())[:19]
                inode.time_modified=str(datetime.datetime.now())[:19]
                b=b+a
                inode.size=offset+len(data)                                    #Increment inode size= length of the data written
                
            
                
        else:
             for i in range(0,(inode.size/config.BLOCK_SIZE)-1):                   #If the length of the data to be written is less than the block size
             
                interface.free_data_block(inode.blk_numbers[index+i],B[index+i])                          #Free all the data blocks after index block and update the index block with
             interface.update_data_block(inode.blk_numbers[index],b_d,B[index+i])                         #the data to be written
        
             inode.time_accessed=str(datetime.datetime.now())[:19]
             inode.time_modified=str(datetime.datetime.now())[:19]
             inode.size=offset+len(data)
        inode.blk_numbers=inode.blk_numbers     
        return(inode)                                              #Updating inode.blk_numbers with the block numbers written in
        
    def ceilings(self,x):
        n = int(x)
        if n-1 < x <= n:
            return n 
        else:
            return n+1             
                
#IMPLEMENTS THE READ FUNCTION 
    def read(self, inode, offset, length): 
        '''READING DATA'''
        B=inode.ser_numbers
   
        if (inode.type!=0):
            print "ERROR: INODE TYPE NOT FILE"
            return (-1)
        
        if(offset>=inode.size):                                                 #If the offset is greater than the size of the inode
            print "ERROR: OFFSET LARGER THAN FILE SIZE."   
            return (-1)                                                            #Give an error and exit
        if(length==-1):
            length=inode.size

        if(length-offset>inode.size):
            print "ERROR: LENGTH GREATER THAN FILE SIZE"
        bl_dat=""                                                              #Stores data that is read
        index=offset/config.BLOCK_SIZE                                         #Index of the block thst contains the offset
        abc=math.ceil(min([offset+length,inode.size]))/config.BLOCK_SIZE                               #Index of the block that contains the last charcter to be read
        index1=self.ceilings(abc)
        E=index*config.BLOCK_SIZE                                              #Stores number of characters before the index block
        N=offset-E                                                          #Stores number of characters in the index block that do not have to be read
     
        read_servers=[]
        if index==index1:
            for i in range(index,index1+1):
                read_servers=MemoryInterface.Read_Data_Servers(B[i])
            print ("\n\nData to be read resides on the following servers: ")
            for i in range (0,len(read_servers)):
                print read_servers[i]
            MemoryInterface.Read_Server_Ack(read_servers)
            for i in range(index,index1+1):                                        #For number of block that have to be read from
                bl_dat=bl_dat+MemoryInterface.get_data_block(inode.blk_numbers[i],B[i])                 #Put all the data block appended togther in bl_data
        inode.time_accessed=str(datetime.datetime.now())[:19]                  #Update the access time
        
        
        for i in range(index,index1):
            read_servers=MemoryInterface.Read_Data_Servers(B[i])
        print ("\n\nData to be read resides on the following servers: ")
        for i in range (0,len(read_servers)):
                print read_servers[i]
        MemoryInterface.Read_Server_Ack(read_servers)
        for i in range(index,index1):                                        #For number of block that have to be read from
            bl_dat=bl_dat+MemoryInterface.get_data_block(inode.blk_numbers[i],B[i])                 #Put all the data block appended togther in bl_data
        inode.time_accessed=str(datetime.datetime.now())[:19]                  #Update the access time
        data_read= bl_dat[N:N+length]
        
        
        return inode,data_read                                             #Read data is bl_data removing N characters from the index block to N+length characters
    
        
            
        

        '''#IMPLEMENTS THE READ FUNCTION 
        def read(self, inode, offset, length): 
            if type == 1: 
                print("Error InodeLayer: Wrong Inode for file read")
                return -1
            if offset >= inode.size + 1: 
                print("Error(Read) InodeLayer: Offset exceeds the file length")
                return inode, -1
                #offset = 0
            if length >= inode.size + 1:
                print("Error(Read) InodeLayer: Length exceeds the file length")
                return inode, -1
                #length = inode.size - offset
            if length == 0: 
                return inode, ""
            if length == -1: 
                length = inode.size -1
            
            curr_offset  = offset 
            end_offset = (offset + length) +  (config.BLOCK_SIZE - ((offset + length) % config.BLOCK_SIZE))
            data = ''
            
            while curr_offset <= end_offset:
                data += self.INODE_TO_BLOCK(inode, curr_offset)
                curr_offset += config.BLOCK_SIZE
            
            start = offset % config.BLOCK_SIZE
            end = start + length   
            inode.time_accessed = datetime.datetime.now()
            return inode, data[start : end]   
                                    #RETURNS INODE TO INODE NUMBER LAYER TO UPDATE INODE AT SERVER'''



