import csv, json, pickle, platform
from collections import defaultdict
from tkinter import *
from tkinter.ttk import Separator, Scrollbar

# A list of widget types that take ARGS instead of KWARGS
# (ie. widgets that must take multiple positional variables on initialisation)
COMPLEXWIDGETS = [OptionMenu]

# A dictionary of widget types and their possible styles ( '-' tag means override; all widgets of this type will override
# the loaded application theme and keep their own style (for specific feature: bg, fg, etc... ))
WIDGET_STYLES = {
    Label: ["fg", "bg"],
    Frame: ["bg"],
    Button: ["fg-black", "bg-white"],
    Entry: ["fg", "bg-white"],
    OptionMenu: ["fg-black", "bg-white"],
    LabelFrame: ["fg", "bg"],
    Canvas: ["bg"],
    Menu: [] # No styling done to Menu widgets
}

# A dictionary of widget names with features of the associated widget that should be overridden
OVERRIDE_WIDGET_FEATURES = defaultdict(list, {
    "label_errormessage": ["fg-red"]
})

# Dictionary of options saved to pickle file for persistance between application runs
BASIC_PERSIST = {
    "THEME": "default"
}

class BeerEncoder(json.JSONEncoder):
    """ An encoder class for saving Beer object data to JSON """
    def default(self, o):
        return o.__dict__

class Beer:
    """ Beer object. Stores all data about custom beers, including name, recipe, ABV, gravity, etc..."""

    def __init__(self, name, jsondata=None):
        """ Initialise the Beer object, loading its data from JSON string if passed """
        self.name = name
        if jsondata:
            self.type = jsondata["type"]
            self.abv, self.gravity = jsondata["abv"], jsondata["gravity"]
            self.ibu, self.srm = jsondata["ibu"], jsondata["srm"]
            self.servingtemp = jsondata["servingtemp"]
            # self.recipe = jsondata["recipe"]
            # self.image = None

    def __repr__(self):
        return f"<Beer ({self.type}): {self.name}>"

    def __str__(self):
        return repr(self)

    def _getformattedname(self):
        """ Returns the formatted name for view button """
        return "".join([w.capitalize() for w in self.name.split()])

    def displayInformation(self):
        """ Creates a popup window showing the beer's data """
        popup = PopupWindow(self.name)
        Label(popup.popup, text=self.name, font=("Helvetica", 18, "bold")).grid(row=0, column=0, columnspan=2)
        Separator(popup.popup, orient=HORIZONTAL).grid(row=1, column=0, columnspan=2, sticky="ew")
        datapairs = [("name", self.name), ("beer type", self.type), ("abv", self.abv), ("serving temp.", self.servingtemp),
        ("gravity", self.gravity), ("ibu", self.ibu), ("srm", self.srm)]
        for r in range(1, 8):
            t, d = datapairs[r-1]
            Label(popup.popup, text=t.capitalize()).grid(row=r+1, column=0)
            Label(popup.popup, text=d).grid(row=r+1, column=1)
        Separator(popup.popup, orient=HORIZONTAL).grid(row=9, column=0, columnspan=2, sticky="ew")
        Button(popup.popup, text="Delete Beer", command=lambda: deleteBeer(self.name) ).grid(row=10, column=0, columnspan=2)

class PopupWindow(Toplevel):
    """ PopupWindow object. Blueprint for the popup windows shown when editing preferences, viewing beers, etc. """
    def __init__(self, title, minsize=(None, None), resizable=False):
        self.popup = Toplevel(application.app)
        self.popup.title(title)
        self.popup.resizable(width=resizable, height=resizable)
        self.popup.minsize(*minsize)
        menubar = Menu(self.popup)
        self.popup.config(menu=menubar)

