import gust_server.src.client_removal_check 

from getpass import getpass

from gust_server.src.server_config_link import Server_Global
from gust_server.src.account_control import Account_Control
from gust_server.src.login_systems import Login_Auth
from gust_server.src.gust_sources import Gust_Sources
from gust_server.src.gust_server_source import Gust_Server
from gust_core.src.yaml_editor import Yaml_Editor



class Gust_Server_Cli:

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

  success, CLI_COMMANDS = Yaml_Editor.Yaml_Read(Server_Global.SERVER_CLI_COMMANDS)
  if (success == False):
    CLI_COMMANDS = {}
    
  AUTHENTICATED = False
  CURRENT_USER = None
  LOGIN_ATTEMPTS = 0

##################################################################
# Core Cli Code

  def Confirm_Authenticated(Func):
    def Confirm(*Args, **Kwargs):
      if Gust_Server_Cli.AUTHENTICATED and Gust_Server_Cli.CURRENT_USER is not None:
        return Func(*Args, **Kwargs)
      print("You need to be signed in to do that")
      return
    return Confirm
        
  def Sign_In():
    while not Gust_Server_Cli.AUTHENTICATED:
      username = input("Enter your username: ")
      password = getpass("Enter your password: ")

      success, return_username = Login_Auth.Login_Check(Account_Control.Format_Username(username, password))
      if success:
        Gust_Server_Cli.AUTHENTICATED = True
        Gust_Server_Cli.CURRENT_USER = [return_username, Account_Control.Format_Username(username, password)]
        print(f"Signed in as {return_username}")
        return
      else:
        Gust_Server_Cli.LOGIN_ATTEMPTS += 1
        if (Gust_Server_Cli.LOGIN_ATTEMPTS >= Server_Global.LOGIN_ATTEMPT_LIMIT):
          print("Too many failed login attempts")
          quit()

        print("username or password is incorrect")
    
    print(f"Already signed in as {Gust_Server_Cli.CURRENT_USER[0]}")

  def Print_Header():
      print(Gust_Server_Cli.BANNER)
      for info in Gust_Server_Cli.CLI_COMMANDS['info']:
        print(f"{info}: {Gust_Server_Cli.CLI_COMMANDS['info'][info]}")
      print("")
      return
  
  def Print_Help():
      
      for command in Gust_Server_Cli.CLI_COMMANDS['commands']:
        print(f"{command}")
        print(f"\t\tAlternate shorthand: [ALT] - {Gust_Server_Cli.CLI_COMMANDS['commands'][command]['alt']}")
        print(f"\t\tArguments - {len(Gust_Server_Cli.CLI_COMMANDS['commands'][command]['args'])}")

        for arg in Gust_Server_Cli.CLI_COMMANDS['commands'][command]['args']:
          print(f"\t\t\t\t\t{arg}: {Gust_Server_Cli.CLI_COMMANDS['commands'][command]['args'][arg]}")
        


      return
  
  def Cli_Startup():
    Gust_Server_Cli.Print_Header()
    print("To use most features you will need to sign in\n[use 'login' or 'l' to login]")
    Gust_Server_Cli.Enter_Command()


  def Enter_Command():
    while True:

      selection = input("\nEnter a command to run: ").lower()

      if not Gust_Server_Cli.Command_Validate(selection):
        print(f"'{selection}' Is an invalid command \n[use 'help' or 'h' to list options]")


  def Command_Validate(Input_Command):
      
    #make sure command is valid
    for command in Gust_Server_Cli.CLI_COMMANDS['commands']:
      if (Input_Command == command):
          Gust_Server_Cli.CLI_COMMANDS['commands'][command]['func']()
          return True
      
      #check for alternate shorthands
      for alternate in Gust_Server_Cli.CLI_COMMANDS['commands'][command]['alt']:
          if (Input_Command == alternate):
            Gust_Server_Cli.CLI_COMMANDS['commands'][command]['func']()
            return True
    
    return False
  
  def Input_Cycle(Command):

    inputs=[]
    for arg in Gust_Server_Cli.CLI_COMMANDS['commands'][Command]['args']:
      inputs.append(input(f"Enter {Gust_Server_Cli.CLI_COMMANDS['commands'][Command]['args'][arg]} : "))
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

    success, source_list = Yaml_Editor.Yaml_Read(Server_Global.SOURCE_LOC)
    if (success == False):
      print("Couldn't Locate Source List")
      return

    Yaml_Editor.Format(source_list, False)
    return
  
  def Print_Downloads():
    print("Printing Downloads List")
    success, download_list = Yaml_Editor.Yaml_Read(Server_Global.DOWNLOAD_LOG_LOC)
    if (success == False):
      print("Couldn't Locate Source List")
      return

    Yaml_Editor.Format(download_list, False)
    return


