import mysql.connector
from .formats import formats

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="dpsbn"
)

if (not db.is_connected()):
    print("ERROR CONNECTING TO DATABASE")

cursor = db.cursor()


def readAll():
    try:
        # important to read all the cursor data before attaching more data to the cursor
        selectDB()
        return cursor.fetchall()
    except:
        pass


def selectDB(db="resortDB"):
    """
    DB - The DB to select - String
    """
    readAll()
    return cursor.execute("USE " + db)


def cleanConnection():
    """
    To close the database connection
    """
    db.close()


def loadColumn(table, column):
    """
    Table - A table in the selected database - String\n
    Column - A column in the table - String\n
    """
    readAll()
    query = "SELECT " + column + " FROM " + table
    cursor.execute(query)
    result = cursor.fetchall()
    result = list(map(lambda x: x[0], result))
    return result


def insertData(table, values):
    """
    Table - A table in the selected database - String\n
    Values - Values for inserting into table. All column values must be provided - Tuple( String, Int, Bool..)\n
    """
    readAll()
    syntax = None
    try:
        syntax = getFormat(table).columns
    except Exception as e:
        print(e)
        return (False, "Invalid table")

    placeHolder = "(" + ("%s," * (len(values) - 1)) + "%s)"
    query = "INSERT INTO " + table + ' ' + syntax + ' VALUES ' + placeHolder
    cursor.execute(query, values)
    db.commit()
    print(cursor.rowcount, "records affected")


def getFormat(table):
    """
    Table - A table in the selected database - String\n
    """
    currdb = executeSQL("SELECT DATABASE() FROM DUAL").fetchone()[0]
    tables = None
    try:
        tables = formats[currdb].keys()
    except Exception as e:
        print(e or repr(e))
        raise Exception
    if not table in tables:
        return False
    return formats[currdb][table]


def deleteData(table, *operators):
    """ 
    Table - A table in the selected database - String\n
    Operators - Identifiers - Tuple( String, String ), Tuple( String, String )...\n
    """
    readAll()
    # Operators = ( (column, key), (column, key), ...)
    identifier = operators[0]
    keys = loadColumn(table, identifier[0])
    if not identifier[1] in keys:
        #print("key does not exist in this database.")
        return (False, "Key Non-Existent")
    query = "DELETE FROM " + table + " WHERE "
    for key in enumerate(operators):
        index, operator = key
        query = query + (" AND " if index != 0 else "") + \
            operator[0] + " = " + "\"{}\"".format(operator[1])
    cursor.execute(query)
    db.commit()
    print(cursor.rowcount, "records affected")


def executeSQL(query, commit=False):
    """
    Query - Your SQL query - String\n
    Commit - Whether to commit after executing the cursor - Boolean\n
    Returns a cursor\n
    """
    readAll()
    cursor.execute(query)
    if (commit):
        db.commit()
    return cursor


def updateData(table, toUpdateColumn, toUpdateValue, identifier):
    """
    Table - A table in the selected database - String\n
    toUpdateColumn - The column in which the update takes place - String\n
    toUpdateValue - The value to update to - String/Integer\n
    Identifier - Identifier to locate correct row (Column, Value) - Tuple( String, String )\n
    """
    readAll()
    # identifier = (identifier (0), identifierValue (1))
    query = "UPDATE " + table + " SET " + toUpdateColumn + " = %s"
    values = (toUpdateValue,)
    if identifier:
        keys = loadColumn(table, identifier[0])
        if not identifier[1] in keys:
            print(
                "identifier key does not exist in this database\nidentifier key provided:", identifier[1]
                )
            return
        query = query + " WHERE " + identifier[0] + " = %s"
        values = values + (identifier[1],)
    cursor.execute(query, values)
    db.commit()
    print(cursor.rowcount, "records affected")


def getData(table, identifier, columnToGet="*", fetchAll=False):
    """
    Table - A table in the selected database - String\n
    Identifier - Identifier to locate correct row(s) in the form of (Column, Value) - Tuple( String, String )\n
    columnToGet - The column to get entries from - String\n
    fetchAll - Whether to fetch all entries in the form of a list (only works if you're fetching one column only) - Boolean\n

    """
    readAll()
    query = "SELECT " + columnToGet + " FROM " + table
    if identifier:
        query = query + " WHERE " + \
            identifier[0] + " = " + "'{}'".format(identifier[1])
    cursor.execute(query)
    result = cursor.fetchall() if fetchAll else cursor.fetchone()
    '''if type(result) == list and fetchAll: # Nope! Not needed since we're dealing with tables with multiple columns
        result = tuple( [x[0] for x in result] )'''
    return result
