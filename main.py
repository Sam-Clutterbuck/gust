import tests

selection = input("1 = server, 0 = client")

if (selection == "1"):
    tests.Launch_Server.Start()

if (selection == "0"):
    tests.Launch_Client.Start()



#from web.src import TEST

#TEST.Start_Web_App()