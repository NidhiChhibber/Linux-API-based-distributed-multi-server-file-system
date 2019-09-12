'''
THIS MODULE ACTS LIKE FILE NAME LAYER AND PATH NAME LAYER (BOTH) ABOVE INODE LAYER.
IT RECIEVES INPUT AS PATH (WITHOUT INITIAL '/'). THE LAYER IMPLEMENTS LOOKUP TO FIND INODE NUMBER OF THE REQUIRED DIRECTORY.
PARENTS INODE NUMBER IS FIRST EXTRACTED BY LOOKUP AND THEN CHILD INODE NUMBER BY RESPECTED FUNCTION AND BOTH OF THEM ARE UPDATED
'''
import InodeNumberLayer,copy, BlockLayer, config

#HANDLE OF INODE NUMBER LAYER
interface = InodeNumberLayer.InodeNumberLayer()

class FileNameLayer():
	def CHILD_INODE_NUMBER_FROM_PARENT_INODE_NUMBER_MFS(self, childname, inode_number_of_parent):
		inode = interface.INODE_NUMBER_TO_INODE_MFS(inode_number_of_parent)
		if not inode: 
			print("Error FileNameLayer: Lookup Failure!")
			return -1
		if inode.type == 0:
			print("Error FileNameLayer: Invalid Directory!")
			return -1
		if childname in inode.directory: return inode.directory[childname]
		print("Error FileNameLayer: Lookup Failure!")
		return -1

	#PLEASE DO NOT MODIFY
	#RETURNS THE CHILD INODE NUMBER FROM THE PARENTS INODE NUMBER
	def CHILD_INODE_NUMBER_FROM_PARENT_INODE_NUMBER(self, childname, inode_number_of_parent):
		inode = interface.INODE_NUMBER_TO_INODE(inode_number_of_parent)
		if not inode: 
			print("Error FileNameLayer: Lookup Failure!")
			return -1
		if inode.type == 0:
			print("Error FileNameLayer: Invalid Directory!")
			return -1
		if childname in inode.directory: return inode.directory[childname]
		print("Error FileNameLayer: Lookup Failure!")
		return -1

	def LOOKUP_MFS(self, path, inode_number_cwd):   
		name_array = path.split('/')
		if len(name_array) == 1: return inode_number_cwd
		else:
			child_inode_number = self.CHILD_INODE_NUMBER_FROM_PARENT_INODE_NUMBER_MFS(name_array[0], inode_number_cwd)
			if child_inode_number == -1: return -1
			return self.LOOKUP_MFS("/".join(name_array[1:]), child_inode_number)
	#PLEASE DO NOT MODIFY
	#RETUNS THE PARENT INODE NUMBER FROM THE PATH GIVEN FOR A FILE/DIRECTORY 
	def LOOKUP(self, path, inode_number_cwd):   
		name_array = path.split('/')
		if len(name_array) == 1: return inode_number_cwd
		else:
			child_inode_number = self.CHILD_INODE_NUMBER_FROM_PARENT_INODE_NUMBER(name_array[0], inode_number_cwd)
			if child_inode_number == -1: return -1
			return self.LOOKUP("/".join(name_array[1:]), child_inode_number)
	
	def new_entry_MFS(self, path, inode_number_cwd, type):
		if path == '/': #SPECIAL CASE OF INITIALIZING FILE SYSTEM
			interface.new_inode_number_MFS(type, inode_number_cwd, "root")
			return True
		parent_inode_number = self.LOOKUP_MFS(path, inode_number_cwd)
		parent_inode = interface.INODE_NUMBER_TO_INODE_MFS(parent_inode_number) 
		childname = path.split('/')[-1]
		if not parent_inode: return -1
		if childname in parent_inode.directory:
			print("Error FileNameLayer: File already exists!")
			return -1
		child_inode_number = interface.new_inode_number_MFS(type, parent_inode_number, childname)  #make new child
		if child_inode_number != -1:
			parent_inode.directory[childname] = child_inode_number
			interface.update_inode_table_MFS(parent_inode, parent_inode_number)
	
	#PLEASE DO NOT MODIFY
	#MAKES NEW ENTRY OF INODE
	def new_entry(self, path, inode_number_cwd, type):
		if path == '/': #SPECIAL CASE OF INITIALIZING FILE SYSTEM
			interface.new_inode_number(type, inode_number_cwd, "root")
			return True
		parent_inode_number = self.LOOKUP(path, inode_number_cwd)
		parent_inode = interface.INODE_NUMBER_TO_INODE(parent_inode_number) 
		childname = path.split('/')[-1]
		if not parent_inode: return -1
		if childname in parent_inode.directory:
			print("Error FileNameLayer: File already exists!")
			return -1
		child_inode_number = interface.new_inode_number(type, parent_inode_number, childname)  #make new child
		if child_inode_number != -1:
			parent_inode.directory[childname] = child_inode_number
			interface.update_inode_table(parent_inode, parent_inode_number)


	def path_to_child_inode_MFS(self,path_name,inode_number_cwd):
		path_array = path_name.split('/')																	#Removes '/' from the path and stores the path as an array
		if path_array[0]=="":
			if(len(path_array)>1):
				print "ERROR FilenameLayer: Invalid path"
				return -1
			inode_incr=0																
		else:
			inode_incr=self.CHILD_INODE_NUMBER_FROM_PARENT_INODE_NUMBER_MFS(path_array[0],inode_number_cwd) 		#Finds inode number of the first Directory
			for i in range (1, len(path_array)):																
				cd=path_array[i]		
				cd_in=self.CHILD_INODE_NUMBER_FROM_PARENT_INODE_NUMBER_MFS(cd,inode_incr)							#Finds the inode number of the last file/dir in the path
				inode_incr= cd_in
		return inode_incr	


	#Finds inode number of the last FILE/DIRECTORY in the path
	def path_to_child_inode(self,path_name,inode_number_cwd):
		path_array = path_name.split('/')																	#Removes '/' from the path and stores the path as an array
		if path_array[0]=="":
			if(len(path_array)>1):
				print "ERROR FilenameLayer: Invalid path"
				return -1
			inode_incr=0																
		else:
			inode_incr=self.CHILD_INODE_NUMBER_FROM_PARENT_INODE_NUMBER_MFS(path_array[0],inode_number_cwd) 		#Finds inode number of the first Directory
			for i in range (1, len(path_array)):																
				cd=path_array[i]		
				cd_in=self.CHILD_INODE_NUMBER_FROM_PARENT_INODE_NUMBER_MFS(cd,inode_incr)							#Finds the inode number of the last file/dir in the path
				inode_incr= cd_in
		return inode_incr																					#Returns the inode number of the last file/dir in the path


	#IMPLEMENTS READ
	def read(self, path, inode_number_cwd, offset, length):
		'''WRITE YOUR CODE HERE'''
		inode_number_child_read=self.path_to_child_inode(path,inode_number_cwd)								#Gets the inode number of the last file/dir in the path
		parent_inode_number_read= self.LOOKUP_MFS(path,inode_number_cwd)										#Get inode number of the parent 
		return interface.read(inode_number_child_read,offset,length,parent_inode_number_read)				#Call the read() in InodeNumberLayer and return the value to AboslutePAthNameLayer

		

	#IMPLEMENTS WRITE
	def write(self, path, inode_number_cwd, offset, data):
		'''WRITE YOUR CODE HERE'''
		inode_number_child_write=self.path_to_child_inode_MFS(path,inode_number_cwd) 							#Gets the inode number of the last file/dir in the path
		parent_inode_number_write= self.LOOKUP_MFS(path,inode_number_cwd)	
		#print "HERE"
		#print inode_number_child_write,parent_inode_number_write									#Get inode number of the parent
		interface.write(inode_number_child_write,offset,data,parent_inode_number_write)						#Call the write() in InodeNumberLayer


	#HARDLINK
	def link(self, old_path, new_path , inode_number_cwd):
		'''WRITE YOUR CODE HERE'''
		old_path_array = old_path.split('/')											#Save the path of the file/dir to which hardlink is to be created after removing '/'
		old_child_inode_number=self.path_to_child_inode_MFS(old_path,inode_number_cwd)		#Get the inode number of the last file/dir in old path
		new_parent_inode_number=self.path_to_child_inode_MFS(new_path,inode_number_cwd)		#Get the inode number of the last file/dir in new path
		new_parent_inode=interface.INODE_NUMBER_TO_INODE_MFS(new_parent_inode_number)		#Inode of dir in which hardlink is to be added
		entry_size = config.MAX_FILE_NAME_SIZE + len(str(config.MAX_NUM_INODES))
		max_entries = (config.INODE_SIZE - 79 ) / entry_size
		try:
			if len(new_parent_inode.directory) == max_entries:								#If directory is full
				print("Error FileNameLayer: Directory is full. No empty inode.")
		except:
			print ""
		interface.link(old_child_inode_number,new_parent_inode_number)					#Call the link() in inodeNumberLayer
		return 1																		#Return 1 if link is sucessful
		
		
	#REMOVES THE FILE/DIRECTORY
	def unlink(self, path, inode_number_cwd):
		if path == "": 
			print("Error FileNameLayer: Cannot delete root directory!")
			return -1
		'''WRITE YOUR CODE HERE'''
		child_inode_number_unlink= self.path_to_child_inode_MFS(path,inode_number_cwd)		#Inode number of the file/dir which has to be unlinked
		parent_inode_number_unlink=self.LOOKUP_MFS(path,inode_number_cwd)					#Inode number of the parent of the file/dir which has to be unlinked
		interface.unlink(child_inode_number_unlink,parent_inode_number_unlink)			#Call the unlink() in the InodeNumberLayer



	#MOVE
	def mv(self, old_path, new_path, inode_number_cwd):
		'''WRITE YOUR CODE HERE'''
	
		old_path_array = old_path.split('/')
		new_path_array = new_path.split('/')
		
		L=len(old_path_array)
		if(old_path_array[0]==""):														#Check if the request is to move the root directory
			print "ERROR FileNameLayer: Can not move root directory."  					#Return error
			return -1
			
		old_child_inode_number_move=self.path_to_child_inode_MFS(old_path,inode_number_cwd) #Inode number of last child in old path
		new_child_inode_number_move=self.path_to_child_inode_MFS(new_path,inode_number_cwd)	#Inode number of last child in new path
		
		old_child_inode=interface.INODE_NUMBER_TO_INODE_MFS(old_child_inode_number_move)	#Inode of last child in old path
		new_child_inode=interface.INODE_NUMBER_TO_INODE_MFS(new_child_inode_number_move)	#Inode of last child in new path
		old_parent_inode_number_move=self.LOOKUP_MFS(old_path,inode_number_cwd)				#Inode number of parent of last child old path
		try:
			if old_child_inode.name in new_child_inode.directory:					#Check if request is to move a file with same name in same directoy 
				print "ERROR FilenameLayer: Can not hardlink files with same name :",old_child_inode.name,"in same directory :",new_child_inode.name,"."
				return -1
		except:
			print ("")
		try:
			if new_child_inode.type==0:														#Request to move into a file	
				print "ERROR FileNameLayer: Can not move into a file."
				return -1
		except:
			print ""
		try:
			if new_child_inode_number_move==old_child_inode_number_move:					#Request to move same directoty into itself
				print "ERROR FileNameLayer: Can not move same directory into itself."
				return -1
		except:
			print ""
		try:
			if old_child_inode.type==1:														#Request to move directory which is not empty
				if old_child_inode.directory!={}:
					print "ERROR FilenameLayer:Can not move a non-empty directory"
				return -1
		except:
			print ""
		if(new_path_array[0]==""):
			self.link(old_path,new_path,inode_number_cwd)
			self.unlink(old_path,inode_number_cwd)
		else:
			if_linked=self.link(old_path,new_path,inode_number_cwd)						#Call link() in the same layer
			if(if_linked==1):															#If linking successeed
				self.unlink(old_path,inode_number_cwd)									#Call unlink() in the same layer
			else:
				print "ERROR FilenameLayer: File not moved: Linking not done"			#If link() did not successeed
				return -1
		
		
		
	
		
		

	