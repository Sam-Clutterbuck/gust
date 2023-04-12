from core.src import Integrity_Check, Gust_Log
 
if Integrity_Check.Dir_Check("client"):
    Gust_Log.System_Log(500, "Attempted to run server whilst client functionality exists", None, "SERVER")
    print("Attempted to run server whilst client functionality exists")
    quit()