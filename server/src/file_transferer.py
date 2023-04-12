import server.src.client_removal_check 

from os.path import getsize
from time import sleep

from core.src import  Yaml_Editor, Commands_Global, Encrypt_Pki, Integrity_Check
from server.src.server_config_link import Server_Global

class File_Transfer:
    
    def Transfer_Files(Source_Name, Source_Breakdown_File, Connection):
        
        Connection.send(Source_Name.encode())

        response = Connection.recv(1024).decode()
        if (response != Commands_Global.COMMANDS["ready check"]["command"]):
            return 

        success = File_Transfer.Send_File(Source_Breakdown_File["hash_file"], Connection)
        if (success == False):
            return

        response = Connection.recv(1024).decode()
        if (response != Commands_Global.COMMANDS["ready check"]["command"]):
            return 


        success = File_Transfer.Send_File(Source_Breakdown_File["file"], Connection)
        if (success == False):
            return
        
        response = Connection.recv(1024).decode()
        if (response != Commands_Global.COMMANDS["ready check"]["command"]):
            return 
        

    def Send_File(File, Connection):

        is_file = Integrity_Check.File_Check(Server_Global.DOWNLOAD_LOC+File)
        if (is_file == False):
            return False
        
        file_size = getsize(Server_Global.DOWNLOAD_LOC+File)

        with open(Server_Global.DOWNLOAD_LOC+File, "r") as hash_file:
            data = hash_file.read()

        encrypted_filename = Encrypt_Pki.Encrypt_Message(File, Connection)
        encrypted_file_size = Encrypt_Pki.Encrypt_Message(str(file_size), Connection)
        encrypted_data = Encrypt_Pki.Encrypt_Message(data, Connection)

        #encrypted_data += Commands_Global.COMMANDS["end transfer"]["command"].encode()

        Connection.send(encrypted_filename)
        Connection.send(encrypted_file_size)
        sleep(2)
        Connection.sendall(encrypted_data)
        Connection.send(Commands_Global.COMMANDS["end transfer"]["command"].encode())

        return True