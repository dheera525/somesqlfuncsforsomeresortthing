# All the functions that are used throughout the entire app.

import os
from dbfuncs import controller, sqlfunc
import PySimpleGUI as sg
from sys import exit

def moveTab(window:sg.Window,tabgroup:str,fromTab:str,toTab:str):
    """
    Moves from one tab to another, deselecting the older tab.
    """
    window[tabgroup].Widget.select(window.metadata['tabs'].index(toTab))
    deselectTab(window,fromTab)

def deselectTab(window:sg.Window,tab:str):
    """
    Hides a tab.
    """
    window[tab].update(visible=False)

def getFonts() -> list[str]:
    """
    Get all current installed fonts on the user's computer.
    """
    root = sg.tk.Tk()
    fonts = list(sg.tk.font.families())
    root.destroy()
    return fonts

def initUserDB(username:str=sqlfunc.existingUser()) -> dict:
    """
    Create a new data table for the specified user (or current user)\n
    Check dbfunc/dataTables.py for details on what functions you can use\n
    Example: initUserDB()["loggedInStatus"].isCurrentUser()

    """
    userDB = controller.dataTables(username).initializeUser()
    return userDB

def getPath(path:str) -> str:
    """
    Returns an absolute path from a relative path.
    """
    return os.path.abspath(path)

def isThemeDark(user:str=sqlfunc.existingUser()) -> bool:
    """
    Returns a boolean indicating whether the current theme is dark or not.
    """
    userDB = initUserDB(user)
    try:
        isThemeDark = (userDB["settings"].getPreference("theme") == "DarkGrey8")
    except:
        isThemeDark = False # Probably because this is being called before logging in
    return isThemeDark

def getDefaultFont(user:str=sqlfunc.existingUser()) -> str:
    """
    Get the current preferred font for the specified user (otherwise current user) from database.
    """
    userDB = initUserDB(user)
    return userDB["settings"].getPreference("font")

def getButton(button_name:str,invert:bool=False) -> str:
    """
    Returns a path to amigoose_assets/(button_name)_[color]\n\n

    invert - Boolean - Whether to invert the colour of the image
    """

    if not invert:
        button = getPath(f"./assets/amigoose_assets/{button_name}_{'light' if isThemeDark() else 'dark'}.png")
    else:
        button = getPath(f"./assets/amigoose_assets/{button_name}_{'dark' if isThemeDark() else 'light'}.png")
    return button

def playHonk():
    """
    Plays the classic honk.mp3
    """
    import vlc
    p = vlc.MediaPlayer(getPath("./assets/amigoose_assets/HJONK.mp3"))
    p.play()

def getTheme(user:str=sqlfunc.existingUser()) -> str:
    """
    Get the current preferred theme for the specified user (otherwise current user) from database.\n
    user - Username to get theme preference for - String
    """
    userDB = initUserDB(user)
    return userDB["settings"].getPreference("theme")

def getThemeBackground() -> tuple:
    """
    Returns the button-color or for transparent buttons to use. \n
    > (theme_bg_colour,theme_bg_colour)
    """
    return (sg.theme_background_color(),sg.theme_background_color())

def isUser(username:str) -> bool:
    """
    Responds with a boolean indicating whether the provided name is the name of a user.\n
    username - Username to check - String
    """
    usernames = sqlfunc.loadColumn("passwords","username")
    return username in usernames

def checkIllegalInput(value:str) -> bool:
    """
    Checks if text is a potential SQL Injection\n
    Value - Text to check - String
    """
    return all(map(lambda x: x not in value,[";","'","\"", " OR "]))

def sanitizeEvent(event:str, allowNumbers=False) -> str:
    """
    Sometimes while nesting windows, the events have numbers allocated to them so that they don't get mixed.\n
    This removes those numbers by selecting only the alphabets, - and _ characters.\n
    Event - Event to check - String
    """
    import re
    if not event: return None

    # I don't even remember making this regex and have no idea why I made it. But all I know is if I remove it, the code breaks. This must stay :)

    if (allowNumbers):
        if re.search("([a-zA-Z0-9_\+-]+)", event): return re.search("([a-zA-Z0-9_\+-]+)", event).group(1)
    
    from string import digits
    event = event.rstrip(digits)
    return event

