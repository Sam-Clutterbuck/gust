import re
import requests

from datetime import datetime

from core.src import  Yaml_Editor, Data_Link, Integrity_Check, Gust_Log


class File_Download:
   
   #####################
   #Globals

    success, yaml_file = Yaml_Editor.Yaml_Read(Data_Link.server_config)
    if (success == False):
        yaml_file = {}
    CONFIG_FILE = yaml_file

    DOWNLOAD_LOC = CONFIG_FILE["download_loc"]
    DOWNLOAD_LOG_LOC= CONFIG_FILE["download_log_loc"]

    DOWNLOADING_STATUS = {}

   #####################

    def Find_Filename(Header):
        #get filename from download header

        content = Header['Content-Disposition']
        filename_extended = re.findall("filename=\".*\"", content)
        filename = re.split("\"", filename_extended[0])

        return filename[1]
   
    def Download_File(url):
       
        success = Integrity_Check.Dir_Check(File_Download.DOWNLOAD_LOC) 
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
        print(response.headers['Content-Length'])
        File_Download.DOWNLOADING_STATUS.update({url:{"file_size":response.headers['Content-Length'],"download_ammmount":0}})
        print("DETS = "+File_Download.DOWNLOADING_STATUS[url])
            
        with open(File_Download.DOWNLOAD_LOC+filename, "wb") as file:
            for chunk in response.iter_content(chunk_size=1024):
        
                # writing one chunk at a time to file
                if chunk:
                    file.write(chunk)
                    File_Download.DOWNLOADING_STATUS[url]["download_ammmount"].update(File_Download.DOWNLOADING_STATUS[url]["download_ammmount"] + 1024)
                    print("LENGTH = "+File_Download.DOWNLOADING_STATUS)
                    #print(download_set)

        Gust_Log.System_Log(200,"Successfully Downloaded: "+filename, None, None)
        return True, filename
    
    def Update_Download_Log(Name,Filename,Hash_File):

        success, yaml_file = Yaml_Editor.Yaml_Read(File_Download.DOWNLOAD_LOG_LOC)
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

        Yaml_Editor.Yaml_Write(File_Download.DOWNLOAD_LOG_LOC, yaml_file)
     
        return True