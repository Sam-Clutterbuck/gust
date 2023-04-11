from server.src.login_systems import Login_Auth
from core.src import Integrity_Check, Gust_Log

class Account_Control:

    def Account_Exists(Username):
        logins = Login_Auth.List_Logins()

        for login in logins:
            username = Login_Auth.Username_Grab(login).upper()
            if (username == Username.upper()):
                return True
        
        return False
    
    def Format_Username(Username, Password):
        hashed_login = Username.upper() + "::::" + Integrity_Check.Sha256_Encode(Password).upper()
        return hashed_login

    def Verify(Func):
        def Admin_Verification(Admin_Account, *Args, **Kargs):
        
            if Admin_Account is None:
                Gust_Log.Authentication_Log(401,f"Attempted to edit user without any admin details entered", None, None)
                return False

            valid_admin, admin_username = Login_Auth.Login_Check(Admin_Account)
            if not valid_admin:
                Gust_Log.Authentication_Log(403,f"Attempted to edit user without valid admin details", None, admin_username)
                return False
            
            return Func(admin_username, *Args, **Kargs)
        return Admin_Verification


    @Verify
    def Add_User(Admin_Verification, New_User, New_Password):

        if Account_Control.Account_Exists(New_User):
            Gust_Log.System_Log(500,f"Trying to create user {New_User} that already exists", None, Admin_Verification)
            return False
        
        with open(Login_Auth.LOGINS, 'a') as login_file:
            login_file.write(Account_Control.Format_Username(New_User,New_Password)+"\n")

        Gust_Log.System_Log(200,f"Created New user: {New_User}", None, Admin_Verification)

        return True
    
    @Verify
    def Password_Reset(Admin_Verification, Target_User, New_Password):
       
        if not Account_Control.Account_Exists(Target_User):
            Gust_Log.Authentication_Log(404,f"Attempted to edit a user ({Target_User}) who doesn't exist", None, Admin_Verification)
            return False

        logins = Login_Auth.List_Logins()

        new_login_list = []
        for login in logins:
            if (Login_Auth.Username_Grab(login).upper() == Target_User.upper()):
                new_login_list.append(Account_Control.Format_Username(Target_User,New_Password))
            else:
                new_login_list.append(login)

        with open(Login_Auth.LOGINS, 'w') as login_file:
            for login in new_login_list:
                login_file.write(login+"\n")

        Gust_Log.System_Log(200,f"Edited passworded for user: {Target_User}", None, Admin_Verification)
        
        return
    
    @Verify
    def Delete_User(Admin_Verification, Target_User):

        if not Account_Control.Account_Exists(Target_User):
            Gust_Log.Authentication_Log(404,f"Attempted to delete a user ({Target_User}) who doesn't exist", None, Admin_Verification)
            return False

        logins = Login_Auth.List_Logins()

        new_login_list = []
        for login in logins:
            if (Login_Auth.Username_Grab(login).upper() != Target_User.upper()):
                new_login_list.append(login)

        with open(Login_Auth.LOGINS, 'w') as login_file:
            for login in new_login_list:
                login_file.write(login+"\n")

        Gust_Log.System_Log(200,f"Deleted user: {Target_User}", None, Admin_Verification)

        return
    