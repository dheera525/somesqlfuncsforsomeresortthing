def encrypt(username,first,last,password):

    # Creates an account, encrypts its password into a private and public key, the binds the user to both keys and saves it in the database

    from .cipher_suite import getEncryptionKey
    from dbfuncs.sqlfunc import insertData,updateData,loadColumn

    vUsername = usernameValidator(username)
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
    
    AllMembers = loadColumn("members","username")
    
    if not username in AllMembers:
        insertData("members", (username, first, last, encoded_password)) # Making the actual account.
    else:
        updateData("members","password",encoded_password,("username",username)) # Or just updating the password if it exists

    return (True,'success')

def usernameValidator(username):
    return (True, "Done.") # No validation as of now