from gust_core.src.yaml_editor import Yaml_Editor

class Commands_Global:

    success, yaml_file = Yaml_Editor.Yaml_Read("gust_core/data/commands.yaml")
    if (success == False):
        yaml_file = {}
    COMMANDS = yaml_file