from os import remove

from server.src.file_downloader import File_Download
from core.src import Yaml_Editor, Data_Link, Integrity_Check




class Gust_Sources:
    
    #####################
    #Globals

    success, yaml_file = Yaml_Editor.Yaml_Read(Data_Link.server_config)
    if (success == False):
        yaml_file = {}
    CONFIG_FILE = yaml_file

    SOURCE_LOC = CONFIG_FILE["server_sources_loc"]
    DOWNLOAD_LOC = CONFIG_FILE["download_loc"]

    #####################

    def List_Sources():
        sources = Yaml_Editor.List_Headers(Gust_Sources.SOURCE_LOC)
        return sources
    
    def Break_Source(Selected_Source):
        breakdown = Yaml_Editor.Breakdown_Dictionary(Selected_Source, Gust_Sources.SOURCE_LOC)
        return breakdown

    def Add_Source(Name,URL,Hash_URL,Hash_Type):
        
        success, yaml_file = Yaml_Editor.Yaml_Read(Gust_Sources.SOURCE_LOC)
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
                print(Name+" Already exists, would you like to overide this save?")
                overide = input("[1 = yes, 0 = no] ")
                if (overide != "1"):
                    print("Cannot not add already existing source")
                    return None
                
                print("Updating : "+yaml_file[source]['file']+" to : "+URL)
                print("Updating : "+yaml_file[source]['hash_file']+" to : "+Hash_URL)
                print("Updating : "+yaml_file[source]['hash_type']+" to : "+Hash_Type)
        
            source_list = Gust_Sources.Write_Sources(new_source)
            return source_list

    def Update_Source(Name,URL,Hash_URL,Hash_Type):
        
        success, yaml_file = Yaml_Editor.Yaml_Read(Gust_Sources.SOURCE_LOC)
        if (success == False):
            return None

        Updated_source = {
            Name:
                {'file': URL,
                'hash_file': Hash_URL,
                'hash_type': Hash_Type,
                }
        }

        for source in yaml_file:
            if (source == Name):
                print(source+" Already Exists:")
                print("Updating : "+yaml_file[source]['file']+" to : "+URL)
                print("Updating : "+yaml_file[source]['hash_file']+" to : "+Hash_URL)
                print("Updating : "+yaml_file[source]['hash_type']+" to : "+Hash_Type)


        source_list = Gust_Sources.Write_Sources(Updated_source)
        return source_list
    
    def Write_Sources(New_Source):
        
        success, yaml_file = Yaml_Editor.Yaml_Read(Gust_Sources.SOURCE_LOC)
        if (success == False):
            return None

        yaml_file.update(New_Source)

        Yaml_Editor.Yaml_Write(Gust_Sources.SOURCE_LOC, yaml_file)
        
        return yaml_file

    def Download_Sources():

        source_list = Gust_Sources.List_Sources()

        for source in source_list:
            urls = Gust_Sources.Break_Source(source)

            success, hash_filename = File_Download.Download_File(urls["hash_file"])
            if (success == False):
                break

            File_Download.Update_Download_Log(source, hash_filename, True)

            success, source_filename = File_Download.Download_File(urls["file"])
            if (success == False):
                break

            File_Download.Update_Download_Log(source, source_filename, False)

            
            matching_hashes = Integrity_Check.Hash_Check(Gust_Sources.DOWNLOAD_LOC+source_filename,Gust_Sources.DOWNLOAD_LOC+hash_filename,urls["hash_type"])

            if (matching_hashes == False):
                remove(Gust_Sources.DOWNLOAD_LOC+source_filename)
                remove(Gust_Sources.DOWNLOAD_LOC+hash_filename)

        return 





