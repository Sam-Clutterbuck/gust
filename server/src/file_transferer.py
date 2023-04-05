from os.path import getsize
from time import sleep

from core.src import  Yaml_Editor, Data_Link, Encrypt_Pki, Integrity_Check

class File_Transfer:

    #####################
    #Globals

    success, yaml_file = Yaml_Editor.Yaml_Read(Data_Link.server_config)
    if (success == False):
        yaml_file = {}
    CONFIG_FILE = yaml_file

    DOWNLOAD_LOC = CONFIG_FILE["download_loc"]
    DOWNLOAD_LOG_LOC= CONFIG_FILE["download_log_loc"]
    SOURCE_LOC = CONFIG_FILE["server_sources_loc"]

    success, yaml_file = Yaml_Editor.Yaml_Read(Data_Link.commands)
    if (success == False):
        yaml_file = {}
    COMMANDS = yaml_file
   #####################
    
    def Transfer_Files(Source_Name, Source_Breakdown_File, Connection):
        
        Connection.send(Source_Name.encode())

        response = Connection.recv(1024).decode()
        if (response != File_Transfer.COMMANDS["ready check"]["command"]):
            return 

        success = File_Transfer.Send_File(Source_Breakdown_File["hash_file"], Connection)
        if (success == False):
            return

        response = Connection.recv(1024).decode()
        if (response != File_Transfer.COMMANDS["ready check"]["command"]):
            return 


        success = File_Transfer.Send_File(Source_Breakdown_File["file"], Connection)
        if (success == False):
            return
        
        response = Connection.recv(1024).decode()
        if (response != File_Transfer.COMMANDS["ready check"]["command"]):
            return 
        

    def Send_File(File, Connection):

        is_file = Integrity_Check.File_Check(File_Transfer.DOWNLOAD_LOC+File)
        if (is_file == False):
            return False
        
        file_size = getsize(File_Transfer.DOWNLOAD_LOC+File)

        with open(File_Transfer.DOWNLOAD_LOC+File, "r") as hash_file:
            data = hash_file.read()

        encrypted_filename = Encrypt_Pki.Encrypt_Message(File, Connection)
        encrypted_file_size = Encrypt_Pki.Encrypt_Message(str(file_size), Connection)
        encrypted_data = Encrypt_Pki.Encrypt_Message(data, Connection)

        #encrypted_data += File_Transfer.COMMANDS["end transfer"]["command"].encode()

        Connection.send(encrypted_filename)
        Connection.send(encrypted_file_size)
        sleep(2)
        Connection.sendall(encrypted_data)
        Connection.send(File_Transfer.COMMANDS["end transfer"]["command"].encode())

        return True