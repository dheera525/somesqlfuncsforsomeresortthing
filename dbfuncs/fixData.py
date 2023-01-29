# Automatically creates all necessary SQL databases and certain data required for the app.

from .formats import formats
from . import sqlfunc

def fixData():
    for db_ in formats: # For each database in formats..

        # Check if database exists. Create it if it does not exist
        sqlfunc.executeSQL("CREATE DATABASE IF NOT EXISTS {}".format(db_)) 

        sqlfunc.selectDB(db_) # Select the database
        requiredTables = [] # A list of the database we need according to formats.py

        for table in formats[db_]: # For each table in the database according to formats.py ...
            requiredTables.append((table,)) # Append the name of that table to requiredTables

        currentTables = sqlfunc.executeSQL("SHOW TABLES").fetchall() # Get all the current tables.
        missingTables = list(filter( lambda x: (x[0].lower(),) not in currentTables, requiredTables )) # Make a list of the tables that are in requiredTables but not currentTables. These tables have to be added.

    # fixing missing tables, if any.
        if missingTables: # If there are requiredTables that are not in currentTables, we need to add them.
            for table in missingTables: # For each table in missingTables...
                query = "CREATE TABLE " + table[0] + "(" + formats[db_][table[0]].syntax + ")" # Create the table using data from formats.py
                try:
                    sqlfunc.executeSQL(query,commit=True) # execute the table creation query and commit.
                    print("Fixed tables:\n",table)
                except Exception as e: # If it errors, print it.
                    print(e)
                    pass

    sqlfunc.selectDB() # Finally, select the appropriate database.