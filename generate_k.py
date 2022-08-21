from cryptography.fernet import Fernet

#this script generate new cyphre key that encryps data in password_new.py
# set varible key to the variable k in passwor_manager.py if you want to change cyphre key

key = Fernet.generate_key()
print(key)
