
from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread

from core.src import Yaml_Editor, Data_Link, Gust_Log, Encrypt_Pki
from server.src.file_transferer import File_Transfer
from server.src.gust_sources import Gust_Sources
from server.src.Login_systems import Login_Auth

class Server_Commands:

    #####################
    #Globals
    success, yaml_file = Yaml_Editor.Yaml_Read(Data_Link.commands)
    if (success == False):
        yaml_file = {}
    COMMANDS = yaml_file
    #####################

    def Translate_Command(Command, Client):
        for option in Server_Commands.COMMANDS:
            if (Server_Commands.COMMANDS[option]["command"] == Command.upper()):
        
                if (Server_Commands.COMMANDS[option]["func"] == "None"):
                    return
                
                Server_Commands.COMMANDS[option]["func"](Client)

    def Update_Sources(Client):
        success, yaml_file = Yaml_Editor.Yaml_Read(Gust_Server.SOURCE_LOC)
        if (success == False):
            return None
        
        source_yaml = {}
        
        for source in yaml_file:
        
            pairs = {source: {"hash_type": yaml_file[source]['hash_type']}}
            source_yaml.update(pairs)

        encrypted_source = Encrypt_Pki.Encrypt_Message(Yaml_Editor.Yaml_Dump(source_yaml), Client)
        Client.sendall(encrypted_source)
        Client.send(Server_Commands.COMMANDS["end transfer"]["command"].encode())
        
    def Download(Client):
        Gust_Sources.Download_Sources()
        Client.send(Server_Commands.COMMANDS["ready check"]["command"].encode())

    def Transfer(Client):

        source_list = Yaml_Editor.List_Headers(Gust_Server.DOWNLOAD_LOG_LOC)
               
        for source in source_list:
            breakdown = Yaml_Editor.Breakdown_Dictionary(source, Gust_Server.DOWNLOAD_LOG_LOC)
            
            File_Transfer.Transfer_Files(source, breakdown, Client)

    def Quit(Client):
        Gust_Server.Gracefull_Close(Client)

    COMMANDS["update sources"].update({"func":Update_Sources})
    COMMANDS["download files"].update({"func":Download})
    COMMANDS["transfer files"].update({"func":Transfer})
    COMMANDS["quit"].update({"func":Quit})
    

