import gust_client.src.server_removal_check
from gust_core.src import Yaml_Editor

class Client_Global:

    success, config_file = Yaml_Editor.Yaml_Read("gust_client/data/client_config.yaml")
    if (success == False):
        config_file = {}

    TARGET_IP = config_file["target ip"]
    TARGET_PORT = config_file["target port"]
    SOURCE_LOC = config_file["client_sources_loc"]
    DOWNLOAD_LOC = config_file["download_loc"]