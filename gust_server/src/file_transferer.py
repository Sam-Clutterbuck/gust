import gust_server.src.client_removal_check 

from os.path import getsize

from gust_core.src import Commands_Global, Integrity_Check, AES_Encrypt
from gust_server.src.server_config_link import Server_Global

class File_Transfer:
    
    def Transfer_Files(Source_Name, Source_Breakdown_File, Client, Session_Info, Session_User):
        
        # confirm the source is valid to send
        outcome = Client.recv(1024).decode()
        if (outcome != Commands_Global.COMMANDS["success"]["command"]):
            return False

        ## source valid to transfer

        success = File_Transfer.Send_File(Source_Breakdown_File["hash_file"], Client, Session_Info, Session_User)
        if (success == False):
            return False
        
        success = File_Transfer.Send_File(Source_Breakdown_File["file"], Client, Session_Info, Session_User)
        if (success == False):
            return False
        
        return True

    def Send_File(File, Client, Session_Info, Session_User):

        is_file = Integrity_Check.File_Check(Server_Global.DOWNLOAD_LOC+File)
        if (is_file == False):
            return False
        
        file_size = getsize(Server_Global.DOWNLOAD_LOC+File)

        with open(Server_Global.DOWNLOAD_LOC+File, "r") as file:
            data = file.read()

        encrypted_filename = AES_Encrypt.Session_Encrypt(Session_Info[Session_User]['session'], Session_User, File)
        encrypted_file_size = AES_Encrypt.Session_Encrypt(Session_Info[Session_User]['session'], Session_User, str(file_size))
        encrypted_data = AES_Encrypt.Session_Encrypt(Session_Info[Session_User]['session'], Session_User, data)


        Client.send(encrypted_filename)
        Client.send(encrypted_file_size)
        
        ready = Client.recv(1024).decode()
        if (ready != Commands_Global.COMMANDS["ready check"]["command"]):
            return False

        Client.sendall(encrypted_data)
        Client.send(Commands_Global.COMMANDS["end transfer"]["command"].encode())

        # confirm the source is valid to send
        outcome = Client.recv(1024).decode()
        if (outcome != Commands_Global.COMMANDS["success"]["command"]):
            return False
        
        return True
        