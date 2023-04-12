import gust_server.src.client_removal_check 

from datetime import datetime
from functools import wraps
from flask import request, session, redirect, url_for, flash

from gust_core.src import Yaml_Editor, Integrity_Check
from gust_server.src import Login_Auth, File_Download, Server_Global, Gust_Sources

class Web_Helpers:

    def Authentication_Check(Func):
        @wraps(Func)
        def Check_For_User(*Args, **Kwargs):

            if "user" in session:
                if (session["authenticated"] == True):
                    return Func(*Args, **Kwargs)
            
            return redirect( url_for("Login_Blocker"))
        return Check_For_User

    def Get_Header_Number(Location):
        sources = Yaml_Editor.List_Headers(Location)

        if sources is None:
            return 0

        return len(sources)
    
    def Get_Details(Location):
        sources = Yaml_Editor.List_Headers(Location)

        data = []

        if sources is None:
            return {}

        for header in sources:
            values = [header]
            pairs = Yaml_Editor.Breakdown_Dictionary(header,Location)

            for key in pairs:
                values.append(pairs[key])

            data.append(values)
        
        return data
    
    def Get_Source_Data():
        source_headings = ["Source Name","Source Url","Hash Url","Hash Type"]
        data = Web_Helpers.Get_Details(Server_Global.SOURCE_LOC)

        source_ammount = Web_Helpers.Get_Header_Number(Server_Global.SOURCE_LOC)

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

    def Url_Log(Func):
        @wraps(Func)
        def Store_Current_Url(*Args, **Kwargs):
            ## store the url of page for redirects that need to return back to a specific page
            session["current_url"] = request.url
            return Func(*Args, **Kwargs)
        return Store_Current_Url
    
    def Get_Previous_Url():
        return session["current_url"]
    
    def Get_Downloads_Data():
        headings = ["Source Name","Last Updated","Updated Today", "Download Progress"]
        time = datetime.now().strftime("%a %d %b %Y")

        sources = Yaml_Editor.List_Headers(Server_Global.SOURCE_LOC)
        
        data = Web_Helpers.Get_Details(Server_Global.DOWNLOAD_LOG_LOC)

        format_data = []

        for row in data:
            temp_data = []
            temp_data.append(row[0])
            temp_data.append(row[3])
            if time in row[3]:
                temp_data.append(True)
                
            format_data.append(temp_data)

        #add any sources that exist but aren't downloaded
        for source in sources:
            match = False
            for row in format_data:
                if (row[0] == source):
                    match = True
                    break 
            
            if not match:
                format_data.append([source])


        ammount = Web_Helpers.Get_Header_Number(Server_Global.DOWNLOAD_LOG_LOC)

        

        return ammount, headings, format_data
    
    def Download_Info():

        sources = Web_Helpers.Get_Details(Server_Global.SOURCE_LOC)

        staged_data = []

        for source in sources:
            if source[1] in File_Download.DOWNLOADING_STATUS:
                percentage = (File_Download.DOWNLOADING_STATUS[source[1]]['download_ammmount'] / File_Download.DOWNLOADING_STATUS[source[1]]['file_size']) * 100
                staged_data.append([source[0], percentage])
            else:

                #check for undownloaded sources
                downloads = Web_Helpers.Get_Details(Server_Global.DOWNLOAD_LOG_LOC)
                
                downloaded_source = False
                for downloded in downloads:
                    if (source[0] == downloded[0]):
                        downloaded_source = True
                
                if downloaded_source:
                    staged_data.append([source[0], 100])
                else:
                    staged_data.append([source[0], 0])

        return staged_data
    

    def New_Or_Update(Name,URL,Hash_URL,Hash_Type):

        success, yaml_file = Yaml_Editor.Yaml_Read(Server_Global.SOURCE_LOC)
        if (success == False):
            return None

        exists = False
        for source in yaml_file:
                if (source == Name):
                    exists = True

        if exists:
            Gust_Sources.Update_Source(Name,URL,Hash_URL,Hash_Type)
        else:
            Gust_Sources.Add_Source(Name,URL,Hash_URL,Hash_Type)