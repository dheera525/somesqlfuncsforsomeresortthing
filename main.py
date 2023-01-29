""" IMPORTING MODULES """

import terminaltables as tt
from dbfuncs import sqlfunc as sf, fixData as fd
import os
import sys
import datetime as dt
from dbfuncs.controller import *  # Import everything from controller

""" CONSTANTS """

ASCII_ART = """
 _    __                 __  _                 
| |  / /___ __________ _/ /_(_)___  ____       
| | / / __ `/ ___/ __ `/ __/ / __ \/ __ \      
| |/ / /_/ / /__/ /_/ / /_/ / /_/ / / / /      
|___/\__,_/\___/\__,_/\__/_/\____/_/ /_/       
      | |  / /___  __  ______ _____ ____  _____
      | | / / __ \/ / / / __ `/ __ `/ _ \/ ___/
      | |/ / /_/ / /_/ / /_/ / /_/ /  __/ /    
      |___/\____/\__, /\__,_/\__, /\___/_/     
                /____/      /____/             
"""
USER_PRIVILEGE = None # 0 or 1 depending on user privilege
USERNAME = None # Username of the currently logged in user

""" FUNCTIONS """

def clearScreen(): # Clear the screen.
    os.system('cls')

def selectPrivilege():

    global USER_PRIVILEGE

    user_priv_options = [
        ['Choose your user privilege: '],
        ['0) Administrator'],
        ['1) Client'],
        ['E) Exit ->']
    ]

    user_priv_table = tt.DoubleTable(user_priv_options)

    user_priv_table.outer_border = True
    user_priv_table.inner_heading_row_border = False
    user_priv_table.inner_column_border = False
    
    while True:

        print(user_priv_table.table)
        
        USER_PRIVILEGE = input("> ").lower()
        
        if ( USER_PRIVILEGE not in [option[0][0].lower() for option in user_priv_options[1:]] ):  # '0','1','e'
            clearScreen()
            print("Invalid option.")
            continue

        USER_PRIVILEGE = int(USER_PRIVILEGE) if USER_PRIVILEGE != 'e' else [print("Goodbye!"), exit(0)]

        return USER_PRIVILEGE


# Splits the detail by '_', capitalizes each word and joins with a whitespace.
# Like test_case -> Test Case
normalize = lambda q: " ".join(map( lambda x: x.capitalize(), q.split('_') ))


def askPersist( toAsk:list, header=(['',''],), title='', footer=([''],), breakPoints=[] ):

    """
    Continuously ask the user for input until all fields provided in toAsk is are filled.
    Use headers, titles, footers to decorate.
    Use breakpoints to configure a special response for which it stops asking the user for input and returns the breakpoint.
    """

    ALL_DETAILS = {}

    def askBox(query): 

        # This formula arranges a list consisting of 
        # 1: The header, if given
        # 2: A key-value based nested list called ALL_DETAILS
        # For Example: [ ["Username", "HiddenEntropy100"], ["Code", 119081].. etc ]
        # 3: The current query/key being requested. Example: ["Name", "Entering..."]
        table_data = [ *header, *zip( [ f'{index + 1}: {key}' for index,key in enumerate(ALL_DETAILS) ], [ value for value in ALL_DETAILS.values() ] ), [ f'{len(ALL_DETAILS) + 1}: ' + query, "Entering..."], [''], [''],[footer]]
        table_instance = tt.SingleTable(table_data, title) # Make a single-line table out of it.

        # Makes a nice table without inner borders.
        table_instance.outer_border = True
        table_instance.inner_heading_row_border = False
        table_instance.inner_column_border = False

        return table_instance.table
    
    for detail in toAsk:

        query_detail = normalize(detail)
        response = None

        while True:
            print( askBox(query_detail) )
            response = input(f"Enter your {query_detail}\n> ")

            if not response:
                print("Please input something!")
                continue

            elif response.lower() in breakPoints: return response.lower()

            break

        ALL_DETAILS[detail] = response
    
    return ALL_DETAILS


