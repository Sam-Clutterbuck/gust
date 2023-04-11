from core.src import Integrity_Check, Data_Link, Gust_Log, Yaml_Editor

class Login_Auth:

    success, yaml_file = Yaml_Editor.Yaml_Read(Data_Link.server_config)
    if (success == False):
        yaml_file = {}
    CONFIG_FILE = yaml_file

    LOGINS = CONFIG_FILE["logins_loc"]

    def List_Logins():

        login_list = []
        with open(Login_Auth.LOGINS, 'r') as login_file:
            while True:
                try:
                    next_line = login_file.readline()

                    if not next_line:
                        break
                    login_list.append(next_line.strip().upper())
                
                except :
                    Gust_Log.System_Log(500,"Error occured reading from file", None, None)

        return login_list

    def Login_Check(Hashed_Login):
    
        #Find username and return to call for logging
        username = Login_Auth.Username_Grab(Hashed_Login)

        exists = Integrity_Check.File_Check(Login_Auth.LOGINS)

        if (exists == False):
            return False, username

        login_list = Login_Auth.List_Logins()
                

        for login in login_list:
            if (login == Hashed_Login.upper()):
                return True, username
        
        return False, username
        
        
    def Username_Grab(Hashed_Login):
        #custom script to grab the username without needing to allow regex import
        username = ""
        seperators_found = 0

        for char in Hashed_Login:
            if (char == ":"):
                seperators_found += 1
                if (seperators_found >= 4):
                    break
            else:
                username += char
        
        return username