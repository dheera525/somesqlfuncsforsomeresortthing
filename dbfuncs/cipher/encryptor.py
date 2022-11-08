def encrypt(username,first,last,password):
    from .cipher_suite import getEncryptionKey
    from dbfuncs.sqlfunc import insertData,updateData,loadColumn

    vUsername = usernameValidator(username) # i havent initialized this, make the func urself
    if not vUsername[0]: return vUsername
    
    try:
        cipher_suite = getEncryptionKey(username)
    except Exception as e:
        print("Error while getting encryption key\n",e)
        return (False, "Error while getting encryption key")

    try:
        encoded_password = cipher_suite.encrypt(bytes(password,'utf-8'))
        encoded_password = str(encoded_password,'utf-8')
    except Exception as e:
        print("Error while encrypting password\n",e)
        return (False, "Error while encrypting password")
    
    # Uploading password to passwords.json (now in sql because why not)
    AllMembers = loadColumn("members","username")
    
    if not username in AllMembers:
        insertData("members", (username, first, last, encoded_password)) # Making the actual account.
    else:
        updateData("members","password",encoded_password,("username",username)) # Or just updating the password if it exists

    return (True,'success')

def usernameValidator(username):
    return (True, "yay success message ig") # however u want to handle usernames idk