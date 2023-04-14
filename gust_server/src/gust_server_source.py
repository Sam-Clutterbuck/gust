import gust_server.src.client_removal_check 

import secrets

from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
from datetime import datetime

from gust_core.src import Yaml_Editor, Commands_Global, Gust_Log, AES_Encrypt, Integrity_Check
from gust_server.src.file_transferer import File_Transfer
from gust_server.src.login_systems import Login_Auth
from gust_server.src.server_config_link import Server_Global

class Gust_Server:

    #####################
    #Globals

    CONCURRENT_SESSIONS = {}
    SERVERSOCKET = socket(AF_INET, SOCK_STREAM)
    #####################







    def Start_Server():

        try:
            Gust_Server.SERVERSOCKET.bind((Server_Global.HOST_IP, Server_Global.HOST_PORT))
        except socket.error as error:
            Gust_Log.System_Log(500,str(error),None, None)

        print('Socket is listening..')
        Gust_Server.SERVERSOCKET.listen(5)

        #Set up seperate thread for each connecting client
        while True:
            client, addr = Gust_Server.SERVERSOCKET.accept()
            print('Connection attempt by: ' + addr[0] + ':' + str(addr[1]))
            new_thread = Thread(target=Gust_Server.Connection_Thread, args=(client, ))
            new_thread.start()
        SERVERSOCKET.close()

    def Connection_Thread(Client):
    
        request = Client.recv(1024).decode()

        for command in Commands_Global.COMMANDS:
            if (request.upper() == Commands_Global.COMMANDS[command]["command"].upper()):
                Commands_Global.COMMANDS[command]["func"](Client)


    def Client_Recieve(Func):
        def Recieve_All(Client, *Args, **Kwargs):

                Client.send(Commands_Global.COMMANDS["ready check"]["command"].encode())
                done = False
                file_bytes = b""

                while (done == False):
                    request = Client.recv(1024)
                    file_bytes += request
                    if (file_bytes[-6:] == Commands_Global.COMMANDS["end transfer"]["command"].encode()):
                        done = True

                return Func(Client, file_bytes[:-6], *Args, **Kwargs)

        return Recieve_All







    #################################################
    # Helpers

    def AES_Login_Checks(Message, Client):
        
        login_list = Login_Auth.List_Logins()

        for login in login_list:
            success, decrypted_message = AES_Encrypt.Login_Decrypt(login, f"{Client.getpeername()[0]}:{Client.getpeername()[1]}" , Message)
            if success:
                return True, decrypted_message
        
        Gust_Log.Authentication_Log(401, "Failed to authenticate login", Client, None)
        return False, None
    
    def AES_Session_Checks(Message, Client):

        for user in Gust_Server.CONCURRENT_SESSIONS:
            success, decrypted_message = AES_Encrypt.Session_Decrypt(Gust_Server.CONCURRENT_SESSIONS[user]['session'], user , Message)
            if success:
                return True, decrypted_message
        
        Gust_Log.Authentication_Log(401, "Failed to authenticate session", Client, None)
        return False, None

    def Send_Response(Message, Client):

        if (type(Message) != bytes):
            Message = Message.encode()

        Client.sendall(Message)
        Client.send(Commands_Global.COMMANDS["end transfer"]["command"].encode())

        return True


    def Prep_Source_List():

        success, source_file = Yaml_Editor.Yaml_Read(Server_Global.SOURCE_LOC)
        if (success == False):
            return None
        
        success, download_log_file = Yaml_Editor.Yaml_Read(Server_Global.DOWNLOAD_LOG_LOC)
        if (success == False):
            return None
        
        client_source_list = {}
        
        for source in source_file:
            
            formatted_source = {source:{"hash_type": source_file[source]['hash_type']}}
            
            if Integrity_Check.File_Check(Server_Global.DOWNLOAD_LOC+download_log_file[source]['file']):
                    formatted_source[source].update({"avaliable":'True'})
            else:
                formatted_source[source].update({"avaliable":'False'})

            try:
                formatted_source[source].update({"last downloaded":download_log_file[source]['last updated']})  
            except:
                formatted_source[source].update({"last downloaded":"unknown"}) 

            client_source_list.update(formatted_source)

        return client_source_list


    def Session_Checks():
        
        pop_clients = []

        for session in Gust_Server.CONCURRENT_SESSIONS:
            # close any expires sessions

            session_date = Gust_Server.CONCURRENT_SESSIONS[session]['session_time'][:-4]
            current_date = datetime.now().strftime("%d%m%Y") 

            session_time = Gust_Server.CONCURRENT_SESSIONS[session]['session_time'][-4:]
            current_time = datetime.now().strftime("%H%M") 

            #ensure the session was for today
            if (current_date != session_date):
                pop_clients.append(session)

            hours = int(session_time[:-2]) * 60
            session_minutes = hours + int(session_time[-2:])

            hours = int(current_time[:-2]) * 60
            current_minutes = hours + int(current_time[-2:])

            time_diff = current_minutes - session_minutes

            print(time_diff)

            if (time_diff >= Server_Global.SESSION_LIMIT):
                pop_clients.append(session)


        for client in pop_clients:
            Gust_Server.CONCURRENT_SESSIONS.pop(client)




    #################################################
    # COMMANDS
    
    @Client_Recieve
    def Authenticate_User(Client, Request):

        # recieve auth request
        successful, decrypted_login = Gust_Server.AES_Login_Checks(Request, Client)
        if not successful:
            Client.send(Commands_Global.COMMANDS["failure"]["command"].encode())
            Gust_Server.Send_Response("Login Authentication Failed" , Client)
            return
        
        ## Authenticated User
        
        Gust_Server.Session_Checks()

        if (len(Gust_Server.CONCURRENT_SESSIONS) >= Server_Global.MAX_CONCURRENT_USERS):
            Client.send(Commands_Global.COMMANDS["failure"]["command"].encode())
            Gust_Server.Send_Response("Max number of sessions exceeded" , Client)
            return


        Gust_Log.Authentication_Log(200, f"Authenticated user {Login_Auth.Username_Grab(decrypted_login)}", Client, Login_Auth.Username_Grab(decrypted_login))
        session = secrets.token_hex(32)
        session_time = datetime.now().strftime("%d%m%Y%H%M") 

        Gust_Server.CONCURRENT_SESSIONS.update({decrypted_login:{'username':Login_Auth.Username_Grab(decrypted_login), 'session':session, 'session_time':session_time}}) 
        print(Gust_Server.CONCURRENT_SESSIONS)

        ## Inform client and send session data
        Client.send(Commands_Global.COMMANDS["success"]["command"].encode())
        session_data = Yaml_Editor.Yaml_Dump(Gust_Server.CONCURRENT_SESSIONS[decrypted_login])
        encrypted_session_data = AES_Encrypt.Login_Encrypt(decrypted_login, f"{Client.getpeername()[0]}:{Client.getpeername()[1]}", session_data)
        Gust_Server.Send_Response(encrypted_session_data , Client)
        return




    @Client_Recieve
    def Session_Open(Client, Request):

        Gust_Server.Session_Checks()

        # recieve session request
        successful, decrypted_user = Gust_Server.AES_Session_Checks(Request, Client)
        if not successful:
            Client.send(Commands_Global.COMMANDS["failure"]["command"].encode())
            return


        # Success response

        Client.send(Commands_Global.COMMANDS["success"]["command"].encode())

        # recieve further function request for this session
        request = Client.recv(1024).decode()

        for command in Commands_Global.COMMANDS:
            if (request.upper() == Commands_Global.COMMANDS[command]["command"].upper()):
                Commands_Global.COMMANDS[command]["func"](Client, decrypted_user)
        




    @Client_Recieve
    def Transfer_Source_List(Client, Request, Session_User):
        
        # recieve source list request

        if Session_User is None:
            Gust_Log.Authentication_Log(403, f"Request With unknown Session recieved", Client, None)
            Client.send(Commands_Global.COMMANDS["failure"]["command"].encode())
            Gust_Server.Send_Response("Request With unknown Session recieved" , Client)
            return
        
        success, decrypted_message = AES_Encrypt.Session_Decrypt(Gust_Server.CONCURRENT_SESSIONS[Session_User]['session'], Session_User , Request)
        if not success:
            Client.send(Commands_Global.COMMANDS["failure"]["command"].encode())
            Gust_Server.Send_Response("Request With Invalid Session recieved" , Client)
            return False

        if (decrypted_message != Commands_Global.COMMANDS["update sources"]["command"]):
            Gust_Log.Authentication_Log(404, f"Recieved an Invalid request during source list transfer : {decrypted_message}", Client, Gust_Server.CONCURRENT_SESSIONS[Session_User]['username'])
            Client.send(Commands_Global.COMMANDS["failure"]["command"].encode())
            Gust_Server.Send_Response("Recieved an Invalid request during source list transfer" , Client)
            return False
        
        # Success response
        #send source list

        source_list = Gust_Server.Prep_Source_List()
        encrypted_source_list = AES_Encrypt.Session_Encrypt(Gust_Server.CONCURRENT_SESSIONS[Session_User]['session'], Session_User, Yaml_Editor.Yaml_Dump(source_list))
       
        Client.send(Commands_Global.COMMANDS["success"]["command"].encode())
        Gust_Server.Send_Response(encrypted_source_list , Client)

        Gust_Log.System_Log(200, f"Sent Source list to {Gust_Server.CONCURRENT_SESSIONS[Session_User]['username']}", Client, Gust_Server.CONCURRENT_SESSIONS[Session_User]['username'])

        return
    



    @Client_Recieve
    def Transfer_File(Client, Request, Session_User):

        # recieve transfer request
        if Session_User is None:
            Gust_Log.Authentication_Log(403, f"Request With unknown Session recieved", Client, None)
            return
        
        success, decrypted_source = AES_Encrypt.Session_Decrypt(Gust_Server.CONCURRENT_SESSIONS[Session_User]['session'], Session_User , Request)
        if not success:
            Client.send(Commands_Global.COMMANDS["failure"]["command"].encode())
            Gust_Server.Send_Response("Request With Invalid Session recieved" , Client)
            return False

        #check source is avaliable to download
        downloaded_source = False
        for header in Yaml_Editor.List_Headers(Server_Global.DOWNLOAD_LOG_LOC):
            if (decrypted_source == header):
                downloaded_source = True

        if not downloaded_source:
            Client.send(Commands_Global.COMMANDS["failure"]["command"].encode())
            Gust_Server.Send_Response("attempted to transfer a file that hasn't been downloaded" , Client)
            return False
        
        # check that the file is downloaded even if its logged
        downloaded_file = Integrity_Check.File_Check(Server_Global.DOWNLOAD_LOC+Yaml_Editor.Breakdown_Dictionary(decrypted_source,Server_Global.DOWNLOAD_LOG_LOC)['hash_file'])
        if not downloaded_file:
            Client.send(Commands_Global.COMMANDS["failure"]["command"].encode())
            Gust_Server.Send_Response("attempted to transfer a file that hasn't been downloaded" , Client)
            return False
        
        # Success response
        # send source being transfered for confirmation

        Client.send(Commands_Global.COMMANDS["success"]["command"].encode())

        encrypted_source_name = AES_Encrypt.Session_Encrypt(Gust_Server.CONCURRENT_SESSIONS[Session_User]['session'], Session_User, decrypted_source)
        Gust_Server.Send_Response(encrypted_source_name , Client)


        File_Transfer.Transfer_Files(decrypted_source, Yaml_Editor.Breakdown_Dictionary(decrypted_source, Server_Global.DOWNLOAD_LOG_LOC), Client, Gust_Server.CONCURRENT_SESSIONS, Session_User)

        return

    @Client_Recieve
    def Quit_Notif(Client, Request):

        if Request.decode() not in Gust_Server.CONCURRENT_SESSIONS:
            return

        Gust_Server.CONCURRENT_SESSIONS.pop(Request.decode())

        return
    

    Commands_Global.COMMANDS["authenticate"].update({"func":Authenticate_User})
    Commands_Global.COMMANDS["session"].update({"func":Session_Open})
    Commands_Global.COMMANDS["update sources"].update({"func":Transfer_Source_List})
    Commands_Global.COMMANDS["transfer files"].update({"func":Transfer_File})
    Commands_Global.COMMANDS["quit"].update({"func":Quit_Notif})








