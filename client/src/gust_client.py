import re
import tqdm

from os import remove
from socket import AF_INET, socket, SOCK_STREAM, SHUT_RDWR
from getpass import getpass

from core.src import Yaml_Editor, Data_Link, Gust_Log, Encrypt_Pki, Integrity_Check


class Gust_Client:
    
    #####################
    #Globals
    success, yaml_file = Yaml_Editor.Yaml_Read(Data_Link.client_config)
    if (success == False):
        yaml_file = {}
    CONFIG_FILE = yaml_file

    TARGET_IP = CONFIG_FILE["target ip"]
    TARGET_PORT = CONFIG_FILE["target port"]
    CLIENTSOCKET = socket(AF_INET, SOCK_STREAM)
    SOURCE_LOC = CONFIG_FILE["client_sources_loc"]
    DOWNLOAD_LOC = CONFIG_FILE["download_loc"]
    
    #####################

    success, yaml_file = Yaml_Editor.Yaml_Read(Data_Link.commands)
    if (success == False):
        yaml_file = {}
    COMMANDS = yaml_file

    def Socket_Check(Socket):
        if Socket is None or (Socket._closed == True):
            Gust_Log.System_Log(500,"No active socket",None)
            quit()

    def Start_Client(Manual):

        authenticated = False

        with Gust_Client.CLIENTSOCKET as open_socket:
            open_socket.connect((Gust_Client.TARGET_IP, Gust_Client.TARGET_PORT))
            Encrypt_Pki.Create_Keys()

            while not authenticated: 

                try:
                    if (Manual == True):

                        ##handle for disconnect
                        Gust_Client.Socket_Check(open_socket)

                        hashed_login = Gust_Client.Manual_Login()
                        authenticated = Gust_Client.Attempt_Login(hashed_login, open_socket)
                        if (authenticated == True):
                            Gust_Client.Recieve_Public_Key(open_socket, hashed_login)
                    else:
                        #AUTOMATIC STEPS
                        print("")

                except OSError as error:
                    if (open_socket._closed == False):
                        Gust_Log.System_Log(500,str(error),open_socket)
                    return 

            while authenticated:

                try:
                    if (Manual == True):

                        ##handle for disconnect
                        Gust_Client.Socket_Check(open_socket)

                        Gust_Client.Send_Command(open_socket)
                    else:
                        #AUTOMATIC STEPS
                        print("")

                except OSError as error:
                    if (open_socket._closed == False):
                        Gust_Log.System_Log(500,str(error),open_socket)
                    return 
                
        

    def Attempt_Login(Hashed_Login, Socket):

        Gust_Client.Socket_Check(Socket)

        if Hashed_Login is None:
            Hashed_Login = ""

        Socket.send(Hashed_Login.encode())
        response = Socket.recv(1024).decode()
        if (response == Gust_Client.COMMANDS["authorised"]["command"]):
            Gust_Log.Authentication_Log(200, "Connected To Server", Socket)
            return True
        
        if (response[-13:] == Gust_Client.COMMANDS["disconnect"]["command"]):

            #remove ![DISCONNECT] header
            message_content = re.findall(".*!", response)
            message_clean = re.split("!", message_content[0])
            response = message_clean[0]
            Gust_Log.Authentication_Log(403,response, Socket)
            Gust_Client.Close_Socket(Socket)
            
        
        print(response)
        return False

    def Manual_Login():

        username  = input("Enter Username: ")
        
        password = getpass('Enter Password: ')
        hashed_pass = Integrity_Check.Sha256_Encode(password)

        return username + "::::" + hashed_pass
    
    def Close_Socket(Socket):
        Gust_Client.Socket_Check(Socket)

        Socket.shutdown(SHUT_RDWR)
        Socket.close()
        quit()
    
    def Recieve_Public_Key(Socket, AES_Key):
        Gust_Client.Socket_Check(Socket)

        if AES_Key is None:
            AES_Key = ""

        succeded = False

        while not succeded:

            encrypted_public_key = Socket.recv(1024)

            #Disconnect command hijacks encrypted_public_key var if errors occur
            if (encrypted_public_key[-13:] == Gust_Client.COMMANDS["disconnect"]["command"]):
                #remove ![DISCONNECT] header
                message_content = re.findall(".*!", encrypted_public_key)
                message_clean = re.split("!", message_content[0])
                encrypted_public_key = message_clean[0]
                Gust_Log.Authentication_Log(403,encrypted_public_key, Socket)
                Gust_Client.Close_Socket(Socket)
                print(encrypted_public_key)

            Encrypt_Pki.Decrypt_Public_Key(encrypted_public_key, AES_Key, Socket)
            
            encrypted_public_key = Encrypt_Pki.Prep_Public_Key(AES_Key)
            Socket.send(encrypted_public_key)

            confirmation = Socket.recv(1024)
            decrypted_confirmation = Encrypt_Pki.Decrypt_Message(confirmation)

            if (decrypted_confirmation == Gust_Client.COMMANDS["authorised"]["command"]):
                Gust_Log.Authentication_Log(200, "Successfully recieved Public Key", Socket)
                
                encrypted_message = Encrypt_Pki.Encrypt_Message(Gust_Client.COMMANDS["authorised"]["command"], Socket)
                Socket.send(encrypted_message)
                succeded = True

            else:
                Socket.send("Failed")

        return
    
    def Prep_File_Transfer(Socket):
        
        source_name = Socket.recv(1024).decode()

        breakdown = None
        source_list = Yaml_Editor.List_Headers(Gust_Client.SOURCE_LOC)
        for source in source_list:
            if (source == source_name):
                breakdown = Yaml_Editor.Breakdown_Dictionary(source, Gust_Client.SOURCE_LOC)

        if breakdown is None:
            Gust_Log.File_Log(404,"Unable to download : "+ source_name + " as it is not in the clients sources list", Socket)
            Socket.send("ERROR".encode())
            return

        Socket.send((Gust_Client.COMMANDS["ready check"]["command"]).encode())

        success, hash_file = Gust_Client.Recieve_File_Transfer(Socket)
        if (success == False):
            return

        success, source_file = Gust_Client.Recieve_File_Transfer(Socket)
        if (success == False):
            return
        
        matching_hashes = Integrity_Check.Hash_Check(source_file, hash_file,breakdown["hash_type"])
        if (matching_hashes == False):
            remove(source_file)
            remove(hash_file)
            return

        return

    def Recieve_File_Transfer(Socket):
        
        file_name = Socket.recv(1024)
        decrypt_file_name = Encrypt_Pki.Decrypt_Message(file_name)
        print("Downloading : " + decrypt_file_name)

        file_size = Socket.recv(1024)
        decrypt_file_size = Encrypt_Pki.Decrypt_Message(file_size)
        print("file_size : " + decrypt_file_size)

        success = Integrity_Check.Dir_Check(Gust_Client.DOWNLOAD_LOC)
        if (success == False):
            Socket.send("ERROR".encode())
            return False, None
        
        file = open(Gust_Client.DOWNLOAD_LOC+decrypt_file_name, "w")

        done = False
        file_bytes = b""

        # Creating progress bar
        progress = tqdm.tqdm(unit="8", unit_scale=True, unit_divisor=1000, total=int())

        # Creating a while loop so the data receiving process doesn't stop after just a single transfer.
        while (done == False):
            data= Socket.recv(1024)
            file_bytes += data
            if file_bytes[-6:] == (Gust_Client.COMMANDS["end transfer"]["command"]).encode():
                done = True
            progress.update(1024)

        file.write(Encrypt_Pki.Decrypt_Message(file_bytes[:-6]))

        file.close()

        Socket.send((Gust_Client.COMMANDS["ready check"]["command"]).encode())
        return True, Gust_Client.DOWNLOAD_LOC+decrypt_file_name
    
    def Send_Command(Socket):

        Valid = False

        while not Valid:

            command_selection = input("Run a Command: \n").upper()

            for command in Gust_Client.COMMANDS:
                if (Gust_Client.COMMANDS[command]["command"] == command_selection):
                    Valid = True

            #specific local overrides for shortcuts

            if (command_selection == "Q"):
                command_selection = Gust_Client.COMMANDS["quit"]["command"]
                Valid = True

            if (command_selection == "L"):
                command_selection = Gust_Client.COMMANDS["list options"]["command"]
                Valid = True

        Socket.send(Encrypt_Pki.Encrypt_Message(command_selection, Socket))
        Gust_Client.Translate_Command(command_selection, Socket)

    def List_Commands(Socket):
        option_list = "Avaliable Options: \n-------------------- \n"
        for option in Gust_Client.COMMANDS:
            option_list += option + " : " + str(Gust_Client.COMMANDS[option]["command"]) + "\n"

        print(option_list)
        return option_list
    
    def Prep_Sources_Update(Socket):

        success = Integrity_Check.File_Check(Gust_Client.SOURCE_LOC)
        if (success == False):
            Socket.send("ERROR".encode())
            return False, None


        file = open(Gust_Client.SOURCE_LOC, "w")

        done = False
        file_bytes = b""

        while (done == False):
            data= Socket.recv(1024)
            file_bytes += data
            if file_bytes[-6:] == (Gust_Client.COMMANDS["end transfer"]["command"]).encode():
                done = True

        file_content = Encrypt_Pki.Decrypt_Message(file_bytes[:-6])
        file.write(file_content)

        file.close()

        print(file_content)

    def Wait_Downloads(Socket):
        print("Waiting for downloads to finish....")

        finished = Socket.recv(1024).decode()
        if (finished == Gust_Client.COMMANDS["ready check"]["command"]):
            print("Download Finished successfully")
        
        return


    def Translate_Command(Command, Socket):
        for option in Gust_Client.COMMANDS:
            if (Gust_Client.COMMANDS[option]["command"] == Command.upper()):

                if (Gust_Client.COMMANDS[option]["func"] == "None"):
                    return

                Gust_Client.COMMANDS[option]["func"](Socket)

    COMMANDS["update sources"].update({"func":Prep_Sources_Update})
    COMMANDS["transfer files"].update({"func":Prep_File_Transfer})
    COMMANDS["list options"].update({"func":List_Commands})
    COMMANDS["download files"].update({"func":Wait_Downloads})
    COMMANDS["quit"].update({"func":Close_Socket})
    