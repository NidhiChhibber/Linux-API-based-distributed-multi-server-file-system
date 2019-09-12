'''
THIS IS A MEMORY MODULE ON THE SREVER WHICH ACTS LIKE MEMORY OF FILE SYSTEM. ALL THE OPERATIONS REGARDING THE FILE SYSTEM OPERATES IN 
THIS MODULE. THE MODULE HAS POINTER TO DISK AND HAS EXACT SAME LAYOUT AS UNIX TYPE FILE SYSTEM.
'''  
import config, DiskLayout,pickle,time


#POINTER TO DISK
sblock = DiskLayout.SuperBlock()			 


#BOOTS THE FILE SYSTEM
class Initialize():
	def __init__(self):
		#ALLOCATING BITMAP BLOCKS 0 AND 1 BLOCKS ARE RESERVED FOR BOOT BLOCK AND SUPERBLOCK
		sblock.BITMAP_BLOCKS_OFFSET, count = 2, 2 
		for i in range(0, sblock.TOTAL_NO_OF_BLOCKS / sblock.BLOCK_SIZE):  	
			sblock.ADDR_BITMAP_BLOCKS.append(DiskLayout.Bitmap_Block(sblock.BLOCK_SIZE))
			count += 1
		#ALLOCATING INODE BLOCKS
		sblock.INODE_BLOCKS_OFFSET = count
		for i in range(0, (sblock.MAX_NUM_INODES * sblock.INODE_SIZE) / sblock.BLOCK_SIZE):		#for Inode blocks
			sblock.ADDR_INODE_BLOCKS.append(DiskLayout.Inode_Block(sblock.INODES_PER_BLOCK))
			count  += 1
		#ALLOCATING DATA BLOCKS
		sblock.DATA_BLOCKS_OFFSET = count
		for i in range(sblock.DATA_BLOCKS_OFFSET, sblock.TOTAL_NO_OF_BLOCKS):
			sblock.ADDR_DATA_BLOCKS.append(DiskLayout.Data_Block(sblock.BLOCK_SIZE))
		#MAKING BLOCKS BEFORE DATA BLOCKS UNAVAILABLE FOR USE SINCE OCCUPIED BY SUPERBLOCK, BOOTBLOCK, BITMAP AND INODE TABLE
		for i in range(0, sblock.DATA_BLOCKS_OFFSET): 
			sblock.ADDR_BITMAP_BLOCKS[i / sblock.BLOCK_SIZE].block[i % sblock.BLOCK_SIZE] = -1


