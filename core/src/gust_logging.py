import logging


#PROD / LIVE : Set to INFO
logging.basicConfig(
    level=logging.INFO,
    format="{asctime} {levelname:<8} {message}",
    style='{',
    filename='gust/core/data/logs/test.log',
    filemode='a'
)

class Gust_Log:

    def Format_Log_Message(Message, Connection):
        
        if Connection is None:
            connection_details = "UNCONNECTED"
        elif (Connection._closed == True):
            connection_details = "DISCONNECTED"
        else: 
            connection_details = str(Connection.getpeername())


        formated_mesage =  "[ " + connection_details +  " ] : " + Message
       
        return formated_mesage

    def Authentication_Log(Code, Message, Connection):
        formated_mesage = Gust_Log.Format_Log_Message(Message, Connection)

        match Code:
            case 200:   #Successfull authentication
                logging.info(formated_mesage)

            case 401:    #Failed authentication
                logging.warning(formated_mesage)

            case 403:    #Reject Authentication Attempts
                logging.critical(formated_mesage)

            case 404:    #Integrity check failure
                logging.critical(formated_mesage)

            case _:
                logging.error(formated_mesage)

    def File_Log(Code, Message, Connection):
        formated_mesage = Gust_Log.Format_Log_Message(Message, Connection)

        match Code:
            case 404:   #file not found
                logging.error(formated_mesage)

            case _:
                logging.error(formated_mesage)

    def System_Log(Code, Message, Connection):
        formated_mesage = Gust_Log.Format_Log_Message(Message, Connection)

        match Code:
            case 200:   #Successfull system process
                logging.info(formated_mesage)

            case 500:   #System Error
                logging.error(formated_mesage)

            case _:
                logging.error(formated_mesage)




      

