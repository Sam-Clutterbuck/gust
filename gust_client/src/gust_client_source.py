import gust_client.src.server_removal_check

import tqdm

from os import remove
from socket import AF_INET, socket, SOCK_STREAM, SHUT_RDWR
from getpass import getpass

from gust_core.src import Yaml_Editor, Commands_Global, Gust_Log, AES_Encrypt, Integrity_Check
from gust_client.src.client_config_link import Client_Global

class Gust_Client:
    
    ##############################
    # Globals

    AUTHENTICATED_USER = None

    #######################################################
    # Decorator logic

    def Run_Client(Func):
        def Connect_Socket(*Args, **Kwargs):
            with socket(AF_INET, SOCK_STREAM) as open_socket:
                open_socket.connect((Client_Global.TARGET_IP, Client_Global.TARGET_PORT))
                return Func(open_socket, *Args, **Kwargs)
        return Connect_Socket
    
    def Send_Request(Socket, Request):
        ready = Socket.recv(1024).decode()
        if (ready != Commands_Global.COMMANDS["ready check"]["command"]):
            Gust_Log.System_Log(500, "Failed Ready check on request", Socket, None)
            return False

        if (type(Request) != bytes):
            Request = Request.encode()

        Socket.sendall(Request)
        Socket.send(Commands_Global.COMMANDS["end transfer"]["command"].encode())

        return True
    
    def Recieve_Message(Socket):
        done = False
        file_bytes = b""

        while (done == False):
            request = Socket.recv(1024)
            file_bytes += request
            if (file_bytes[-6:] == Commands_Global.COMMANDS["end transfer"]["command"].encode()):
                done = True

        return file_bytes[:-6]

    def Close_Socket(Socket):
        Socket.shutdown(SHUT_RDWR)
        Socket.close()

    #######################################################
    # Command Logic

    def Sign_In():
        while True:
            username = input("Enter your username: ")
            password = getpass("Enter your password: ")

            if username is not None or password is not None:
                break

        hashed_login = username.upper() + "::::" + Integrity_Check.Sha256_Encode(password).upper()
        return hashed_login, username
            

    def Connect_Session(Func):
        def Session_Open(Socket, *Args, **Kwargs):

            Socket.send(Commands_Global.COMMANDS["session"]["command"].encode())


            encrypted_message = Gust_Client.Encrypt_Session(Gust_Client.AUTHENTICATED_USER['login']) 
            if not Gust_Client.Send_Request(Socket, encrypted_message):
                print("Invalid Session")
                Gust_Client.Close_Socket(Socket)
                return False
            
            outcome = Socket.recv(1024).decode()
            if (outcome != Commands_Global.COMMANDS["success"]["command"]):
                Gust_Log.Authentication_Log(401, f"Failed to establish session", Socket, Gust_Client.AUTHENTICATED_USER['username'])
                print("Failed to establish session")
                return False
            
            return Func(Socket, *Args, **Kwargs)
        return Session_Open
        

    def Wait_Server_Response(Socket):
        
        outcome = Socket.recv(1024).decode()
        if (outcome != Commands_Global.COMMANDS["success"]["command"]):
            failure_Reason = Gust_Client.Recieve_Message(Socket).decode()

            try:
                username = Gust_Client.AUTHENTICATED_USER['username']
            except:
                username = None

            Gust_Log.System_Log(500, failure_Reason, Socket, username)
            print(failure_Reason)
            return False, None

        message = Gust_Client.Recieve_Message(Socket)
        return True, message

    def Decrypt_Session(Socket, Encrypted_Message):
        successful, decrypted_message = AES_Encrypt.Session_Decrypt(Gust_Client.AUTHENTICATED_USER['session'], Gust_Client.AUTHENTICATED_USER['login'], Encrypted_Message)
        if not successful:
            Gust_Log.System_Log(500, f"decryption failed", Socket, Gust_Client.AUTHENTICATED_USER['username'])
            print("Decryption failed")
            return None
        
        return decrypted_message
    
    def Encrypt_Session(Message):
        encrypted_message = AES_Encrypt.Session_Encrypt(Gust_Client.AUTHENTICATED_USER['session'], Gust_Client.AUTHENTICATED_USER['login'], Message)
        return encrypted_message



    def Prep_Transfered_File(Socket, Source_Name):
        
        # check source being sent is valid
        decrypted_source_name = Gust_Client.Decrypt_Session(Socket, Source_Name)
        if decrypted_source_name is None:
            return False

        valid = False
        for header in Yaml_Editor.List_Headers(Client_Global.SOURCE_LOC):
            if (header == decrypted_source_name):
                print(f"Server prepping {decrypted_source_name} for transfer")
                valid = True
        
        if not valid:
            print(f"Server attempted to send invalid source: {decrypted_source_name}")
            Socket.send(Commands_Global.COMMANDS["failure"]["command"].encode())
            return False

        #confirm source is valid
        Socket.send(Commands_Global.COMMANDS["success"]["command"].encode())

        # recieve hash
        successful, hash_file = Gust_Client.Recieve_File(Socket)
        if not successful:
            return False
        print(f"successfully recieved hash file : {hash_file}")

        # recieve source
        successful, source_file = Gust_Client.Recieve_File(Socket)
        if not successful:
            return False
        print(f"successfully recieved source file : {source_file}")
        
        

        # check hashes of new files
        matching_hashes = Integrity_Check.Hash_Check(source_file, hash_file, Yaml_Editor.Breakdown_Dictionary(decrypted_source_name,Client_Global.SOURCE_LOC)['hash_type'])
        if (matching_hashes == False):
            print("Hash check failed")
            remove(source_file)
            remove(hash_file)
            return False
        
        return True


    def Recieve_File(Socket):

        encrypted_filename = Socket.recv(1024)
        encrypted_file_size = Socket.recv(1024)

        filename = Gust_Client.Decrypt_Session(Socket, encrypted_filename)
        if filename is None:
            Socket.send(Commands_Global.COMMANDS["failure"]["command"].encode())
            return False, None
        file_size = Gust_Client.Decrypt_Session(Socket, encrypted_file_size)
        if file_size is None:
            Socket.send(Commands_Global.COMMANDS["failure"]["command"].encode())
            return False, None
        
        print(f"Downloading : {filename}")
        print(f"File size : {Gust_Client.Byte_Size_Conversion(file_size)}")
        
        success = Integrity_Check.Dir_Check(Client_Global.DOWNLOAD_LOC)
        if (success == False):
            Socket.send(Commands_Global.COMMANDS["failure"]["command"].encode())
            return False, None

         # if valid prepare for file transfer

        Socket.send(Commands_Global.COMMANDS["ready check"]["command"].encode())

        # write file content
        file = open(Client_Global.DOWNLOAD_LOC+filename, "w")

        done = False
        file_bytes = b""

        # Create progress bar
        progress = tqdm.tqdm(unit="8", unit_scale=True, unit_divisor=1000, total=int())

        while (done == False):
            data= Socket.recv(1024)
            file_bytes += data
            if (file_bytes[-6:] == Commands_Global.COMMANDS["end transfer"]["command"].encode()):
                done = True
            progress.update(1024)

        recieved_content = Gust_Client.Decrypt_Session(Socket, file_bytes[:-6])
        if recieved_content is None:
            Socket.send(Commands_Global.COMMANDS["failure"]["command"].encode())
            file.close()
            
            return False, None
        
        file.write(recieved_content)

        file.close()

        Socket.send(Commands_Global.COMMANDS["success"]["command"].encode())
        return True, Client_Global.DOWNLOAD_LOC+filename


    def Byte_Size_Conversion(Bytes):

        if (type(Bytes) != int):
            try:
                Bytes = int(Bytes)
            except:
                return Bytes

        if (Bytes <= 0):
            return "0B"
        
        names = ['B', 'KB', 'MB', 'GB', 'TB']
        converted = False
        steps = 0
        while not converted:
            if (Bytes <= 1024):
                 converted = True
                 break
            Bytes = Bytes / 1024
            steps += 1
            
        return f"{round(Bytes, 2)} {names[steps]}"
            


    #######################################################
    # Actual Commands

    @Run_Client
    def Authenticate(Socket):
        # Send authentication request
        Socket.send(Commands_Global.COMMANDS["authenticate"]["command"].encode())
        
        login, username = Gust_Client.Sign_In()
        encrypted_message = AES_Encrypt.Login_Encrypt(login, f"{Socket.getsockname()[0]}:{Socket.getsockname()[1]}", login)

        if not Gust_Client.Send_Request(Socket, encrypted_message):
            print("Connection Issue occured")
            Gust_Client.Close_Socket(Socket)
            return False
        

        # Ensure no errors occur
        successful, session_info = Gust_Client.Wait_Server_Response(Socket)
        if not successful:
            return False

        # Decrypt session info

        successful, decrypted_session = AES_Encrypt.Login_Decrypt(login, f"{Socket.getsockname()[0]}:{Socket.getsockname()[1]}" , session_info)
        if not successful:
            Gust_Log.System_Log(500, f"Authentication message decryption failed", Socket, username)
            print("Decryption failed")

        session = Yaml_Editor.Yaml_Load(decrypted_session)
        session.update({'login': login})

        Gust_Client.AUTHENTICATED_USER = session

        Gust_Client.Close_Socket(Socket)
        return True

    @Run_Client
    def Send_Quit_Notif(Socket):

        Socket.send(Commands_Global.COMMANDS["quit"]["command"].encode())

        Gust_Client.Send_Request(Socket, Gust_Client.AUTHENTICATED_USER['login'])

        return


    @Run_Client
    @Connect_Session
    def Update_Sources(Socket):

        # Send source list request

        Socket.send(Commands_Global.COMMANDS["update sources"]["command"].encode())

        encrypted_message = Gust_Client.Encrypt_Session(Commands_Global.COMMANDS["update sources"]["command"])  

        if not Gust_Client.Send_Request(Socket, encrypted_message):
            print("Connection Issue occured")
            Gust_Client.Close_Socket(Socket)
            return False

        # Ensure no errors occur
        successful, source_list = Gust_Client.Wait_Server_Response(Socket)
        if not successful:
            return False
        
        # Decrypt recieved source list

        decrypted_source_list = Gust_Client.Decrypt_Session(Socket, source_list)
        if decrypted_source_list is None:
            return False

        formated_source_list = Yaml_Editor.Yaml_Load(decrypted_source_list)

        if not Yaml_Editor.Yaml_Write(Client_Global.SOURCE_LOC, formated_source_list):
            print("Failed to update client source list")
            Gust_Client.Close_Socket(Socket)
        
        Gust_Client.Close_Socket(Socket)
        return True




    @Run_Client
    @Connect_Session
    def Transfer_Source(Socket, Target_Source):

        # Send transfer request
        Socket.send(Commands_Global.COMMANDS["transfer files"]["command"].encode())

        encrypted_source = Gust_Client.Encrypt_Session(Target_Source)

        if not Gust_Client.Send_Request(Socket, encrypted_source):
            print("Connection Issue occured")
            Gust_Client.Close_Socket(Socket)
            return False
        
        # Ensure no errors occur
        successful, source_name = Gust_Client.Wait_Server_Response(Socket)
        if not successful:
            return False
        
        # prep to recieve the files
        Valid_Files_Recieved = Gust_Client.Prep_Transfered_File(Socket, source_name)
        if not Valid_Files_Recieved:
            return False
        
        return True


                    