#OPERATIONS ON FILE SYSTEM
class Operations():

	#GIVES ADDRESS OF INODE TABLE
	def addr_inode_table(self):				
		return pickle.dumps(sblock.ADDR_INODE_BLOCKS)		#Return marshalled value


	#RETURNS THE DATA OF THE BLOCK
	def get_data_block(self, block_number):	
		block_number=pickle.loads(block_number)			#Unmarshall recieved arguments
		
		if block_number == 0:
			error_message=("Memory: Reserved for Boot Block")
			z=[] 
			z=[-1,error_message]						#Pack errorvalue and message
			return pickle.dumps(z)						#Return marshalled value
		elif block_number == 1: 
			error_message=("Memory: Reserved for Super Block")
			z=[] 
			z=[-1,error_message]			#Pack errorvalue and message
			return pickle.dumps(z)			#Return marshalled value
		elif block_number >= sblock.BITMAP_BLOCKS_OFFSET and block_number < sblock.INODE_BLOCKS_OFFSET:
			z=[sblock.ADDR_BITMAP_BLOCKS[block_number - sblock.BITMAP_BLOCKS_OFFSET].block,'']
			return pickle.dumps(z)			#Return marshalled value
		elif block_number >= sblock.INODE_BLOCKS_OFFSET and block_number < sblock.DATA_BLOCKS_OFFSET:
			z=[sblock.ADDR_INODE_BLOCKS[block_number - sblock.INODE_BLOCKS_OFFSET].block,'']
			return pickle.dumps(z)			#Return marshalled value
		elif block_number >= sblock.DATA_BLOCKS_OFFSET and block_number < sblock.TOTAL_NO_OF_BLOCKS:
			z=[sblock.ADDR_DATA_BLOCKS[block_number - sblock.DATA_BLOCKS_OFFSET].block,'']
			return pickle.dumps(z)			#Return marshalled value
		else: 
			error_message=("Memory: Block index out of range or Wrong input!")
			z=[] 
			z=[-1,error_message]			#Pack errorvalue and message
			return pickle.dumps(z)			#Return marshalled value


	#RETURNS THE BLOCK NUMBER OF AVAIALBLE DATA BLOCK  
	def get_valid_data_block(self):			
		for i in range(0, sblock.TOTAL_NO_OF_BLOCKS):
			if sblock.ADDR_BITMAP_BLOCKS[i / sblock.BLOCK_SIZE].block[i % sblock.BLOCK_SIZE] == 0:
				sblock.ADDR_BITMAP_BLOCKS[i / sblock.BLOCK_SIZE].block[i % sblock.BLOCK_SIZE] = 1
				z=[i,'']		#Return marshalled value
				return pickle.dumps(z)		#Return marshalled value
		error_message="Memory: No valid blocks available"
		z=[-1,error_message]
		return pickle.dumps(z)		#Return marshalled value

	#REMOVES THE INVALID DATA BLOCK TO MAKE IT REUSABLE
	def free_data_block(self, block_number): 
		block_number=pickle.loads(block_number) 	
		sblock.ADDR_BITMAP_BLOCKS[block_number / sblock.BLOCK_SIZE].block[block_number % sblock.BLOCK_SIZE] = 0
		b = sblock.ADDR_DATA_BLOCKS[block_number - sblock.DATA_BLOCKS_OFFSET].block
		for i in range(0, sblock.BLOCK_SIZE): b[i] = '\0'
		return pickle.dumps(1)		#Return any marshalled value


	#WRITES TO THE DATA BLOCK
	def update_data_block(self, block_number, block_data):	
		block_number=pickle.loads(block_number)
		block_data=pickle.loads(block_data)	
		b = sblock.ADDR_DATA_BLOCKS[block_number - sblock.DATA_BLOCKS_OFFSET].block
		sblock.ADDR_BITMAP_BLOCKS[block_number / sblock.BLOCK_SIZE].block[block_number % sblock.BLOCK_SIZE] = 1
		for i in range(0, len(block_data)): b[i] = block_data[i]
		
		#print("Memory: Data Copy Completes")
		return pickle.dumps(1)		#Return any marshalled value
	
	
	#UPDATES INODE TABLE WITH UPDATED INODE
	def update_inode_table(self, inode, inode_number):
		inode=pickle.loads(inode)
		inode_number=pickle.loads(inode_number)
		sblock.ADDR_INODE_BLOCKS[inode_number / sblock.INODES_PER_BLOCK].block[inode_number % sblock.INODES_PER_BLOCK] = inode
		return pickle.dumps(1)		#Return any marshalled value

	
	#RETURNS THE INODE FROM INODE NUMBER
	def inode_number_to_inode(self, inode_number):
		inode_number=pickle.loads(inode_number)
		z=sblock.ADDR_INODE_BLOCKS[inode_number / sblock.INODES_PER_BLOCK].block[inode_number % sblock.INODES_PER_BLOCK]
		return pickle.dumps(z)

	
		#SHOWS THE STATUS OF DISK LAYOUT IN MEMORY
	def status(self):
		counter = 1
		string = ""
		string += "\n----------BITMAP: ----------(Block Number : Valid Status)\n"
		block_number = 0
		for i in range(2, sblock.INODE_BLOCKS_OFFSET):
			string += "Bitmap Block : " + str(i - 2) + "\n"
			b = sblock.ADDR_BITMAP_BLOCKS[i - sblock.BITMAP_BLOCKS_OFFSET].block
			for j in range(0, len(b)):
				if j == 50: break   #only to avoid useless data to print
				string += "\t\t[" + str(block_number + j) + "  :  "  + str(b[j]) + "]  \n"
			block_number += len(b)
			if counter == 1: break
		string += ".....showing just part(20) of 1st bitmap block!\n"

		string += "\n\n----------INODE Blocks: ----------(Inode Number : Inode(Address)\n"
		inode_number = 0
		for i in range(sblock.INODE_BLOCKS_OFFSET, sblock.DATA_BLOCKS_OFFSET):
			string += "Inode Block : " + str(i - sblock.INODE_BLOCKS_OFFSET) + "\n"
			b = sblock.ADDR_INODE_BLOCKS[i - sblock.INODE_BLOCKS_OFFSET].block
			for j in range(0, len(b)):
				string += "\t\t[" + str(inode_number + j) + "  :  "  + str(bool(b[j])) + "]  \n"
			inode_number += len(b)
		
		string += "\n\n----------DATA Blocks: ----------\n  "
		counter = 0
		for i in range(sblock.DATA_BLOCKS_OFFSET, sblock.TOTAL_NO_OF_BLOCKS):
			if counter == 28: 
				string += "......Showing just part(25) data blocks\n"
				break
			string += (str(i) + " : " + "".join(sblock.ADDR_DATA_BLOCKS[i - sblock.DATA_BLOCKS_OFFSET].block)) + "  "
			counter += 1

		
		string += "\n\n----------HIERARCHY: ------------\n"
		for i in range(sblock.INODE_BLOCKS_OFFSET, sblock.DATA_BLOCKS_OFFSET):
			for j in range(0, sblock.INODES_PER_BLOCK):
				inode = sblock.ADDR_INODE_BLOCKS[i-sblock.INODE_BLOCKS_OFFSET].block[j]
				if inode and inode[0]:
					string += "\nDIRECTORY: " + inode[1] + "\n"
					for x in inode[7]: string += "".join(x[:config.MAX_FILE_NAME_SIZE]) + " || "
					string += "\n"
		
		return pickle.dumps(string)