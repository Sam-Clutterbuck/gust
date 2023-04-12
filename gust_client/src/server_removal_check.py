from gust_core.src import Integrity_Check, Gust_Log
 
if Integrity_Check.Dir_Check("server"):
    Gust_Log.System_Log(500, "Attempted to run client whilst server functionality exists", None, "CLIENT")
    print("Attempted to run client whilst server functionality exists")
    quit()