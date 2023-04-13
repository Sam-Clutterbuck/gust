import yaml

from gust_core.src.gust_logging import Gust_Log
from gust_core.src.integrity_checks import Integrity_Check

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
                Gust_Log.File_Log(500,error, None, None)
                return False

    def Yaml_Dump(Yaml_Content):
        dump = yaml.safe_dump(Yaml_Content)
        return dump
    
    def Yaml_Load(Non_Yaml_Content):
        yaml_content = yaml.safe_load(Non_Yaml_Content)
        return yaml_content

    def List_Headers(File):

        success, yaml_file = Yaml_Editor.Yaml_Read(File)
        if (success == False):
            return None

        avaliable_sources=[]

        for source in yaml_file:
            avaliable_sources.append(source)
        
        return avaliable_sources
        
        

    def Breakdown_Dictionary(Selected_Header, File):

        success, yaml_file = Yaml_Editor.Yaml_Read(File)
        if (success == False):
            return None
        
        for header in yaml_file:
            if (header == Selected_Header):
                return yaml_file[header]
        
        return None

    def Format(Yaml_File, Newline):
        
        Yaml_Editor.Formating_Loop(Yaml_File, Newline, 0)
        return
    
    def Formating_Loop(Yaml_File, Newline, Indent):
    
        if (Newline == True):
            endpoint = ':\n'
        else:
            endpoint = ': '

        try:

            if (type(Yaml_File) == str):

                Yaml_Editor.Indent(Indent, Newline)
                print(Yaml_File)
                return
            
            elif (type(Yaml_File) == dict):

                for key in Yaml_File:
                    Yaml_Editor.Indent(Indent, Newline)
                    if (type(Yaml_File[key]) == str):
                        print(f"{key}: {Yaml_File[key]}")
                    else:    
                        print(key, end=endpoint)
                        Yaml_Editor.Formating_Loop(Yaml_File[key], Newline, Indent+1)
        
        except:
            return
        
    def Indent(Indent_Ammount, Newline):

        #smaller indents for multiline readability
        if (Newline == True):
            print(('  ' * Indent_Ammount), end='')
        else:
            print(('\t' * Indent_Ammount), end='')

