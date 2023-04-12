import server.src.client_removal_check 

from os import remove
from threading import Thread

from server.src.server_config_link import Server_Global
from server.src.file_downloader import File_Download
from core.src import Yaml_Editor, Integrity_Check




class Gust_Sources:
    

    def List_Sources():
        sources = Yaml_Editor.List_Headers(Server_Global.SOURCE_LOC)
        return sources
    
    def Break_Source(Selected_Source):
        breakdown = Yaml_Editor.Breakdown_Dictionary(Selected_Source, Server_Global.SOURCE_LOC)
        return breakdown

    def Add_Source(Name,URL,Hash_URL,Hash_Type):
        
        success, yaml_file = Yaml_Editor.Yaml_Read(Server_Global.SOURCE_LOC)
        if (success == False):
            return None

        new_source = {
            Name:
                {'file': URL,
                'hash_file': Hash_URL,
                'hash_type': Hash_Type,
                }
        }

        for source in yaml_file:
            if (source == Name):
                return None
        
            source_list = Gust_Sources.Write_Sources(new_source)
            return source_list

    def Update_Source(Name,URL,Hash_URL,Hash_Type):
        
        success, yaml_file = Yaml_Editor.Yaml_Read(Server_Global.SOURCE_LOC)
        if (success == False):
            return None

        Updated_source = {
            Name:
                {'file': URL,
                'hash_file': Hash_URL,
                'hash_type': Hash_Type,
                }
        }

        exists = False
        for source in yaml_file:
            if (source == Name):
                exists = True
                print("Updating : "+yaml_file[source]['file']+" to : "+URL)
                print("Updating : "+yaml_file[source]['hash_file']+" to : "+Hash_URL)
                print("Updating : "+yaml_file[source]['hash_type']+" to : "+Hash_Type)

        if (exists == False):
            return None

        source_list = Gust_Sources.Write_Sources(Updated_source)
        return source_list
    
    def Delete_Source(Source):

        source_list = Gust_Sources.List_Sources()

        if Source not in source_list:
            return None

        #Delete Source from file
        success, yaml_file = Yaml_Editor.Yaml_Read(Server_Global.SOURCE_LOC)
        if (success == False):
            return None

        yaml_file.pop(Source)

        Yaml_Editor.Yaml_Write(Server_Global.SOURCE_LOC, yaml_file)


        #Delete Source from downloads
        success, yaml_file = Yaml_Editor.Yaml_Read(Server_Global.DOWNLOAD_LOG_LOC)
        if (success == False):
            return None
        
        exists = False
        for sources in yaml_file:
            if (Source == sources):
                exists = True
                if Integrity_Check.File_Check(Server_Global.DOWNLOAD_LOC+yaml_file[Source]['file']):
                    remove(Server_Global.DOWNLOAD_LOC+yaml_file[Source]['file'])
                if Integrity_Check.File_Check(Server_Global.DOWNLOAD_LOC+yaml_file[Source]['hash_file']):
                    remove(Server_Global.DOWNLOAD_LOC+yaml_file[Source]['hash_file'])

        if (exists == True):
            yaml_file.pop(Source)

        Yaml_Editor.Yaml_Write(Server_Global.DOWNLOAD_LOG_LOC, yaml_file)
        
        return 

    def Write_Sources(New_Source):
        
        success, yaml_file = Yaml_Editor.Yaml_Read(Server_Global.SOURCE_LOC)
        if (success == False):
            return None

        yaml_file.update(New_Source)

        Yaml_Editor.Yaml_Write(Server_Global.SOURCE_LOC, yaml_file)
        
        return yaml_file

    def Download_Sources():

        source_list = Gust_Sources.List_Sources()

        for source in source_list:
            Gust_Sources.Download_Source(source)
            

        return 

    def Download_Source(Source):

        source_list = Gust_Sources.List_Sources()

        if Source not in source_list:
            return

        new_thread = Thread(target=Gust_Sources.Download_Source_Threading, args=(Source, ))
        new_thread.start()
        return

    def Download_Source_Threading(Source):

        urls = Gust_Sources.Break_Source(Source)
            
        success, hash_filename = File_Download.Download_File(urls["hash_file"])
        if (success == False):
            return

        File_Download.Update_Download_Log(Source, hash_filename, True)

        success, source_filename = File_Download.Download_File(urls["file"])
        if (success == False):
            return

        File_Download.Update_Download_Log(Source, source_filename, False)

        
        matching_hashes = Integrity_Check.Hash_Check(Server_Global.DOWNLOAD_LOC+source_filename,Server_Global.DOWNLOAD_LOC+hash_filename,urls["hash_type"])

        if (matching_hashes == False):
            remove(Server_Global.DOWNLOAD_LOC+source_filename)
            remove(Server_Global.DOWNLOAD_LOC+hash_filename)

        return




