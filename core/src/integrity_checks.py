import hashlib
from os.path import isfile, isdir

from core.src.gust_logging import Gust_Log

class Integrity_Check:

    def File_Check(File):

        if (isfile(File) == False):
            Gust_Log.File_Log(404,"unable to locate file "+File, None)
            return False
        return True
    
    def Dir_Check(Directory):

        if (isdir(Directory) == False):
            Gust_Log.File_Log(404,"unable to locate Directory "+Directory, None)
            return False
        return True

    def Read_File(File_Loc):

            exists = Integrity_Check.File_Check(File_Loc)
            if (exists == False):
                return False, None

            with open(File_Loc, 'rb') as File:
                try:
                    data = File.read()
                    return True, data
                except:
                    Gust_Log.System_Log(500,"Error occured reading from file", None)
                    return False, None
                
    def Hash_Check(Source_File, Hash_File, Hash_Type):
        
        success, source_data = Integrity_Check.Read_File(Source_File)
        success, hash_data = Integrity_Check.Read_File(Hash_File)

        if (source_data is None) or (hash_data is None):
            return False

        match Hash_Type.lower():
            case "md5":
                # deepcode ignore InsecureHash: <MD5 is not the most secure however is still a commercial standard hash check>
                hash_check = hashlib.md5()

            case "sha256":
                hash_check = hashlib.sha256()

            case _:
                hash_check = hashlib.md5()


        hash_check.update(source_data)
        source_hash = hash_check.hexdigest()

        if (source_hash == hash_data.decode()):
            print("Hash integrity check succeded : " + Source_File)
            Gust_Log.Authentication_Log(200,"Hash integrity check succeded : " + Source_File, None)
            return True
        else:
            print("Hash integrity check failed : " + Source_File)
            Gust_Log.Authentication_Log(404,"Hash integrity check failed : " + Source_File, None)
            return False
        
    def Sha256_Encode(Message):
        sha256 = hashlib.sha256()
        sha256.update(Message.encode())
        hashed_message = sha256.hexdigest()
        return hashed_message