class Gust_Server:
    
    #####################
    #Globals
    success, yaml_file = Yaml_Editor.Yaml_Read(Data_Link.server_config)
    if (success == False):
        yaml_file = {}
    CONFIG_FILE = yaml_file

    HOST_IP = CONFIG_FILE["ip"]
    HOST_PORT = CONFIG_FILE["port"]
    LOGIN_ATTEMPT_LIMIT = CONFIG_FILE["connection attempt limit"]
    MAX_CONCURRENT_USERS = CONFIG_FILE["max concurrent users"]
    DOWNLOAD_LOG_LOC= CONFIG_FILE["download_log_loc"]
    SOURCE_LOC = CONFIG_FILE["server_sources_loc"]

    CONCURRENT_CONNECTIONS = {}

    SERVERSOCKET = socket(AF_INET, SOCK_STREAM)
    #####################

    def Connection_Check(Client):
        if Client is None or (Client._closed == True):
            Gust_Log.System_Log(500,"No active connection",None, None)
            quit()

    def Start_Server():
        
        try:
            Gust_Server.SERVERSOCKET.bind((Gust_Server.HOST_IP, Gust_Server.HOST_PORT))
        except socket.error as error:
            Gust_Log.System_Log(500,str(error),None, None)

        print('Socket is listening..')
        Gust_Server.SERVERSOCKET.listen(5)
        Encrypt_Pki.Create_Keys()

        #Set up seperate thread for each connecting client
        while True:
            client, addr = Gust_Server.SERVERSOCKET.accept()
            print('Connection attempt by: ' + addr[0] + ':' + str(addr[1]))
            new_thread = Thread(target=Gust_Server.Server_Steps, args=(client, ))
            new_thread.start()
        SERVERSOCKET.close()


    def Server_Steps(Client):
        
        Gust_Server.Connection_Check(Client)

        authorised = False
        
        #login authorisation checks
        while not authorised:
            try:

                ##handle for disconnect
                Gust_Server.Connection_Check(Client)

                success = Gust_Server.Attempt_Login(Client)
                if (success == True):
                    authorised = True

            except OSError as error:
                if (Client._closed == False):
                    Gust_Log.System_Log(500,str(error),Client, None)
                return
            

        #authorised tasks once logged in
        while authorised:
            try:

                ##handle for disconnect
                Gust_Server.Connection_Check(Client)

                Gust_Server.Recieve_Commands(Client)

            except OSError as error:
                if (Client._closed == False):
                    Gust_Log.System_Log(500,str(error),Client, Gust_Server.CONCURRENT_CONNECTIONS[Client])
                return 
        
        Gust_Server.Gracefull_Close(Client)

    def Attempt_Login(Client):

        successful_login = False
        login_attempts = 0

        while not successful_login:
            login_details = Client.recv(1024).decode()
            success, username = Gust_Server.Login_Authorisation(login_details)
                    
            if (success == False):
                login_attempts +=1

                if (login_attempts >= Gust_Server.LOGIN_ATTEMPT_LIMIT):
                    Gust_Log.Authentication_Log(403, "Excessive Failed login attempts for :" + username, Client, username)
                    Client.send(("Excessive Failed login - Disconnected from server"+Server_Commands.COMMANDS["disconnect"]["command"]).encode())
                    Client.send("Safe to close".encode())
                    Client.close()

                Gust_Log.Authentication_Log(401, "Incorrect login details for :" + username, Client, username)
                Client.send("Incorrect login details".encode())
            
            else:
                
                if (len(Gust_Server.CONCURRENT_CONNECTIONS) >= Gust_Server.MAX_CONCURRENT_USERS):
                    
                    print("SENT")
                    Client.send(("Max concurrent users reached - please wait and try again later"+Server_Commands.COMMANDS["disconnect"]["command"]).encode())
                    Client.close()
                    quit()

                Gust_Log.Authentication_Log(200, username + " Logged into server", Client, username)
                Client.send((Server_Commands.COMMANDS["authorised"]["command"]).encode())

                Gust_Server.CONCURRENT_CONNECTIONS.update({Client:username})

                Gust_Server.Send_Public_Key(Client, login_details)

                successful_login = True
            
        return successful_login


    def Login_Authorisation(Login_Details):

        if Login_Details is None:
            return False, "No Username Entered"

        success, username = Login_Auth.Login_Check(Login_Details)
        return success, username
    
    def Send_Public_Key(Client, Login_Details):

        authenticated= False
        auth_attempts = 0

        while not authenticated:
        
            encrypted_public_key = Encrypt_Pki.Prep_Public_Key(Login_Details)
            Client.send(encrypted_public_key)

            confirmation = Client.recv(1024)
            Encrypt_Pki.Decrypt_Public_Key(confirmation, Login_Details, Client)

            encrypted_message = Encrypt_Pki.Encrypt_Message(Server_Commands.COMMANDS["authorised"]["command"], Client)
            Client.send(encrypted_message)

            confirmation = Client.recv(1024)
            decrypted_confirmation = Encrypt_Pki.Decrypt_Message(confirmation)

            if (decrypted_confirmation == Server_Commands.COMMANDS["authorised"]["command"]):
                Gust_Log.Authentication_Log(200, "Public key passed to client successfully", Client, Gust_Server.CONCURRENT_CONNECTIONS[Client])
                authenticated = True
                return 
            
            if (auth_attempts >= Gust_Server.LOGIN_ATTEMPT_LIMIT):
                Gust_Log.Authentication_Log(403, "Excessive Failed Public Key authoriusation attempts ", Client, Gust_Server.CONCURRENT_CONNECTIONS[Client])
                Client.send(("Excessive Failed Public Key authorisation attempts - Disconnected from server"+Server_Commands.COMMANDS["disconnect"]["command"]).encode())
                Gust_Server.Gracefull_Close(Client)

            Gust_Log.Authentication_Log(401, "Incorrect public keys", Client, Gust_Server.CONCURRENT_CONNECTIONS[Client])
                
    def Recieve_Commands(Client):

        recieved_command = Encrypt_Pki.Decrypt_Message(Client.recv(1024))
        Server_Commands.Translate_Command(recieved_command, Client)
        
    def Gracefull_Close(Client):
        Gust_Server.CONCURRENT_CONNECTIONS.pop(Client)

        Client.send("Safe to disconnect".encode())
        Client.close()
        quit()