class Application(Tk):
    """ Application object. Blueprint for the window shown to user, with custom methods to allow for easier adding of widgets """
    def __init__(self, /, *, title, \
        size="650x500+400+200", jsonpath="data/beers.json", iconpath="assets/icon.ico"):
        self.app = Tk()
        self.title, self.iconpath = title, iconpath
        self.options = self.loadPickle()
        self.rows, self.cols = 1, 1
        self.app.title(title)
        self.app.geometry(size)
        self.app.minsize(650, 500)
        self.widgets = defaultdict(None)
        self.beers = loadBeers(jsonpath)
        self.theme_name = self.options["THEME"]
        self.theme = self.applyTheme()

    def __repr__(self):
        return f"<Application: {self.title}>"

    def __str__(self):
        return repr(self)

    def loadPickle(self, persist="data/persist.pk"):
        """ Loads pickled persistant data (ie. options kept between program instances) from file, unpickles and returns """
        try:
            with open(persist, "rb") as pckl_file:
                persist_data = pickle.load(pckl_file)
        except FileNotFoundError:
            with open(persist, "wb") as pckl_file:
                pickle.dump(BASIC_PERSIST, pckl_file)
                persist_data = BASIC_PERSIST
        return persist_data

    def applyTheme(self, override=None):
        """ Applies the loaded theme to the application window. If the theme is default, do nothing and return """
        if self.theme_name == "default": return None # If theme is default
        loaded_theme = loadTheme(self.theme_name)
        if loaded_theme == None: return None # If theme doesn't exist
        self.app["bg"] = loaded_theme["bg"]
        return loaded_theme

    def packWidget(self, master, widget_type, widget_name, *args, pkws=None, **kwargs):
        """ Creates a new instance of widget with kwargs, packs onto master widget, saves the instance to Application.items
            and returns widget instance for use """
        widget = widget_type(master, kwargs)
        for feature in WIDGET_STYLES[widget_type]:
            # overriding application theme for custom colour (ie. Entry boxes bg always white, fg always black)
            self.override(widget, feature)
        if ( override := OVERRIDE_WIDGET_FEATURES[widget_name] ):
            for feature in override:
                for feature in override: self.override(widget, feature)
        if pkws: widget.pack(pkws)
        else: widget.pack()
        self.widgets[widget_name] = widget
        return widget

    def gridWidget(self, master, widget_type, widget_name, *args, row, column, gkws=None, **kwargs):
        """ Resizes grid layout, creates a new widget instance with args and kwargs, adds to the grid,
            saves the instance to Application.items and returns widget instance for use """
        if row > self.rows: self.rows = row
        if column > self.cols: self.cols = column
        if widget_type in COMPLEXWIDGETS: widget = widget_type(master, *args)
        else: widget = widget_type(master, kwargs)
        for feature in WIDGET_STYLES[widget_type]:
            # overriding application theme for custom colour (ie. Entry boxes bg always white, fg always black)
            self.override(widget, feature)
        if ( override := OVERRIDE_WIDGET_FEATURES[widget_name] ):
            for feature in override: self.override(widget, feature)
        if gkws: widget.grid(row=row, column=column, **gkws)
        else: widget.grid(row=row, column=column)
        self.widgets[widget_name] = widget
        return widget

    def override(self, widget, feature):
        if "-" in feature: feature, col = feature.split('-')
        elif "=" in feature:
            feature, col = feature.split("=")
            try:
                col = self.theme[col]
            except KeyError as e:
                print(f"Failed assigning '{col}' to {repr(widget)}[{feature}]")
                print(f"No theme feature called '{col}'. Perhaps you meant to use a '-' instead of a '=' when defining overrides?")
                quit()
        else: col = self.theme[feature]
        try:
            widget[feature] = col
        except TclError as e:
            print(f"Failed assigning '{col}' to {repr(widget)}[{feature}]")
            print(f"No theme feature called '{col}'. Perhaps you meant to use a '=' instead of a '-' when defining overrides?")
            quit()

def createBeer(application, data):
    """ Creates a new beer, adds it to the 'application.beers' list, and saves it to the JSON file """
    name = data.pop(0)
    if name.get().lower() in map(lambda b: b.name.lower(), application.beers):
        application.widgets["label_errormessage"]["text"] = "Error adding beer. Name already taken"
        return False
    elif name.get() == "":
        application.widgets["label_errormessage"]["text"] = "Error adding beer. Enter valid name"
        return False
    else:
        headers = ["type", "servingtemp", "abv", "ibu", "srm", "gravity"]
        newbeer = Beer(name.get())
        for (kw, v) in zip(headers, data):
            val = repr(v.get())
            if len(v.get()) == 0 or (kw=="type" and v.get()=="Choose a type") or (kw=="srm" and v.get()=="Choose an SRM value"):
                keyword = kw if kw != "servingtemp" else "serving temp"
                application.widgets["label_errormessage"]["text"] = f"Error adding beer. Enter valid {keyword}."
                return False
            exec(f"newbeer.{kw} = {val}")
        application.beers.append(newbeer)
        saveBeers(application.beers)
        application = restartApplication(application)

