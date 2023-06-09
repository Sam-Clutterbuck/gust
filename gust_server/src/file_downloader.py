import gust_server.src.client_removal_check 

import re
import requests

from datetime import datetime

from gust_core.src import  Yaml_Editor, Integrity_Check, Gust_Log
from gust_server.src.server_config_link import Server_Global


class File_Download:
   
   #####################
   #Globals

    DOWNLOADING_STATUS = {}

   #####################

    def Find_Filename(Header):
        #get filename from download header

        content = Header['Content-Disposition']
        filename_extended = re.findall("filename=\".*\"", content)
        filename = re.split("\"", filename_extended[0])

        return filename[1]
   
    def Download_File(url):
       
        success = Integrity_Check.Dir_Check(Server_Global.DOWNLOAD_LOC) 
        if (success == False):
                return False, None

        if url is None or (url == ''):
            Gust_Log.System_Log(500,"Invalid Url provided", None, None)
            return False, None

        #Pull download
        response = requests.get(url, stream = True, allow_redirects=True)

        if (response.status_code != 200):
            Gust_Log.System_Log(500,"[ " + str(response.status_code) + " ] Error occured when downloading file", None, None)
            return False, None

        filename = File_Download.Find_Filename(response.headers)
        File_Download.DOWNLOADING_STATUS.update({url:{"file_size":int(response.headers['Content-Length']),"download_ammmount":0}})
       
            
        with open(Server_Global.DOWNLOAD_LOC+filename, "wb") as file:
            for chunk in response.iter_content(chunk_size=1024):
        
                # writing one chunk at a time to file
                if chunk:
                    file.write(chunk)
                    File_Download.DOWNLOADING_STATUS[url].update({"download_ammmount":File_Download.DOWNLOADING_STATUS[url]["download_ammmount"] + 1024})
                    

        Gust_Log.System_Log(200,"Successfully Downloaded: "+filename, None, None)

        if (File_Download.DOWNLOADING_STATUS[url]["download_ammmount"] >= File_Download.DOWNLOADING_STATUS[url]["file_size"]):
            File_Download.DOWNLOADING_STATUS.pop(url)

        return True, filename
    
    def Update_Download_Log(Name,Filename,Hash_File):

        success, yaml_file = Yaml_Editor.Yaml_Read(Server_Global.DOWNLOAD_LOG_LOC)
        if (success == False):
            return False
        
        if yaml_file is None:
            yaml_file = {}

        if Name not in yaml_file:
            yaml_file.update({Name:{}})

        if (Hash_File == True):
            yaml_file[Name].update({'hash_file': Filename, 'last updated': datetime.now().strftime("%a %d %b %Y - %H:%M")})
        else :
            yaml_file[Name].update({'file': Filename})

        Yaml_Editor.Yaml_Write(Server_Global.DOWNLOAD_LOG_LOC, yaml_file)
     
        return True