###########################
# Authenticated Commands

  @Confirm_Authenticated
  def Add_Source():
    print("Adding New Source")
    inputs = Gust_Server_Cli.Input_Cycle("add_source")
    if inputs is None:
      return
    Gust_Sources.Add_Source(inputs[0],inputs[1],inputs[2],inputs[3])
    Gust_Server_Cli.Print_Sources()

  @Confirm_Authenticated
  def Update_Source():
    print("Updating Source")
    inputs = Gust_Server_Cli.Input_Cycle("update_source")
    if inputs is None:
      return
    Gust_Sources.Update_Source(inputs[0],inputs[1],inputs[2],inputs[3])
    Gust_Server_Cli.Print_Sources()

  @Confirm_Authenticated
  def Delete_Source():
    print("Deleting Source")

    valid_source = False
    while not valid_source:

      inputs = Gust_Server_Cli.Input_Cycle("delete_source")
      if inputs is None:
        return

      source_list = Gust_Sources.List_Sources()

      if inputs[0] in source_list:
        valid_source = True
        break

      print("enter a valid source")

    if valid_source:
      Gust_Sources.Delete_Source(inputs[0])
      Gust_Server_Cli.Print_Sources()

  @Confirm_Authenticated
  def Download_All():
    print("Downloading All Sources")
    Gust_Sources.Download_Sources()
    Gust_Server_Cli.Print_Downloads()
    print("If new downloads don't show please wait and check again with 'print_downloads'")

  @Confirm_Authenticated
  def Download_Source():
    print("Downloading Selected Source")
    inputs = Gust_Server_Cli.Input_Cycle("source_download")
    if inputs is None:
      return
    Gust_Sources.Download_Source(inputs[0])
    Gust_Server_Cli.Print_Downloads()
    print("If new downloads don't show please wait and check again with 'print_downloads'")

  @Confirm_Authenticated
  def New_User():
    print("Adding New User")
    inputs = Gust_Server_Cli.Input_Cycle("new_user")
    if inputs is None:
      return
    Account_Control.Add_User(Gust_Server_Cli.CURRENT_USER[1],inputs[0],inputs[1])

  @Confirm_Authenticated
  def Delete_User():
    print("Deleting User")
    inputs = Gust_Server_Cli.Input_Cycle("del_user")
    if inputs is None:
      return
    Account_Control.Delete_User(Gust_Server_Cli.CURRENT_USER[1],inputs[0])

  @Confirm_Authenticated
  def Password_Reset():
    print("Reseting User Password")
    inputs = Gust_Server_Cli.Input_Cycle("passwd_reset")
    if inputs is None:
      return
    Account_Control.Password_Reset(Gust_Server_Cli.CURRENT_USER[1],inputs[0],inputs[1])

  @Confirm_Authenticated
  def Start_Server():
    print("Starting Server")
    Gust_Server.Start_Server()
    

  CLI_COMMANDS['commands']['login'].update({'func':Sign_In})
  CLI_COMMANDS['commands']['quit'].update({'func':quit})
  CLI_COMMANDS['commands']['help'].update({'func':Print_Help})
  CLI_COMMANDS['commands']['print_sources'].update({'func':Print_Sources})
  CLI_COMMANDS['commands']['add_source'].update({'func':Add_Source})
  CLI_COMMANDS['commands']['update_source'].update({'func':Update_Source})
  CLI_COMMANDS['commands']['delete_source'].update({'func':Delete_Source})
  CLI_COMMANDS['commands']['print_downloads'].update({'func':Print_Downloads})
  CLI_COMMANDS['commands']['download_all'].update({'func':Download_All})
  CLI_COMMANDS['commands']['source_download'].update({'func':Download_Source})
  CLI_COMMANDS['commands']['new_user'].update({'func':New_User})
  CLI_COMMANDS['commands']['del_user'].update({'func':Delete_User})
  CLI_COMMANDS['commands']['passwd_reset'].update({'func':Password_Reset})
  CLI_COMMANDS['commands']['start_server'].update({'func':Start_Server})