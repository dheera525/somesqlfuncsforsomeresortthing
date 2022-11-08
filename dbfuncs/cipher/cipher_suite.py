def getEncryptionKey(username):
    from cryptography.fernet import Fernet
    from dbfuncs.sqlfunc import getData,insertData,loadColumn
    
    tokensUsernames = loadColumn("encryptiontokens","username")

    if (not username in tokensUsernames):
        key = str(Fernet.generate_key(),'utf-8')
        print("Performing first-time user encryption")
        insertData("encryptiontokens",(username,key))

    token = getData("encryptiontokens",("username",username),'token')[0]

    try:
        return Fernet(token)
    except Exception as e:
        print("Error while reading encryption key.\n",e)
        return (None)