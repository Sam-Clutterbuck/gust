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


'''


    PRIVATE_KEY = ""
    PUBLIC_KEY = ""
    LINKED_PUBLIC_KEYS = {}

    def Link_Public_Key(New_Key, Connection):

        Encrypt_Pki.LINKED_PUBLIC_KEYS.update({Connection: New_Key})

        return
    
    def Remove_Public_Key(Key, Connection):

        Encrypt_Pki.LINKED_PUBLIC_KEYS[Connection].pop()

        return

    def Create_Keys():
        Encrypt_Pki.PUBLIC_KEY, Encrypt_Pki.PRIVATE_KEY = rsa.newkeys(2048)
    
    def Get_Public_Key(Connection):

        public_key = Encrypt_Pki.LINKED_PUBLIC_KEYS[Connection]
        
        return public_key
    
    def Encrypt_Message(Message, Connection):
        #requires unencoded input
        public_key = Encrypt_Pki.Get_Public_Key(Connection)

        encrypted_message = rsa.encrypt(Message.encode(), public_key)
        return encrypted_message
    
    
    def Decrypt_Message(Message):
        #requires encoded input
        decrypted_message = rsa.decrypt(Message, Encrypt_Pki.PRIVATE_KEY)
        return decrypted_message.decode()
    
    def Get_Symmetric_Cipher(Key):

        #Hash the key and take first 32 bytes ( max for AES)
        hashed_key = Integrity_Check.Sha256_Encode(Key).encode()[:32]

        cipher = AES.new(hashed_key, AES.MODE_EAX, hashed_key)
        return cipher
    
    def Prep_Public_Key(AES_Key):

        raw_public_key = Encrypt_Pki.PUBLIC_KEY.save_pkcs1("PEM")
        encrypted_public_key = Encrypt_Pki.AES_Encrypt(AES_Key, raw_public_key)

        return encrypted_public_key

    def Decrypt_Public_Key(Public_Key, AES_Key, Connection):

        success, decrypted_raw_public_key = Encrypt_Pki.AES_Decrypt(AES_Key, Public_Key)
        decrypted_public_key = rsa.PublicKey.load_pkcs1(decrypted_raw_public_key)
        Encrypt_Pki.Link_Public_Key(decrypted_public_key, Connection)

        return decrypted_public_key
    
    def AES_Encrypt(AES_Key, Message):
        AES_cipher = Encrypt_Pki.Get_Symmetric_Cipher(AES_Key)
        encrypted_message = AES_cipher.encrypt(Message)
        return encrypted_message
    
    def AES_Decrypt(AES_Key, Message):
        AES_cipher = Encrypt_Pki.Get_Symmetric_Cipher(AES_Key)

        try:
            decrypted_message = AES_cipher.decrypt(Message).decode()
        except:
            return False, "failed"

            
        #decrypted_message = AES_cipher.decrypt(Message).decode()
        return True, decrypted_message
'''