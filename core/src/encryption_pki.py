import rsa
from Crypto.Cipher import AES

from core.src.integrity_checks import Integrity_Check

class Encrypt_Pki:

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
        AES_cipher = Encrypt_Pki.Get_Symmetric_Cipher(AES_Key)

        encrypted_public_key = AES_cipher.encrypt(raw_public_key)
        return encrypted_public_key

    def Decrypt_Public_Key(Public_Key, AES_Key, Connection):
        AES_cipher = Encrypt_Pki.Get_Symmetric_Cipher(AES_Key)

        decrypted_raw_public_key = AES_cipher.decrypt(Public_Key).decode()
        decrypted_public_key = rsa.PublicKey.load_pkcs1(decrypted_raw_public_key)
        Encrypt_Pki.Link_Public_Key(decrypted_public_key, Connection)

        return decrypted_public_key

