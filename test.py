from dbfuncs import sqlfunc as sf
from dbfuncs.fixData import fixData
import datetime as dt

# This function creates all needed databases and tables. You need to run this before starting the code.
fixData()

# Importing functions for:

from dbfuncs.controller import \
    member_Create, member_Delete, member_GetBookings, member_GetName, member_Modify, member_GetLoginDetails  # The members table
from dbfuncs.controller import \
    resort_Create, resort_Delete, resort_GetBookings, resort_GetDetails, resort_Modify # The resorts table
from dbfuncs.controller import \
    booking_Create, booking_Delete, booking_GetBookingsBy, booking_GetDetails, booking_GetTiming, booking_Modify # The bookings table

""" MEMBER FUNCTIONS """

# Creating a member with username "testacc"
member_Create(
    username = "testacc",\
    first = "Derin",
    last = "Arken",\
    password = "Sekrit123"
)

# Getting the name of a member
print(member_GetName("testacc")) # assert {'first_name': 'Derin', 'last_name': 'Arken'}

# Changing data of a member
member_Modify("testacc", first="Brian")
member_Modify(username="testacc", password="anEvenMoreSecretPasswordxyz123")

# Checking the changed data
print(member_GetName("testacc")) # assert {'first_name': 'Brian', 'last_name': 'Arken'}

""" RESORT FUNCTIONS """

# Creating a resort
resort_Create(
    name = "Fantasia",\
    location = "Bangalore",\
    price = "12000",\
    description = "A luxury hotel located in Koramangala, the liveliest place in Bangalore. World-class cuisine, facilities and rooms.",\
    facilities = "Room Service, Restaurant, Gift Store, Swimming Pool, Jacuzzi"
)

# Get specific data from a resort
print( resort_GetDetails("Fantasia", "name", "location") ) # assert {'name': 'Fantasia', 'location': 'Bangalore'}


""" BOOKING FUNCTIONS """

# Creating a booking
print("Creating a booking")
id = booking_Create("Fantasia", "testacc", "2020-02-02 12:12:12", "2020-02-02 12:12:13", 3, 1200) # Returns booking ID

# Modifying booking data
print("Modifying booking data")
booking_Modify(id, end_date=dt.date(year=2022, month=11, day=23), cost=9000)

booking_Modify(id, start_date=dt.date(year=3000, month=12, day=30)) # Will fail cuz start date > end date

# Getting data for a booking
print("Getting data for a booking")
print( booking_GetDetails(id) )

# Finding bookings based on a search criteria
print("Finding bookings based on a search criteria")
# Start date is before 6/3/2024 and cost is 9000
print( booking_GetBookingsBy(start_date_before=dt.date(year=2024, month=3, day=6),cost=9000) ) # Gets 1 result
# End date is before 18/6/2009
print( booking_GetBookingsBy(end_date_before=dt.date(year=2009, month=6, day=18)) ) # Gets no result

# Get all bookings made by username "testacc"
print( member_GetBookings("testacc") )

""" DELETING """

# Deleting a resort deletes all related bookings too
resort_Delete( "Fantasia" ) # Deletes a resort based on it's name

# Deleting a member does the same
member_Delete("testacc") # Deletes a member based on their username

sf.cleanConnection() # Closing the connection to the database