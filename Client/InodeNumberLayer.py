'''
THIS MODULE ACTS AS A INODE NUMBER LAYER. NOT ONLY IT SHARES DATA WITH INODE LAYER, BUT ALSO IT CONNECTS WITH MEMORY INTERFACE FOR INODE TABLE 
UPDATES. THE INODE TABLE AND INODE NUMBER IS UPDATED IN THE FILE SYSTEM USING THIS LAYER
'''
import InodeLayer, config, MemoryInterface, datetime, InodeOps


#HANDLE OF INODE LAYER
interface = InodeLayer.InodeLayer()


class InodeNumberLayer():
	def INODE_NUMBER_TO_INODE_MFS(self, inode_number):
		array_inode = MemoryInterface.inode_number_to_inode_MFS(inode_number)
		inode = InodeOps.InodeOperations().convert_array_to_table(array_inode)
		if inode: inode.time_accessed = datetime.datetime.now()   #TIME OF ACCESS
		return inode
	#PLEASE DO NOT MODIFY
	#ASKS FOR INODE FROM INODE NUMBER FROM MemoryInterface.(BLOCK LAYER HAS NOTHING TO DO WITH INODES SO SEPERTAE HANDLE)
	def INODE_NUMBER_TO_INODE(self, inode_number):
		array_inode = MemoryInterface.inode_number_to_inode(inode_number)
		inode = InodeOps.InodeOperations().convert_array_to_table(array_inode)
		if inode: inode.time_accessed = datetime.datetime.now()   #TIME OF ACCESS
		return inode


	#PLEASE DO NOT MODIFY
	#RETURNS DATA BLOCK FROM INODE NUMBER
	def INODE_NUMBER_TO_BLOCK(self, inode_number, offset, length):
		inode = self.INODE_NUMBER_TO_INODE(inode_number)
		if not inode:
			print("Error InodeNumberLayer: Wrong Inode Number! \n")
			return -1
		return interface.read(inode, offset, length)


	def update_inode_table_MFS(self, table_inode, inode_number):
		if table_inode: table_inode.time_modified = datetime.datetime.now()  #TIME OF MODIFICATION 
		array_inode = InodeOps.InodeOperations().convert_table_to_array(table_inode)
		MemoryInterface.update_inode_table_MFS(array_inode, inode_number)

	#PLEASE DO NOT MODIFY
	#UPDATES THE INODE TO THE INODE TABLE
	def update_inode_table(self, table_inode, inode_number):
		if table_inode: table_inode.time_modified = datetime.datetime.now()  #TIME OF MODIFICATION 
		array_inode = InodeOps.InodeOperations().convert_table_to_array(table_inode)
		MemoryInterface.update_inode_table(array_inode, inode_number)
	
	def new_inode_number_MFS(self, type, parent_inode_number, name):
		if parent_inode_number != -1:
			parent_inode = self.INODE_NUMBER_TO_INODE_MFS(parent_inode_number)
			if not parent_inode:
				print("Error InodeNumberLayer: Incorrect Parent Inode")
				return -1
			entry_size = config.MAX_FILE_NAME_SIZE + len(str(config.MAX_NUM_INODES))
			max_entries = (config.INODE_SIZE - 79 ) / entry_size
			if len(parent_inode.directory) == max_entries:
				print("Error InodeNumberLayer: Maximum inodes allowed per directory reached!")
				return -1
		for i in range(0, config.MAX_NUM_INODES):
			if self.INODE_NUMBER_TO_INODE_MFS(i) == False: #FALSE INDICTES UNOCCUPIED INODE ENTRY HENCE, FREEUMBER
				inode = interface.new_inode(type)
				inode.name = name
				self.update_inode_table_MFS(inode, i)
				return i
		print("Error InodeNumberLayer: All inode Numbers are occupied!\n")
	#PLEASE DO NOT MODIFY
	#FINDS NEW INODE INODE NUMBER FROM FILESYSTEM
	def new_inode_number(self, type, parent_inode_number, name):
		if parent_inode_number != -1:
			parent_inode = self.INODE_NUMBER_TO_INODE(parent_inode_number)
			if not parent_inode:
				print("Error InodeNumberLayer: Incorrect Parent Inode")
				return -1
			entry_size = config.MAX_FILE_NAME_SIZE + len(str(config.MAX_NUM_INODES))
			max_entries = (config.INODE_SIZE - 79 ) / entry_size
			if len(parent_inode.directory) == max_entries:
				print("Error InodeNumberLayer: Maximum inodes allowed per directory reached!")
				return -1
		for i in range(0, config.MAX_NUM_INODES):
			if self.INODE_NUMBER_TO_INODE(i) == False: #FALSE INDICTES UNOCCUPIED INODE ENTRY HENCE, FREEUMBER
				inode = interface.new_inode(type)
				inode.name = name
				self.update_inode_table(inode, i)
				return i
		print("Error InodeNumberLayer: All inode Numbers are occupied!\n")


	#LINKS THE INODE
	def link(self, inode_number, parent_inode_number):		
		'''WRITE YOUR CODE HERE'''
		child_inode= self.INODE_NUMBER_TO_INODE_MFS(inode_number)			#Find the inode from the inode number of the file to which hardlinked is to be created
		child_name=child_inode.name										#Name of the file that is to be linked
		parent_inode=self.INODE_NUMBER_TO_INODE_MFS(parent_inode_number)	#Parent inode number where the hardlink is to be created
		parent_inode.directory[child_name]=inode_number					#In parent inode, add file named as child_name with its inode number
		child_inode.links+=1											#Increment the reference count of the number of link by 1
		self.update_inode_table_MFS(child_inode,inode_number)				#Update the inode table for the child inode
		self.update_inode_table_MFS(parent_inode,parent_inode_number)		#Update the inode table for destination


	#REMOVES THE INODE ENTRY FROM INODE TABLE
	def unlink(self, inode_number, parent_inode_number):
		'''WRITE YOUR CODE HERE'''
		child_inode= self.INODE_NUMBER_TO_INODE_MFS(inode_number)	#Find the inode from the inode number of the file to which hardlinked is to be removed
	
		child_name=child_inode.name								#Name of the file is to be unlinked
		parent_inode=self.INODE_NUMBER_TO_INODE_MFS(parent_inode_number) #Inode of the directory from which file is to be unlinked		
		del parent_inode.directory[child_name]					#Delete from the directory the file name same as child_inode name
		
		child_inode.links-=1											#Decrement the reference count of the number of link by 1
		self.update_inode_table_MFS(child_inode,inode_number)				#Update the inode table for the file unlinked
		self.update_inode_table_MFS(parent_inode,parent_inode_number)		#Update the inode table for the directory from which file is unlinked
		
		if child_inode.type==0:											#If inode is file type
			if child_inode.links==0:									#If there are nomore links to the inode
				#for i in range(0,len(child_inode.blk_numbers)-1):
				
					#interface.free_data_block_MFS(child_inode,child_inode.blk_numbers[i])		#Free all the data vlocks associated to the inode
				if child_inode.size!=0:
					interface.free_data_block(child_inode,child_inode.blk_numbers)
				
				for i in range(0,len(child_inode.blk_numbers)-1):
					interface.free_data_block_MFS(child_inode,child_inode.blk_numbers[i])
					
					
					child_inode.size=0														#Inode size should be made 0
					self.update_inode_table_MFS(bool(0),inode_number)	
											#Update the inode table for the inode
		if child_inode.type==1:																#If inode type is directory
			if child_inode.links==1:														#If there are no more links to the directory
				for i in range(0,len(child_inode.blk_numbers)-1):
					if child_inode.size!=0:
						interface.free_data_block(child_inode,child_inode.blk_numbers[i])		#Free all the data vlocks associated to the inode
						interface.free_data_block_MFS(child_inode,child_inode.blk_numbers[i])
					else:
						interface.free_data_block_MFS(child_inode,child_inode.blk_numbers[i])

					
	
					child_inode.size=0														#Inode size should be made 0
					self.update_inode_table_MFS(bool(0),inode_number)							#Update the inode table to show inode unoccupied	

		
		
	#IMPLEMENTS WRITE FUNCTIONALITY
	def write(self, inode_number, offset, data, parent_inode_number):
		'''WRITE YOUR CODE HERE'''
		
		inode_write=self.INODE_NUMBER_TO_INODE_MFS(inode_number)				#Get inode from the inode number in which data is to be written
		inode=interface.write(inode_write,offset,data) 						#Call write() in InodeLayer	
		self.update_inode_table_MFS(inode_write,inode_number)					#Update the inode post writing into it
		 
	#IMPLEMENTS READ FUNCTIONALITY
	def read(self, inode_number, offset, length, parent_inode_number):
		'''WRITE YOUR CODE HERE'''
		inode_read=self.INODE_NUMBER_TO_INODE_MFS(inode_number)					#Get inode from the inode number in which data is to be read
		return interface.read(inode_read,offset,length)[1]					#Call read() in InodeLayer and return the value to FileNameL
		
		