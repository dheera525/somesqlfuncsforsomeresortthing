import uuid
from . import sqlfunc as sf
import datetime as dt

#  MEMBER FUNCTIONS

def member_GetName(username): # Gets the first and last name of a member and returns a dictionary
    first_name, last_name = sf.getData("members", ("username", username), "firstName, lastName")
    return {"first_name": first_name, "last_name": last_name}

def member_Create(username, first, last, password):
    # This function creates an account.
    sf.insertData("members", (username, first, last, password))

def member_Delete(username):

    # This function takes as many tables (strings) as needed and uses the deleteData function from 'sqlfunc' module and deletes all records of the user.
    dlt = lambda *tables: [ sf.deleteData(table, ("username", username)) for table in tables]

    # Deleting the user from the members and booking tables.
    dlt("members", "bookings")

def member_Modify(username, first=None, last=None, password=None, new_username=None):
    # Modify an account
    """
    Change any of the default-named parameters:\n
    first -> firstName\n
    last -> lastName\n
    password -> password for the account\n
    new_username -> username to change the account to\n
    """
    
    if password: # Checks if the password is being changed and does that first
        sf.updateData("members", "password", password, ("username", username))

    id = ("username", new_username or username)        

    updateUsername = lambda tables: [sf.updateData(table, "username", new_username, id) for table in tables]  # THis function updates the username in all tables.

    if new_username: updateUsername( ["members", "bookings"] ) # Changes username in all tables with a username column.
    if first: sf.updateData("members", "firstName", first, id) # Change first name
    if last: sf.updateData("members", "lastName", last, id) # Change last name

def member_GetBookings(username): # Get all bookings for a member.
    return sf.getData( "bookings", ("username", username), fetchAll=True)

def member_GetLoginDetails(username): # Get a member's username and password
    data = sf.getData("members", ("username", username), "username, password")
    if not data: return None
    username, password = sf.getData("members", ("username", username), "username, password")
    return {"username": username, "password": password}

# BOOKING FUNCTIONS 

def resort_Create(name, location, price, description, facilities):
    sf.insertData("resorts", (name, location, price, description, facilities))

def resort_Modify(name, location=None, price=None, description=None, facilities=None, new_name=None):

    id = ("name", new_name or name)
    
    updateName = lambda tables: [ sf.updateData(table, "name", new_name, id) for table in tables ]
    # This updates the resort name in all tables ( a list ) provided
    # Note that this won't actually be of use since we have "on update cascade" which pretty much does all we need.

    if location: sf.updateData("resort", "location", location, id) # Update location
    if price: sf.updateData("resorts", "price", price, id) # Update price
    if description: sf.updateData("resorts", "facilities", facilities, id) # Update facilities
    if new_name: updateName( ["resorts"] ) # Update resort name

def resort_Delete(name): # Careful, name is case sensitive! Make sure you don't mess this part up.

    try: sf.deleteData("resorts", ("name", name))
    except: return print("Couldn't delete", name, "! The username is case sensitive")

    # Also delete all related bookings
    sf.deleteData("bookings", ("resort_name", name))

def resort_GetDetails(name, *columns):
    # Get the details of a single resort
    columnsToGet = ",".join( list(map(str, columns)) )
    resort = sf.getData("resorts", ("name", name), columnsToGet or "*")
    if not resort: return None
    else: return dict( zip(columns or ["name", 'location', 'price', 'description', 'facilities'], resort) )

def resort_GetAll(*columns):
    # Get the details of all resorts
    columnsToGet = ",".join( list(map(str, columns)) )
    return [ dict( zip(columns, resort)) for resort in sf.getData("resorts", columnToGet=columnsToGet, fetchAll=True) ]


def resort_GetBookings(name):
    return sf.getData( "bookings", ("resort_name", name), fetchAll=True)

# BOOKING FUNCTIONS

def booking_Create(resort, username, start_date:dt.date, end_date:dt.date, occupants, cost):
    # The start_date and end_date arguments are datetime.date objects
    BOOKING_ID = uuid.uuid4().hex
    sf.insertData("bookings", (resort, username, start_date, end_date, occupants, cost, BOOKING_ID) )
    return BOOKING_ID

def booking_GetTiming(id):
     # Gets the start date and end date of a booking
    gt = lambda d: {
        "year": d.strftime("%Y"),
        "month": d.strftime("%m"),
        "day": d.strftime(r"%d"),
        "hour": d.strftime("%H"),
        "minute": d.strftime("%M")
    }
    start_date, end_date = sf.getData("bookings", ("id", id), "start_date, end_date")
    return { "start_date": gt(start_date), "end_date": gt(end_date) }

def booking_Modify(booking_id, start_date:dt.date=None, end_date:dt.date=None, occupants=None, cost=None):
    # Note that resort cannot be changed as it's a foreign key. ig it can be changed to a pre-existing resort in the resorts table but lets make life easier yeah?
    # Also you can't change the username because the fitness gram pacer test

    id = ("id", booking_id)

    sd, ed = sf.getData("bookings", ("id", booking_id), "start_date, end_date")
    if start_date and start_date >= ed: return print("[ERR] start date greater than or equal to end date")
    elif end_date and sd >= end_date: return print("[ERR] start date greater than or equal to end date")
    
    if start_date: sf.updateData("bookings", "start_date", start_date, id)
    if end_date: sf.updateData("bookings", "end_date", end_date, id)
    if occupants: sf.updateData("bookings", "occupants", occupants, id)
    if cost: sf.updateData("bookings", "cost", cost, id)

def booking_GetDetails(id, *columns):
    # Gets the details of a booking record
    columns = set(columns) or set("*")
    columnsToGet = ",".join( list(map(str, columns)) )
    result = dict( zip( columns, sf.getData("bookings", ("id", id), columnsToGet) ) )
    if any([ column in ["start_date", "end_date", "*"] for column in columns]): result.update( booking_GetTiming(id) )
    return result

def booking_GetAll(*columns):
    # Gets details of all bookings
    columns = ["resort_name", "username", "start_date", "end_date", "occupants","cost","id"]
    columnsToGet = ",".join( list(map(str, columns)) )
    results = [ dict(zip( columns, booking )) for booking in sf.getData("bookings", columnToGet=columnsToGet or None, fetchAll=True) ]
    for result in results:
        if any([ column in ["start_date", "end_date", "*"] for column in columns]): result.update( booking_GetTiming(result["id"]) )
    return results

def booking_GetBookingsBy(start_date_before:dt.date=None, end_date_before:dt.date=None, occupants:int=None, cost:int=None):
    # Gets bookings based on a constraint
    query = "SELECT * FROM bookings WHERE "
    q0 = query
    suffixAnd = lambda: query + 'AND ' if query[::-1][0:3][::-1] != "AND" and query != q0 else query

    if start_date_before: query = suffixAnd() + "start_date <= '" + start_date_before.strftime(r'%Y-%m-%d %H:%M:%S') + "' "
    if end_date_before: query = suffixAnd() + "end_date <= '" + end_date_before.strftime(r'%Y-%m-%d %H:%M:%S') + "' "
    if occupants: query = suffixAnd() + "occupants = " + str(occupants) + " "
    if cost: query = suffixAnd() + "cost = " + str(cost) + " "

    return sf.executeSQL(query).fetchall()

def booking_Delete(booking_id):
    # Deletes a booking
    sf.deleteData("bookings", ("id", booking_id))