def deleteBeer(beername):
    """ Removes the beer with the given name from the beers list, saves the list, then reloads the application """
    global application
    application.beers = filter(lambda b: b.name != beername, application.beers)
    saveBeers(application.beers)
    application = restartApplication(application)

def loadBeers(path="data/beers.json"):
    """ Loads beer data from JSON file passed as arg """
    try:
        with open(path, "r") as beerfile:
            beerdata = json.load(beerfile)
        return [Beer(k, v) for (k,v) in beerdata.items()]
    except json.JSONDecodeError:
        return list()

def saveBeers(beers, path="data/beers.json"):
    """ Saves beer data to JSON file passed as arg """
    JSONstrings = [json.dumps(beer, cls=BeerEncoder) for beer in beers]
    loadedJSON = [json.loads(s) for s in JSONstrings]
    saveJSON = dict()
    for beer in filter(lambda b: b["name"] != '', loadedJSON):
        name = beer["name"]
        del(beer["name"])
        saveJSON[name] = beer
    json.dump(saveJSON, open(path, "w"), indent=2)

def loadTheme(themename, path="data/themes.json"):
    """ Loads the theme needed for the application to be styled """
    global THEMES
    THEMES = json.load(open(path, "r")) # Load all themes
    try:
        return THEMES[themename] # Return theme
    except KeyError: # If theme doesn't exist
        return None

def restartApplication(application):
    """ Destroys the TKinter Window, deletes the instance of Application class, and creates a new one from scratch """
    try: application.app.destroy()
    except: application.app.quit()
    application = setupWindow()
    return application

def submitSettings(settings):
    """ Applies settings to the Application object, and saves them to the pickle """
    global application
    persist = {option:setting.get() for (option,setting) in settings.items()}
    with open("data/persist.pk", "wb") as pickle_file:
        pickle.dump(persist, pickle_file)
    application = restartApplication(application)

def settingsPopup():
    """ Manages the popup window shown when the user clicks 'Preferences' button """
    # Add more settings here
    settings_popup = PopupWindow("Settings", minsize=(200, 200), resizable=True)
    settings = dict(
        THEME = StringVar(value=application.theme_name)
    )
    val_dict = {
        "THEME": list(sorted(THEMES))
    }
    Label(settings_popup.popup, text="").grid(row=0, column=0, columnspan=2)
    Separator(settings_popup.popup, orient=HORIZONTAL).grid(row=1, column=0, columnspan=2, sticky="ew")
    for (_row, (option, setting)) in enumerate(application.options.items()):
        Label(settings_popup.popup, text=f"{option.lower().capitalize()}: ").grid(row=_row+1, column=0)
        OptionMenu(settings_popup.popup, settings[option], *val_dict[option]).grid(row=_row+1, column=1)
    submit = Button(settings_popup.popup, text="Submit", command=lambda: submitSettings(settings))
    submit.grid(row=len(application.options)+1, column=0, columnspan=2, sticky="s")


