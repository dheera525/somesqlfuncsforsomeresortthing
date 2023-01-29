# every table in the database and their formats

class Format():
    # This class basically takes 3 arguments. Table, Syntax and Columns. It organizes that into a class called format. (x).table, (x).syntax, (x).columns define it's properties. 
    def __init__ (self, table, syntax, columns):
        self.table = table 
        self.syntax = syntax 
        self.columns = columns 

# Formats:

Members = Format(
    "members", # The name of the table | table

    """
    username varchar(255) PRIMARY KEY,
    firstName varchar(255) NOT NULL,
    lastName varchar(255),
    password varchar(255) NOT NULL
    """, # The syntax to create the table | syntax

    "(username, firstName, lastName, password)" # All the column names stored in a tuple. | columns
)

Resorts = Format(
    "resorts",

    """
    name varchar(255) PRIMARY KEY,
    location varchar(255) NOT NULL,
    price int NOT NULL,
    description varchar(690),
    facilities varchar(420)
    """,

    "(name, location, price, description, facilities)"
)

Bookings = Format(
    "bookings",

    """
    resort_name varchar(255),
    username varchar(255) NOT NULL,
    start_date date NOT NULL,
    end_date date,
    occupants int DEFAULT 1,
    cost int NOT NULL,
    id varchar(50) PRIMARY KEY,
    FOREIGN KEY (resort_name) REFERENCES resorts(name) on update cascade on delete cascade
    """,

    "(resort_name, username, start_date, end_date, occupants, cost, id)"

)

# Database-table map
formats = {
    "resortdb": {
        "members": Members,
        "resorts": Resorts,
        "bookings": Bookings
    }
}