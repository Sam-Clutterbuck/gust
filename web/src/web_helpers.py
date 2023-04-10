from functools import wraps
from flask import Flask, render_template, request, session, redirect, url_for, flash

from core.src import Yaml_Editor, Data_Link, Integrity_Check
from server.src import Login_Auth

class Web_Helpers:

    #####################
    #Globals

    success, yaml_file = Yaml_Editor.Yaml_Read(Data_Link.server_config)
    if (success == False):
        yaml_file = {}
    CONFIG_FILE = yaml_file

    SOURCE_LOC = CONFIG_FILE["server_sources_loc"]

    #####################

    def Authentication_Check(Func):
        @wraps(Func)
        def Check_For_User(*Args, **Kwargs):

            if "user" in session:
                if (session["authenticated"] == True):
                    return Func(*Args, **Kwargs)
            
            return redirect( url_for("Login_Blocker"))
        return Check_For_User

    def Get_Sources_Number():
        sources = Yaml_Editor.List_Headers(Web_Helpers.SOURCE_LOC)

        if sources is None:
            return 0

        return len(sources)
    
    def Get_Source_Details():
        sources = Yaml_Editor.List_Headers(Web_Helpers.SOURCE_LOC)

        data = []

        if sources is None:
            return {}

        for header in sources:
            values = [header]
            pairs = Yaml_Editor.Breakdown_Dictionary(header,Web_Helpers.SOURCE_LOC)

            for key in pairs:
                values.append(pairs[key])

            data.append(values)
        
        return data
    
    def Get_Source_Data():
        source_headings = ["Source Name","Source Url","Hash Url","Hash Type"]
        data = Web_Helpers.Get_Source_Details()

        source_ammount = Web_Helpers.Get_Sources_Number()

        return source_ammount, source_headings, data
    
    def Log_In(Username, Password):

        hashed_login = Username + "::::" + Integrity_Check.Sha256_Encode(Password)

        success, username = Login_Auth.Login_Check(hashed_login)

        if success:
            session["user"] = Username
            session["authenticated"] = True #could make more complex authentication controls later
            return True, redirect(url_for("Home"))
        
        flash("Incorrect username or password", "warning")
        return False, None

    def Log_Out():
        if "authenticated" in session:
            session.pop("authenticated")
        if "user" in session:
            session.pop("user")