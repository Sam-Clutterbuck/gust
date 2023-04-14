from gust_client.src.client_config_link import Client_Global
from gust_client.src.gust_client_source import Gust_Client
from gust_core.src.yaml_editor import Yaml_Editor

class Gust_Client_Cli:

    ##################################################################
    # setup and staging


    BANNER = """
  ▄▄█▀▀▀██▄                   ██
▄██▀     ▀                   ▄██
██▀       ▀▀███  ▀███  ▄██▀████████
██           ██    ██  ██   ▀▀ ██
██▄    ▀████ ██    ██  ▀█████▄ ██
▀██▄     ██  ██    ██  █▄   ██ ██
  ▀▀███████  ▀████▀███▄██████▀ ▀████

▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀
 ▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀
  """

    success, CLI_COMMANDS = Yaml_Editor.Yaml_Read(Client_Global.CLIENT_CLI_COMMANDS)
    if (success == False):
        CLI_COMMANDS = {}
    
    AUTHENTICATED = False

##################################################################
# Core Cli Code

    def Confirm_Authenticated(Func):
        def Confirm(*Args, **Kwargs):
            if Gust_Client_Cli.AUTHENTICATED is True and Gust_Client.AUTHENTICATED_USER is not None:
                return Func(*Args, **Kwargs)
            print("You need to be signed in to do that\n[use 'connect' or 'c' to login]")
            return
        return Confirm

    def Print_Header():
        print(Gust_Client_Cli.BANNER)
        for info in Gust_Client_Cli.CLI_COMMANDS['info']:
            print(f"{info}: {Gust_Client_Cli.CLI_COMMANDS['info'][info]}")
        print("")
        return
    
    def Print_Help():
        
        for command in Gust_Client_Cli.CLI_COMMANDS['commands']:
            print(f"{command}")
            print(f"\t\tAlternate shorthand: [ALT] - {Gust_Client_Cli.CLI_COMMANDS['commands'][command]['alt']}")
            print(f"\t\tArguments - {len(Gust_Client_Cli.CLI_COMMANDS['commands'][command]['args'])}")

            for arg in Gust_Client_Cli.CLI_COMMANDS['commands'][command]['args']:
                print(f"\t\t\t\t\t{arg}: {Gust_Client_Cli.CLI_COMMANDS['commands'][command]['args'][arg]}")
            


        return
    
    def Cli_Startup():
        Gust_Client_Cli.Print_Header()
        print("To interact with server you will need to sign in\n[use 'connect' or 'c' to login]")
        Gust_Client_Cli.Enter_Command()


    def Enter_Command():
        while True:

            selection = input("\nEnter a command to run: ").lower()

            if not Gust_Client_Cli.Command_Validate(selection):
                print(f"'{selection}' Is an invalid command \n[use 'help' or 'l' to list options]")


    def Command_Validate(Input_Command):
        
        #make sure command is valid
        for command in Gust_Client_Cli.CLI_COMMANDS['commands']:
            if (Input_Command == command):
                Gust_Client_Cli.CLI_COMMANDS['commands'][command]['func']()
                return True
        
            #check for alternate shorthands
            for alternate in Gust_Client_Cli.CLI_COMMANDS['commands'][command]['alt']:
                if (Input_Command == alternate):
                    Gust_Client_Cli.CLI_COMMANDS['commands'][command]['func']()
                    return True
            
        return False
    
    def Input_Cycle(Command):

        inputs=[]
        for arg in Gust_Client_Cli.CLI_COMMANDS['commands'][Command]['args']:
            inputs.append(input(f"Enter {Gust_Client_Cli.CLI_COMMANDS['commands'][Command]['args'][arg]} : "))
            if (inputs[-1].upper() == "Q"):
                print("Quiting command")
                return None
        
        return inputs
    
    ##################################################################
    # Cli Command Functions


    ###########################
    # Unauthenticated Commands

    def Print_Sources():
        print("Printing Source List")

        success, source_list = Yaml_Editor.Yaml_Read(Client_Global.SOURCE_LOC)
        if (success == False):
            print("Couldn't Locate Source List")
            return

        Yaml_Editor.Format(source_list, False)
        return
    
    def Connect():
        print("Connecting to client")
        if not Gust_Client.Authenticate():
            Gust_Client_Cli.AUTHENTICATED = False
            return
        
        Gust_Client_Cli.AUTHENTICATED = True
        print(f"{Gust_Client.AUTHENTICATED_USER['username']} authenticated")

    def Quit_Cli():
        
        if Gust_Client.AUTHENTICATED_USER is not None:
            Gust_Client.Send_Quit_Notif()

        quit()


    ###########################
    # Authenticated Commands

    @Confirm_Authenticated
    def Update_Sources():
        print("Updating Client sources with latest server sources")
        if Gust_Client.Update_Sources():
            print("Updated source list")
            Gust_Client_Cli.Print_Sources()
        

    @Confirm_Authenticated
    def Transfer_All():
        print("Setting up Source Transfer")

        for source in Yaml_Editor.List_Headers(Client_Global.SOURCE_LOC):
            if not Gust_Client.Transfer_Source(source):
                print(f"Failed to transfer {source}")
            else:
                print(f"{source} transfered successfully")


    @Confirm_Authenticated
    def Transfer_Source():
        print("Setting up Source Transfer")
        inputs = Gust_Client_Cli.Input_Cycle("transfer_source")
        if inputs is None:
            return
        print(f"Requesting transfer of {inputs[0]} from server to client")
        if not Gust_Client.Transfer_Source(inputs[0]):
            print(f"Failed to transfer {inputs[0]}")
            return
        print(f"{inputs[0]} transfered successfully")

    CLI_COMMANDS['commands']['connect'].update({'func':Connect})
    CLI_COMMANDS['commands']['quit'].update({'func':Quit_Cli})
    CLI_COMMANDS['commands']['help'].update({'func':Print_Help})
    CLI_COMMANDS['commands']['print_sources'].update({'func':Print_Sources})
    CLI_COMMANDS['commands']['update_sources'].update({'func':Update_Sources})
    CLI_COMMANDS['commands']['transfer_all'].update({'func':Transfer_All})
    CLI_COMMANDS['commands']['transfer_source'].update({'func':Transfer_Source})
    