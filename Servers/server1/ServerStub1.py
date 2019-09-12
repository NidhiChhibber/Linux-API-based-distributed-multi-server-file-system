#!/usr/bin/python

import SimpleXMLRPCServer,Memory,codecs
interface=Memory.Operations()
def Server_State():
    return 1
def main():   
    print "This is a server 1"
    server=SimpleXMLRPCServer.SimpleXMLRPCServer(("localhost",8801)) 
    #server=SimpleXMLRPCServer.SimpleXMLRPCServer(("172.31.28.49",8801))     #Create SimpleXMLRPC Server instance
    server.register_function(Memory.Initialize)                         #Register functions to be called
    server.register_function(interface.get_data_block)
    server.register_function(interface.inode_number_to_inode)
    server.register_function(interface.get_valid_data_block)
    server.register_function(interface.free_data_block)
    server.register_function(interface.update_data_block)
    server.register_function(interface.update_inode_table)
    server.register_function(interface.status)
    server.register_function(Server_State)

    print ("To End:CTRL+C")
    server.serve_forever() #Spin loop forever

if __name__ == "__main__":
    main()