def getBasename(filePath:str) -> str:
    """
    Returns the basename of the file path\n\n
    filePath - String - Path to the file
    """
    return os.path.basename(filePath)

def prettyDate(time:int):
    """
    Get a pretty string like 'an hour ago', 'Yesterday', '3 months ago' etc from a UNIX/EPOCH integer,\n

    Thanks to https://stackoverflow.com/questions/1551382/user-friendly-time-format-in-python/ \n
    The alternative was to use the "arrow" or "humanize" packages but I didn't want to clutter my deps\n

    time - Integer - UNIX/EPOCH integer of the time.
    """
    from datetime import datetime
    now = datetime.now()
    diff = now - datetime.fromtimestamp(time)
    second_diff = diff.seconds
    day_diff = diff.days

    if day_diff < 0:
        return '???'

    if day_diff == 0:
        if second_diff < 10:
            return "just now"
        if second_diff < 60:
            return str(second_diff) + " s"
        if second_diff < 120:
            return "a minute ago"
        if second_diff < 3600:
            return str(second_diff // 60) + " min"
        if second_diff < 7200:
            return "an hour ago"
        if second_diff < 86400:
            return str(second_diff // 3600) + " h"
    if day_diff == 1:
        return "Yesterday"
    if day_diff < 7:
        return str(day_diff) + " d"
    if day_diff < 31:
        return str(day_diff // 7) + " w"
    if day_diff < 365:
        return str(day_diff // 30) + " mo"
    return str(day_diff // 365) + " y"

class WinElement():
    """
    Window Element. PySimpleGUI window controller I made for easy access.\n\n

    Parameters -> run (PySimpleGUI watcher), window (PySimpleGUI window)

    + .start() -> Starts the window and it's watcher.\n
    Arguments: \n
    argsWindow [ Make a window with specific arguments ]\n\n

    + .stop() -> Stops the window.\n
    Arguments: \n
    noKill | restart [ Stops the window but not it's watcher. Restart restarts the window. ]\n
    argsWin [ Arguments for the next time the window restarts, if it does. ]\n

    """
    def __init__(self,run,window):
        self.run = run
        self.makeWindow = window

    def start(self, argsWindow=None, argsWatch=None):

        def parseArgs(args):
            # This will make all args into a tuple
            return (args,) if not args is None and type(args) != tuple else args

        argsWindow = parseArgs(argsWindow)
        argsWatch = parseArgs(argsWatch)

        self.window = self.makeWindow(*argsWindow) if argsWindow else self.makeWindow()
        self.restart = False
        result = False
        while True:
            if (self.restart):
                self.restart = False
                break
            toBreak = self.run(self.window,*argsWatch) if argsWatch else self.run(self.window)
            if (toBreak and toBreak[0]):
                if (toBreak[1]):
                    result = toBreak[1]
                    break
                else:
                    exit(0)
        return result

    def stop(self,restart=False,noKill=False, argsWin=None, argsWatch=None):
        if noKill or restart:
            self.restart = True    

        if restart:
            self.window.close()
            return self.start(argsWindow=argsWin,argsWatch=argsWatch)
        
        return self.window.close()
        

class TabElement():
    """
    Tab Element. PySimpleGUI Tab controller I made for easy access\n\n
    
    Exec is the tab watcher which continuously scans for tab events, similar to window watcher.\n
    Layout is the pre-generated tab layout that the user can switch to.\n\n

    **.getLayout()** -> Returns the tab's layout.\n
    argsLayout [ arguments for generating the tab layout ]\n
    """
    def __init__(self,layout,exec):
        self.exec = exec
        self.layout = layout
    def getLayout(self,argsLayout=None):
        return (self.layout(argsLayout) if argsLayout else self.layout()).copy()