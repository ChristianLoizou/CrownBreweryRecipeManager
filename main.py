import json
from collections import defaultdict
from tkinter import *
from tkinter.ttk import Separator, Scrollbar

COMPLEXWIDGETS = [OptionMenu]

class Beer:
    """ Beer object. Stores all data about custom beers, including name, recipe, ABV, gravity, etc..."""
    def __init__(self, name, jsondata):
        self.name, self.type = name, jsondata["type"]
        self.abv, self.gravity = jsondata["ABV"], jsondata["gravity"]
        self.ibu, self.srm = jsondata["IBU"], jsondata["SRM"]
        self.servingtemp = jsondata["servingtemp"]
        self.recipe = jsondata["recipe"]
        self.image = None

    def __repr__(self):
        return f"<Beer: {self.name}>"

    def __str__(self):
        return repr(self)

    def _getformattedname(self): return "".join([w.capitalize() for w in self.name.split()])

    def displayInformation(self):
        popup = Tk()
        popup.title(self.name)
        Label(popup, text=self.name, font=("Helvetica", 18, "bold")).grid(row=0, column=0, columnspan=2)
        Separator(popup, orient=HORIZONTAL).grid(row=1, column=0, columnspan=2, sticky="ew")
        datapairs = [("name", self.name), ("beer type", self.type), ("abv", self.abv), ("gravity", self.gravity),
                ("ibu", self.ibu), ("srm", self.srm)]
        for r in range(1, 7):
            t, d = datapairs[r-1]
            Label(popup, text=t.capitalize()).grid(row=r+1, column=0)
            Label(popup, text=d).grid(row=r+1, column=1)

class Application(Tk):
    """ Application object. Blueprint for the window shown to user, with custom methods to allow for easier adding of widgets"""
    def __init__(self, /, *, title, size="830x600+400+200", jsonpath="data/beers.json", iconpath="assets/icon.ico"):
        self.app = Tk()
        self.title, self.iconpath = title, iconpath
        self.rows, self.cols = 1, 1
        self.app.title(title)
        self.app.geometry(size)
        self.app.minsize(830, 600)
        self.items = defaultdict(None)
        self.beers = loadBeers(jsonpath)

    def __repr__(self):
        return f"<Application: (title={repr(self.title)}, children={len(self.app.children)}, ...)>"

    def __str__(self):
        return repr(self)

    def packWidget(self, master, widget_type, widget_name, *args, pkws=None, **kwargs):
        widget = widget_type(master, kwargs)
        if pkws: widget.pack(pkws)
        else: widget.pack()
        self.items[widget_name] = widget
        return widget

    def gridWidget(self, master, widget_type, widget_name, *args, row, column, gkws=None, **kwargs):
        if row > self.rows: self.rows = row
        if column > self.cols: self.cols = column
        if widget_type in COMPLEXWIDGETS: widget = widget_type(master, *args)
        else: widget = widget_type(master, kwargs)
        if gkws: widget.grid(row=row, column=column, **gkws)
        else: widget.grid(row=row, column=column)
        self.items[widget_name] = widget
        return widget

def createBeer(application, *args):
    # Create new beer and append it to 'application.beers'
    pass

def loadBeers(path="data/beers.json"):
    """ Loads beer data from JSON file passed as arg """
    with open(path, "r") as beerfile:
        beerdata = json.load(beerfile)
    return [Beer(k, v) for (k,v) in beerdata.items()]

def saveBeers(path, beers):
    """ Saves beer data to JSON file passed as arg """
    with open(path, "w") as beerfile:
        json.dump(beers, beerfile, indent=2)

def setupWindow():
    """ Sets up GUI with widgets """
    # Create basic window layout
    root = Application(title="Crown Brewery Recipe Manager")
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

    BEERTYPES = tuple(sorted(["IPA", "Golden Ale", "American IPA", "Bitter", "Stout"]))
    beername = StringVar()
    beertype = StringVar()
    beerservingtemp = DoubleVar()

    beertype.set("Choose a type")

    root.gridWidget(createframe, Label, "label_beername", row=0, column=0, text="Enter beer name: ")
    name = root.gridWidget(createframe, Entry, "entry_beername", beername, row=0, column=1)
    root.gridWidget(createframe, Label, "label_beertype", row=0, column=2, text="Enter beer type: ")
    type = root.gridWidget(createframe, OptionMenu, "entry_beertype", beertype, *BEERTYPES, row=0, column=3)
    root.gridWidget(createframe, Label, "label_servingtemp", row=1, column=0, text="Enter serving temp. (ºC): ")
    servingtemp = root.gridWidget(createframe, Entry, "entry_servingtemp", beerservingtemp, row=1, column=1, width=10)

    submit = root.gridWidget(createframe, Button, "button_submitcreation", row=3, column=0, text="Create",
        command=lambda: createBeer(root, beername, beertype, beerservingtemp),
        gkws={"columnspan":4, "sticky":"ew", "padx":5, "pady":5})

    # Set up the "view" frame
    ROWSIZE = 5
    for beernum, beer in enumerate(root.beers):
        buttonname = "button_"+beer._getformattedname()
        _row = 1 + (beernum//ROWSIZE)
        root.gridWidget(viewframe, Button, buttonname, row=_row, column=beernum%ROWSIZE, text=beer.name,
        command=beer.displayInformation, gkws={"ipadx":35, "ipady":15, "padx":5, "pady":5})
    return root

if __name__ == "__main__":
    application = setupWindow()
    # print(f"\n{application}\n")
    application.app.mainloop()
