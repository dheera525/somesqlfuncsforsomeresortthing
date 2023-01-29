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
        # important to read all the cursor data before attaching more data to the cursor because when you cursor.execute without cursor.fetch-ing all the data, the module might crash.
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


def loadColumn(table, column): # Gets all rows from a column
    """
    Table - A table in the selected database - String\n
    Column - A column in the table - String\n
    """
    readAll()
    query = "SELECT " + column + " FROM " + table
    cursor.execute(query)
    result = cursor.fetchall()
    result = list(map(lambda x: x[0], result)) # Converts [ (a,b), (x,y), (m,n)] to [a,x,m]
    return result


def insertData(table, values): # Inserts a tuple of values into a table. 
    # Example: insertData("sometable", (1,"test",0.9))
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


def getFormat(table): # Gets the format of a table. (Table, Syntax & Columns)
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


def deleteData(table, *operators): # Deletes a record based on some conditions (operators).
    # Example: deleteData("testTable", ("number", 1)) will delete all values from testTable where the value of column "number" is 1.
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


def executeSQL(query, commit=False): # cursor.execute basically. if commit=true then it will db.commit() after executing the query.
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


def updateData(table, toUpdateColumn, toUpdateValue, identifier): # Updates a certain column with a certain value where identifier matches.
    # Example: updateData("TestTable", "Number", 1, ("Username", "hunter2")) will change the value of the column called "number" to 2 where the "username" column is "hunter2"
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


def getData(table, identifier=None, columnToGet="*", fetchAll=False): # Gets all the columns from columnsToGet with the specified identifier.
    # Example: getData("TestTable", ("number", 1), "name, password", True) will get all rows from the name and password column where the column "number" is 1. It will also return everything in a list because of fetchAll.
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
    return result
