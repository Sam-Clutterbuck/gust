import rsa
from Crypto.Cipher import AES

from gust_core.src.integrity_checks import Integrity_Check

class AES_Encrypt:

    ############################################################
    # AES cipher

    def AES_Cipher(Key, Nonce):

        #Hash the key and take first 32 bytes ( max for AES)
        hashed_key = Integrity_Check.Sha256_Encode(Key)[:32].encode()
        hashed_nonce = Integrity_Check.Sha256_Encode(Nonce)[:32].encode()

        cipher = AES.new(hashed_key, AES.MODE_EAX, hashed_nonce)
        return cipher

    ############################################################
    # Login encrypted

    def Login_Encrypt(Login, Client_Connection, Message):
        aes_cipher = AES_Encrypt.AES_Cipher(Login, Client_Connection)    

        if (type(Message) != bytes):
            Message = Message.encode()

        encrypted_message = aes_cipher.encrypt(Message)
        return encrypted_message


    def Login_Decrypt(Login, Client_Connection, Message):
        aes_cipher = AES_Encrypt.AES_Cipher(Login, Client_Connection)    

        try:
            if (type(Message) != bytes):
                Message = Message.encode()

            encrypted_message = aes_cipher.decrypt(Message)
            return True, encrypted_message.decode()
        except:
            return False, None

    ############################################################
    # Session encrypted

    def Session_Encrypt(Session, Login, Message):
        aes_cipher = AES_Encrypt.AES_Cipher(Session, Login)    

        if (type(Message) != bytes):
            Message = Message.encode()

        encrypted_message = aes_cipher.encrypt(Message)
        return encrypted_message

    def Session_Decrypt(Session, Login, Message):
        aes_cipher = AES_Encrypt.AES_Cipher(Session, Login)    

        try:
            if (type(Message) != bytes):
                Message = Message.encode()

            encrypted_message = aes_cipher.decrypt(Message)
            return True, encrypted_message.decode()
        except:
            return False, None