def accountPage(mode="login"):

    def tryLogin():

        return askPersist( 
            ["username", "password"],
            title="| LOG IN |",
            footer="Enter \"R\" to register a new account instead\nEnter \"E\" to exit.",
            breakPoints=["r","e"]
            )

    def tryRegister():

        return askPersist(
            ["username", "password", "repeat_password", "first_name", "last_name"],
            title="| REGISTER |",
            footer="Enter \"L\" to login with an existing account instead\nEnter \"E\" to exit.",
            breakPoints=["l","e"]
        )
    
    data = None # The data returned after user tries to login/register.

    if mode == "login":
        data = tryLogin()
        if data == "e": exit(0) # If "e" is entered, exit
        if data == "r":
            clearScreen()
            return accountPage(mode="register")

    if mode == "register":
        data = tryRegister()
        if data == "e": exit(0)
        if data == "l":
            clearScreen()
            return accountPage(mode="login")
        if data["password"] != data["repeat_password"]:
            print("Passwords do not match! Try again.")
            return accountPage(mode="register")

    return data

def verifyLogin(data):
    
    if "repeat_password" in data.keys(): # If the data contains "repeat_password", it's probably a registration.

        if data["repeat_password"] != data["password"]: # Check if the repeated password matches the password they entered.
            
            print("Repeated password does not match! Try again.")
            return verifyLogin( accountPage( mode="register" ) ) # Otherwise make them do it again.

        member_Create(data["username"], data["first_name"], data["last_name"], data["password"]) # Create the user's profile. Complete their registration.

    memberDetails = member_GetLoginDetails(data["username"]) # Get the account details for a member.

    if not memberDetails: return None # If the login details do not match.

    if memberDetails["password"] == data["password"]:   
        return data["username"] # Return the username if it works.
    else: return None # Otherwise return nothing and fail.

def showAllResorts():

    clearScreen()
    HEADER = (["Name", "Location", "Price/Night"],)
    resorts = sorted(resort_GetAll("name", "location", "price"), key=lambda resort: resort['location'])

    resorts_table = tt.DoubleTable([*HEADER, *[ list(resort.values()) for resort in resorts] ] or [ "No resorts!" ], "| VV - All Resorts |")

    print(resorts_table.table)

def showResortDetails():

    while True:

        print( tt.SingleTable([ ["Enter the name of the resort you would like to get details about\nEnter 'e' to quit. "] ]).table )
        resortName = input("> ")

        resort = resort_GetDetails(resortName)
        if not resort:
            print("[ERR] Invalid Resort Name.\n")
            continue
        
        clearScreen()
        
        resortTables = [
            
        tt.SingleTable([
            [resort["name"]],
        ], f"| VV - Viewing {resort['name']} |"),

        tt.SingleTable([
            ["Located in", resort["location"]]
        ]),
        
        tt.SingleTable([
            [resort["description"]]
        ]),

        tt.SingleTable([
            [f"With facilities like {resort['facilities']}"]
        ]),

        tt.SingleTable([
            ["Costs", str(resort["price"]) + " per night"],
        ]),

        ]
        
        allResortTable = tt.DoubleTable(
            [
                *[[resortTable.table] for resortTable in resortTables],
                ["<" + "-" * len(resort["name"]) + ">"]
            ],
            f"| VV - Viewing {resort['name']} |"
        )

        for resortTable in resortTables + [allResortTable]:
            resortTable.outer_border = True
            resortTable.inner_heading_row_border = False
            resortTable.inner_column_border = False
            resortTable.justify_columns = {0: 'center', 1: 'center'}
            resortTable.inner_footing_row_border = True

        return [print(allResortTable.table)]

