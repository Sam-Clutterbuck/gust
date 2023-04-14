import gust_client.src.server_removal_check
from gust_core.src import Yaml_Editor

class Client_Global:

    success, config_file = Yaml_Editor.Yaml_Read("gust_client/data/client_config.yaml")
    if (success == False):
        config_file = {}


    target = open('gust_client/data/target_ip','r')
    
    TARGET_IP = target.readline()  
    TARGET_PORT = config_file["target port"]
    SOURCE_LOC = config_file["client_sources_loc"]
    DOWNLOAD_LOC = config_file["download_loc"]
    CLIENT_CLI_COMMANDS = config_file["cli commands"]