def setupWindow():
    """ Sets up GUI with widgets """
    # Create basic window layout
    root = Application(title="Crown Brewery Recipe Manager")

    menubar = Menu(root.app)
    root.app.config(menu=menubar)
    # Add more menu options here
    if SYSTEM == 'Darwin': # If the application is running on a Mac
        root.app.createcommand('tk::mac::ShowPreferences', settingsPopup)
    elif SYSTEM == 'Windows': # If the application is running on a Windows machine
        pass
    elif SYSTEM == 'Linux': # If the application is running on a Linux machine
        pass

    titleframe = root.gridWidget(root.app, Frame, "frame_titleframe", row=0, column=0, highlightbackground="black",
        highlightthickness=1, height=65,
        gkws={"sticky":"new"})
    bodyframe = root.gridWidget(root.app, Frame, "frame_bodyframe", row=1, column=0, highlightthickness=1,
        gkws={"sticky":"sew"})
    createframe = root.gridWidget(bodyframe, LabelFrame, "frame_createframe", row=0, column=0, text="Create New Recipe",
        highlightbackground="black", highlightthickness=1,
        gkws={"sticky":"new"})
    scrollcanvas = root.gridWidget(bodyframe, Canvas, "canvas_scroll", row=1, column=0,
        gkws={"sticky":"new"})
    viewframe = root.packWidget(scrollcanvas, LabelFrame, "frame_viewframe", text="View Recipes",
        highlightbackground="black", highlightthickness=1,
        pkws={"fill":"both"})

    # Space the "title", "create" and "view" frames correctly
    for i in range(root.rows): root.app.grid_rowconfigure(i, weight=i)
    for i in range(root.cols): root.app.grid_columnconfigure(i, weight=1)

    # Set up the "title" frame
    root.gridWidget(titleframe, Label, "label_title", row=0, column=0, text="Recipe Manager", font=("Helvetica", 18, "bold"),
        gkws={"sticky":"nsew"})
    root.gridWidget(titleframe, Label, "label_subtitle", row=1, column=0, text="by Christian A Loizou")

    # Set up the "create" frame
    newbeer = dict(
        type = StringVar(),
        srm = StringVar()
    )

    with open("data/beertypes.csv", "r") as typecsvfile:
        BEERTYPES = list(csv.reader(typecsvfile))[0]
    with open("data/srm.csv", "r") as srmcsvfile:
        SRMSCALE = list(csv.reader(srmcsvfile))[0]

    newbeer["type"].set("Choose a type")
    newbeer["srm"].set("Choose an SRM value")

    root.gridWidget(createframe, Label, "label_beername", row=0, column=0, text="Enter beer name: ")
    name = root.gridWidget(createframe, Entry, "entry_beername", row=0, column=1)
    root.gridWidget(createframe, Label, "label_beertype", row=0, column=2, text="Enter beer type: ")
    type = root.gridWidget(createframe, OptionMenu, "entry_beertype", newbeer["type"], *BEERTYPES, row=0, column=3)

    root.gridWidget(createframe, Label, "label_servingtemp", row=1, column=0, text="Enter serving temp. (ºC): ")
    servingtemp = root.gridWidget(createframe, Entry, "entry_servingtemp", row=1, column=1, width=10)
    root.gridWidget(createframe, Label, "label_abv", row=1, column=2, text="Enter ABV (%): ")
    abv = root.gridWidget(createframe, Entry, "entry_abv", row=1, column=3, width=10)

    root.gridWidget(createframe, Label, "label_ibu", row=2, column=0, text="Enter IBU value: ")
    ibu = root.gridWidget(createframe, Entry, "entry_ibu", row=2, column=1, width=10)
    root.gridWidget(createframe, Label, "label_srm", row=2, column=2, text="Enter SRM value: ")
    srm = root.gridWidget(createframe, OptionMenu, "entry_srm", newbeer["srm"], *SRMSCALE, row=2, column=3)

    root.gridWidget(createframe, Label, "label_gravity", row=3, column=0, text="Enter gravity: ")
    gravity = root.gridWidget(createframe, Entry, "entry_gravity", row=3, column=1, width=10)

    submit = root.gridWidget(createframe, Button, "button_submitcreation", row=3, column=2, text="Create",
        command=lambda: createBeer(root, [name, newbeer["type"], servingtemp, abv, ibu, newbeer["srm"], gravity]),
        gkws={"columnspan":2, "sticky":"ew", "padx":5, "pady":5})

    # Set up the "view" frame
    ROWSIZE = 3
    for beernum, beer in enumerate(root.beers):
        buttonname = "button_"+beer._getformattedname()
        _row, _col = 1 + (beernum//ROWSIZE), beernum%ROWSIZE
        root.gridWidget(viewframe, Button, buttonname, row=_row, column=_col, text=beer.name,
        command=beer.displayInformation, gkws={"ipadx":35, "ipady":15, "padx":5, "pady":5})

    # Add an empty error message label for use later
    root.gridWidget(root.app, Label, "label_errormessage", row=2, column=0, text="", fg="red",
        gkws={"columnspan":5, "sticky":"s"})

    return root

if __name__ == "__main__":
    SYSTEM = platform.system() # Gets the system of the machine running the application (ie. MAC, WINDOWS or LINUX)
    application = setupWindow()
    application.app.mainloop()