def bookResort():
    global USERNAME

    while True:

        print("NOTE: ENTER 'E' TO QUIT.")
        print( tt.SingleTable([ ["What is the name of the resort?"] ]).table )
        resortName = input("> ")

        if resortName == "e": return print("Press enter to return to menu.")

        if not resort_GetDetails(resortName):
            print("That's an invalid resort name! Try again.")
            continue
        
        start_date =  askPersist(
            ["day", "month", "year"],
            title="| REGISTER |",
            footer="When does your booking start?\nEnter \"E\" to exit.",
            breakPoints=["e"]
        )

        if start_date == "e": return print("Press enter to return to menu.")

        end_date =  askPersist(
            ["day", "month", "year"],
            title="| REGISTER |",
            footer="When does your booking end?\nEnter \"E\" to exit.",
            breakPoints=["e"]
        )

        for item in list(start_date.values()) + list(end_date.values()):
            try: int(item)
            except ValueError: continue

        if end_date == "e": return print("Press enter to return to menu.")

        while True:
            occupants = input("Enter number of occupants\n> ")
            if occupants == "e": return print("Press enter to return to menu.")
            if occupants not in ('12345678'): continue # MAX 8 OCCUPANTS BECAUSE HOW ARE YOU GOING TO FIT 9 PEOPLE IN A ROOM
            break
        
        cost = resort_GetDetails(resortName)["price"] * int(occupants)

        booking_id = booking_Create( 
            resort= resortName, 
            username= USERNAME,
            start_date= dt.date(
                year= int(start_date["year"]),
                month= int(start_date["month"]),
                day= int(start_date["day"])
            ),
            end_date= dt.date(
                year= int(end_date['year']),
                month= int(end_date['month']),
                day= int(end_date['day'])
            ),
            occupants= occupants,
            cost= cost
        )
        
        print( tt.SingleTable([ ["Booking Created!\nYour booking ID is " + booking_id + "\nYou have chosen to pay by cash at the venue"] ]).table )

def seeBookings():
    global USERNAME

    all_bookings = booking_GetAll()

    bookingsTableData = []

    for booking in all_bookings:
        resort_details = resort_GetDetails(booking["resort_name"])
        first_name = member_GetName(USERNAME)["first_name"]
        sd = booking["start_date"]
        ed = booking["end_date"]
        bookingsTableData.extend(
            [   
                [],
                [f"| Booking {all_bookings.index(booking) + 1}"],
                ["Resort:", booking["resort_name"]],
                ["Located at", resort_details['location']],
                ["Booked for", f"{booking['occupants']} occupants"],
                [f"Priced {booking['occupants']} x {resort_details['price']} = ", booking["cost"]],
                [f"Check-in on {sd['day']}/{sd['month']}/{sd['year']} and Check-out on {sd['day']}/{sd['month']}{ ('/' + ed['year']) if sd['year'] != ed['year'] else ' during the same year'}"],
                ["BOOKING ID", booking['id']],
                []
            ]
        )
    
    bookingsTable = tt.SingleTable( bookingsTableData, f"| VV - All Bookings for {first_name} |" )
    bookingsTable.justify_columns = {0: 'left', 1: "right"}
    bookingsTable.outer_border = True
    bookingsTable.inner_heading_row_border = False
    bookingsTable.inner_column_border = False

    clearScreen()
    print(bookingsTable.table)

def cancelBooking():

    while True:
        print( tt.SingleTable([ ["Enter the ID of the booking you want to cancel\nEnter 'e' to exit."] ]).table )
        booking_id = input("> ")
        if booking_id == "e": return print("Press enter to return to menu.")

        booking = sf.getData("bookings", ("id", booking_id))
        if not booking:
            print("Invalid Booking ID!")
            continue
        
        booking_Delete(booking_id)
        return print("Successfully deleted the booking at " + booking[0] + "!")
    

def restart(): # Restart this script
    os.execv(sys.executable, ['python'] + sys.argv) # Restarts this python file.

