# Automatically creates all necessary SQL databases and certain data required for the app.

from .formats import formats
from . import sqlfunc
from os import name as osname

def fixData():
    for db_ in formats:
        # Checking if database exists.
        sqlfunc.executeSQL("CREATE DATABASE IF NOT EXISTS {}".format(db_))

        # Checking each db for tables.
        sqlfunc.selectDB(db_)
        requiredTables = []
        for table in formats[db_]:
            requiredTables.append((table,))
        dbtables = sqlfunc.executeSQL("SHOW TABLES").fetchall()
        missingTables = list(filter( lambda x: (x[0].lower(),) not in dbtables, requiredTables ))

    # fixing missing tables, if any.
        if missingTables:
            for table in missingTables:
                query = "CREATE TABLE " + table[0] + "(" + formats[db_][table[0]].syntax + ")"
                try:
                    sqlfunc.executeSQL(query,commit=True)
                    print("Fixed tables:\n",table)
                except Exception as e:
                    print(e)
                    pass