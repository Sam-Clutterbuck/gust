import yaml

from core.src.gust_logging import Gust_Log
from core.src.integrity_checks import Integrity_Check

class Yaml_Editor:

    def Yaml_Read(File):

        success = Integrity_Check.File_Check(File) 
        if (success == False):
                return False, None

        with open(File) as file:
            try:
                yaml_file = yaml.safe_load(file)
            except yaml.YAMLError as error:
                Gust_Log.System_Log(500,error, None, None)
                return False, None
        return True, yaml_file
    
    def Yaml_Write(File, Yaml_Content):

        with open(File, "w") as writer:
            try:
                yaml.dump(Yaml_Content, writer)
                return True
            except yaml.YAMLError as error:
                Gust_Log.System_Log(500,error, None, None)
                return False

    def Yaml_Dump(Yaml_Content):
        dump = yaml.safe_dump(Yaml_Content)
        return dump

    def List_Headers(File):

        success, yaml_file = Yaml_Editor.Yaml_Read(File)
        if (success == False):
            return None

        avaliable_sources=[]

        for source in yaml_file:
            avaliable_sources.append(source)
            return avaliable_sources
        
        return None
        

    def Breakdown_Dictionary(Selected_Header, File):

        success, yaml_file = Yaml_Editor.Yaml_Read(File)
        if (success == False):
            return None
        
        for header in yaml_file:
            if (header == Selected_Header):
                return yaml_file[header]
        
        return None