def clientMenu():
    first_name = member_GetName(USERNAME)["first_name"]

    date = dt.datetime.today().strftime("%A | %I:%M %p")

    rows = [ 
        ["| Resorts"],
        ["  (1)", "Explore resorts"],
        ["  (2)", "Get details about a resort"],
        ["  (3)", "Book a resort"],
        ["| Bookings"],
        ["  (4)", "See my bookings"],
        ["  (5)", "Cancel a booking"],
        ["| Me"],
        ["  (6)", "Change account settings"],
        ["  (7)", "Logout"],
        ["| System"],
        ["  (e)", "Exit application"]
         ]

    commandHandler = {
        1: showAllResorts,
        2: showResortDetails,
        3: bookResort,
        4: seeBookings,
        5: cancelBooking,
        7: restart,
        'e': exit
    }

    menuLayout = (
        ["", "", "", "X"],
        ['', f"", date + f"\nHello, {first_name}"],
        ["","",""],
        *rows
    )

    menuTable = tt.SingleTable(menuLayout, "| VV - Client Menu |")
    menuTable.justify_columns = {0: 'left', 1: "left", 3: 'right', 4: 'right'}
    menuTable.outer_border = True
    menuTable.inner_heading_row_border = True
    menuTable.inner_column_border = False

    while True:

        print(menuTable.table)
        res = input("Enter the number of the command you'd like to execute\n> ")

        try: res = int(res) # attempt to convert res to an integer
        except ValueError: pass

        if res not in commandHandler.keys():
            clearScreen()
            print("That's an invalid command! Please only select a command from this list.")
            continue
            
        commandHandler[res]() # Execute the respective command
        input("\n")
        
def adminMenu():

    first_name = member_GetName(USERNAME)["first_name"]

    date = dt.datetime.today().strftime("%A | %I:%M %p")

    rows = [ 
        ["| Resorts"],
        ["  (1)", "Add a resort"],
        ["  (2)", "Remove a resort"],
        ["  (3)", "Modify a resort"],
        ["| Bookings"],
        ["  (4)", "See bookings for a certain user"],
        ["  (5)", "Cancel a booking"],
        ["  (6)", "Modify a booking"],
        ["| Users"],
        ["  (7)", "Modify a user"],
        ["  (8)", "Delete a user"],
        ["| System"],
        ["  (e)", "Exit application"]
         ]

    commandHandler = {
        'e': exit
    }

    menuLayout = (
        ["", "", "", "X"],
        ['', f"", date + f"\nWelcome back, {first_name}"],
        ["","",""],
        *rows
    )

    menuTable = tt.SingleTable(menuLayout, "| VV - Admin Panel |")
    menuTable.justify_columns = {0: 'left', 1: "left", 3: 'right', 4: 'right'}
    menuTable.outer_border = True
    menuTable.inner_heading_row_border = True
    menuTable.inner_column_border = False

    while True:

        print(menuTable.table)
        res = input("Enter the number of the command you'd like to execute\n> ")

        try: res = int(res) # attempt to convert res to an integer
        except ValueError: pass

        if res not in commandHandler.keys():
            clearScreen()
            print("That's an invalid command! Please only select a command from this list.")
            continue
            
        commandHandler[res]() # Execute the respective command
        input("\n")

""" RUNTIME CODE """

fd.fixData()

clearScreen()
while True:

    # Have the user select their privilege.
    print(ASCII_ART)
    selectPrivilege()
    
    # If the user is a client, ask them to signup/signin
    if USER_PRIVILEGE == 1:
        data = accountPage() # Get them to signup/signin
        if not verifyLogin(data): # Verify their login details.
            clearScreen()
            print("Your login details were invalid, try again!")    
            continue
        USERNAME = data["username"] # Log the user in, officially.
    
    clearScreen()
    if USER_PRIVILEGE == 1:
        clientMenu() # Open up the client menu if the user is a client
    elif USER_PRIVILEGE == 0:
        adminMenu() # Open up the admin menu if the user is an admin
    
    exit(0)