def decrypt(username,password):
    from dbfuncs.cipher.cipher_suite import getEncryptionKey
    from dbfuncs.sqlfunc import loadColumn,getData

    if (not username in loadColumn("encryptiontokens","username")):
         return (False,"Invalid Username")
         
    try:
        cipher_suite = getEncryptionKey(username)
    except Exception as e:
        return (False, "Error: Invalid encryption key\n",e)
        
    allMembers= loadColumn("members","username")

    if (not username in allMembers):
        return (False, "Error: Username not in password database")
    
    encrypted_password = getData("members", ("username", username), "password")[0]
    
    decoded_text = cipher_suite.decrypt(bytes(encrypted_password,'utf-8'))

    if (str(decoded_text,'utf-8') != password):
        return (False, "Incorrect Password")
    
    return (True, "Access Granted")
    