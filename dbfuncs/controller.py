import uuid
from . import sqlfunc as sf
from .cipher.encryptor import encrypt
import datetime as dt

class controller():
    """
    Sub-classes:\n
    member() -> Stuff to do w the member database and updating members\n
    resort() -> Stuff to do w resorts and their properties\n
    """

    def __init__(self):
        self.member = Member
        self.resort = Resort
        self.bookings = Bookings

class Member(controller):

    def getName(self, username):
        first_name, last_name = sf.getData("members", ("username", username), "firstName, lastName")
        return {"first_name": first_name, "last_name": last_name}
    
    def create(self, username, first, last, password):
        encrypt(username, first, last, password)
    
    def delete(self, username):

        dlt = lambda *tables: [ sf.deleteData(table, ("username", username)) for table in tables]

        # Deleting from members, encryption tokens and bookings
        dlt("members", "encryptiontokens", "bookings")
    
    def modify(self, username, first=None, last=None, password=None, new_username=None):
        """
        Change any of the default-named parameters:\n
        first -> firstName\n
        last -> lastName\n
        password -> password for the account\n
        new_username -> username to change the account to\n
        """
        
        if password: # If the passwords changing, prioritize it.
            encrypt(username, first, last, password)

        id = ("username", new_username or username)        

        updateUsername = lambda tables: [sf.updateData(table, "username", new_username, id) for table in tables] 

        if new_username: updateUsername( ["members", "encryptiontokens", "bookings"] ) # Changes username in all tables with a username column.
        if first: sf.updateData("members", "firstName", first, id)
        if last: sf.updateData("members", "lastName", last, id)

    def getBookings(self, name):
        return sf.getData( "bookings", ("username", name), fetchAll=True)

class Resort(controller):
    
    def create(self, name, location, price, description, facilities):
        sf.insertData("resorts", (name, location, price, description, facilities))
    
    def modify(self, name, location=None, price=None, description=None, facilities=None, new_name=None):

        id = ("name", new_name or name)
        
        updateName = lambda tables: [ sf.updateData(table, "name", new_name, id) for table in tables ] # Note that this won't actually be of use since we have "on update cascade" which pretty much does all we need.

        if location: sf.updateData("resort", "location", location, id)
        if price: sf.updateData("resorts", "price", price, id)
        if description: sf.updateData("resorts", "facilities", facilities, id)
        if new_name: updateName( ["resorts"] )

    def delete(self, name): # Careful, name is case sensitive! Make sure you don't mess this part up.

        try: sf.deleteData("resorts", ("name", name))
        except: return print("Couldn't delete", name, "! The username is case sensitive")

        # Also delete all related bookings
        sf.deleteData("bookings", ("resort_name", name))

    def getDetails(self, name, *columns):
        columnsToGet = ",".join( list(map(str, columns)) )
        return dict( zip(columns, sf.getData("resorts", ("name", name), columnsToGet)) )
    
    def getBookings(self, name):
        return sf.getData( "bookings", ("resort_name", name), fetchAll=True)

class Bookings(controller):

    def create(self, resort, username, start_date:dt.date, end_date:dt.date, occupants, cost):
         # If you want to add a date, make sure it's a datetime.date object
        BOOKING_ID = uuid.uuid4().hex
        sf.insertData("bookings", (resort, username, start_date, end_date, occupants, cost, BOOKING_ID) )
        return BOOKING_ID
    
    def getTiming(self, id):

        gt = lambda d: {
            "year": d.strftime("%Y"),
            "month": d.strftime("%m"),
            "day": d.strftime(r"%d"),
            "hour": d.strftime("%H"),
            "minute": d.strftime("%M")
        }
        start_date, end_date = sf.getData("bookings", ("id", id), "start_date, end_date")
        return { "start_date": gt(start_date), "end_date": gt(end_date) }

    def modify(self, booking_id, start_date:dt.date=None, end_date:dt.date=None, occupants=None, cost=None):
        # Note that resort cannot be changed as it's a foreign key. ig it can be changed to a pre-existing resort in the resorts table but lets make life easier yeah?
        # Also you can't change the username because i'm being paid 400 bucks to do this.

        id = ("id", booking_id)

        sd, ed = sf.getData("bookings", ("id", booking_id), "start_date, end_date")
        if start_date and start_date >= ed: return print("[ERR] start date greater than or equal to end date")
        elif end_date and sd >= end_date: return print("[ERR] start date greater than or equal to end date")
        
        if start_date: sf.updateData("bookings", "start_date", start_date, id)
        if end_date: sf.updateData("bookings", "end_date", end_date, id)
        if occupants: sf.updateData("bookings", "occupants", occupants, id)
        if cost: sf.updateData("bookings", "cost", cost, id)

    def getDetails(self, id, *columns):
        columns = set(columns) or set("*")
        columnsToGet = ",".join( list(map(str, columns)) )
        result = dict( zip( columns, sf.getData("bookings", ("id", id), columnsToGet) ) )
        if any([ column in ["start_date", "end_date", "*"] for column in columns]): result.update( self.getTiming(id) )
        return result

    def getBookingsBy(self, start_date_before:dt.date=None, end_date_before:dt.date=None, occupants:int=None, cost:int=None):
        query = "SELECT * FROM bookings WHERE "
        q0 = query
        suffixAnd = lambda: query + 'AND ' if query[::-1][0:3][::-1] != "AND" and query != q0 else query

        if start_date_before: query = suffixAnd() + "start_date <= '" + start_date_before.strftime(r'%Y-%m-%d %H:%M:%S') + "' "
        if end_date_before: query = suffixAnd() + "end_date <= '" + end_date_before.strftime(r'%Y-%m-%d %H:%M:%S') + "' "
        if occupants: query = suffixAnd() + "occupants = " + str(occupants) + " "
        if cost: query = suffixAnd() + "cost = " + str(cost) + " "

        return sf.executeSQL(query).fetchall()

    def delete(self, booking_id):
        sf.deleteData("bookings", ("id", booking_id))