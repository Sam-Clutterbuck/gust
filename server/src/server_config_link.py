import server.src.client_removal_check 
from core.src import Yaml_Editor

class Server_Global:

    success, config_file = Yaml_Editor.Yaml_Read("server/data/server_config.yaml")
    if (success == False):
        config_file = {}

    HOST_IP = config_file["ip"]
    HOST_PORT = config_file["port"]
    LOGIN_ATTEMPT_LIMIT = config_file["connection attempt limit"]
    MAX_CONCURRENT_USERS = config_file["max concurrent users"]
    DOWNLOAD_LOG_LOC= config_file["download_log_loc"]
    DOWNLOAD_LOC = config_file["download_loc"]
    SOURCE_LOC = config_file["server_sources_loc"]
    SERVER_CLI_HELP = config_file["server_cli_help"]
    SERVER_CLI_COMMANDS = config_file["server_cli_commands"]
    LOGINS = config_file["logins_loc"]
    

