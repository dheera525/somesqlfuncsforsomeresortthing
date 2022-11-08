from dbfuncs.controller import controller 
from dbfuncs import sqlfunc as sf
from dbfuncs.fixData import fixData
import datetime as dt

# This function creates all needed databases and tables. You need to run this before starting your code.
fixData()

# This is the SQL controller class (cuz it sounds cool).
# You have to initialize a controller for each table.
ctrl = controller()

# Initializing controllers for:

member = ctrl.member() # The members table
resort = ctrl.resort() # The resorts table
bookings = ctrl.bookings() # The bookings table

""" MEMBER FUNCTIONS """

# Creating a member with username "testacc"
member.create(
    username = "testacc",\
    first = "Derin",
    last = "Arken",\
    password = "Sekrit123"
)

# Getting the name of a member
print(member.getName("testacc")) # assert {'first_name': 'Derin', 'last_name': 'Arken'}

# Changing data of a member
member.modify("testacc", first="Brian")

# Checking the changed data
print(member.getName("testacc")) # assert {'first_name': 'Brian', 'last_name': 'Arken'}

""" RESORT FUNCTIONS """

# Creating a resort
resort.create(
    name = "Fantasia",\
    location = "Bangalore",\
    price = "12000",\
    description = "A luxury hotel located in Koramangala, the liveliest place in Bangalore. World-class cuisine, facilities and rooms.",\
    facilities = "Room Service, Restaurant, Gift Store, Swimming Pool, Jacuzzi"
)

# Get specific data from a resort
print( resort.getDetails("Fantasia", "name", "location") ) # assert {'name': 'Fantasia', 'location': 'Bangalore'}


""" BOOKING FUNCTIONS """

# Creating a booking
print("Creating a booking")
id = bookings.create("Fantasia", "testacc", "2020-02-02 12:12:12", "2020-02-02 12:12:13", 3, 1200) # Returns booking ID

# Modifying booking data
print("Modifying booking data")
bookings.modify(id, end_date=dt.date(year=2022, month=11, day=23), cost=9000)

bookings.modify(id, start_date=dt.date(year=3000, month=12, day=30)) # Will fail cuz start date > end date

# Getting data for a booking
print("Getting data for a booking")
print( bookings.getDetails(id) )

# Finding bookings based on a search criteria
print("Finding bookings based on a search criteria")
# Start date is before 6/3/2024 and cost is 9000
print( bookings.getBookingsBy(start_date_before=dt.date(year=2024, month=3, day=6),cost=9000) ) # Gets 1 result
# End date is before 18/6/2009
print( bookings.getBookingsBy(end_date_before=dt.date(year=2009, month=6, day=18)) ) # Gets no result

# Get all bookings made by username "testacc"
print( member.getBookings("testacc") )

""" DELETING """

# Deleting a resort deletes all related bookings too
resort.delete( "Fantasia" ) # Deletes a resort based on it's name

# Deleting a member does the same
member.delete("testacc") # Deletes a member based on their username

