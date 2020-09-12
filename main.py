import json
from collections import defaultdict
from tkinter import *
from tkinter.ttk import Separator

class Beer:

    def __init__(self, name, jsondata):
        self.name, self.type = name, jsondata["type"]
        self.abv, self.gravity = jsondata["ABV"], jsondata["gravity"]
        self.ibu, self.srm = jsondata["IBU"], jsondata["SRM"]
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

    def __init__(self, /, *, title, size="800x600+400+200", jsonpath="data/beers.json", iconpath="assets/icon.ico"):
        self.app = Tk()
        self.title, self.iconpath = title, iconpath
        self.rows, self.cols = 1, 1
        self.app.title(title)
        self.app.geometry(size)
        self.app.minsize(800, 600)
        self.items = defaultdict(None)
        self.beers = loadBeers(jsonpath)

    def __repr__(self):
        return f"<Application: (title={repr(self.title)}, children={len(self.app.children)}, ...)>"

    def __str__(self):
        return repr(self)

    def packLabelledFrame(self, master, frame_name, *args, pkws=None, **kwargs):
        frame = LabelFrame(master, kwargs)
        if pkws: frame.pack(pkws)
        else: frame.pack()
        self.items[frame_name] = frame
        return frame

    def gridFrame(self, master, frame_name, *args, row, column, gkws=None, **kwargs):
        if row > self.rows: self.rows = row
        if column > self.cols: self.cols = column
        frame = Frame(master, kwargs)
        if gkws: frame.grid(row=row, column=column, **gkws)
        else: frame.grid(row=row, column=column)
        self.items[frame_name] = frame
        return frame

    def gridLabel(self, master, label_name, *args, row, column, gkws=None, **kwargs):
        if row > self.rows: self.rows = row
        if column > self.cols: self.cols = column
        label = Label(master, kwargs)
        if gkws: label.grid(row=row, column=column, **gkws)
        else: label.grid(row=row, column=column)
        self.items[label_name] = label
        return label

    def gridButton(self, master, button_name, *args, row, column, gkws=None, **kwargs):
        if row > self.rows: self.rows = row
        if column > self.cols: self.cols = column
        button = Button(master, kwargs)
        if gkws: button.grid(row=row, column=column, **gkws)
        else: button.grid(row=row, column=column)
        self.items[button_name] = button
        return button

    def gridEntry(self, master, entry_name, *args, row, column, gkws=None, **kwargs):
        if row > self.rows: self.rows = row
        if column > self.cols: self.cols = column
        entry = Entry(master, kwargs)
        if gkws: entry.grid(row=row, column=column, **gkws)
        else: entry.grid(row=row, column=column)
        self.items[entry_name] = entry
        return entry

def loadBeers(path="data/beers.json"):
    with open(path, "r") as beerfile:
        beerdata = json.load(beerfile)
    return [Beer(k, v) for (k,v) in beerdata.items()]

def saveBeers(path, beers):
    with open(path, "w") as beerfile:
        json.dump(beers, beerfile, indent=2)

def setupWindow():
    # Create basic window layout
    root = Application(title="Crown Brewery Recipe Manager")
    titleframe = root.gridFrame(root.app, "frame_titleframe", row=0, column=0, highlightbackground="black", highlightthickness=1,
        height=65, gkws={"sticky":"new", "columnspan":3})
    bodyframe = root.gridFrame(root.app, "frame_bodyframe", row=1, column=0, highlightthickness=1,
        gkws={"sticky":"nsew", "columnspan":3})
    createframe = root.packLabelledFrame(bodyframe, "frame_createframe", text="Create New Recipe",
        highlightbackground="black", highlightthickness=1,
        pkws={"fill":"both"})
    viewframe = root.packLabelledFrame(bodyframe, "frame_viewframe", text="View Recipes",
        highlightbackground="black", highlightthickness=1,
        pkws={"fill":"both"})

    # Space the "title", "create" and "view" frames correctly
    for i in range(root.rows): root.app.grid_rowconfigure(i, weight=i)
    for i in range(root.cols): root.app.grid_columnconfigure(i, weight=1)

    # Set up the "title" frame
    root.gridLabel(titleframe, "label_title", row=0, column=0, text="Recipe Manager", font=("Helvetica", 18, "bold"),
        gkws={"sticky":"nsew"})
    root.gridLabel(titleframe, "label_subtitle", row=1, column=0, text="by Christian A Loizou")

    # Set up the "create" frame
    root.gridLabel(createframe, "label_entrytitle", row=0, column=0, text="Enter beer name: ")
    name = root.gridEntry(createframe, "entry_beername", row=0, column=1)
    root.gridLabel(createframe, "label_entrytitle", row=0, column=2, text="Enter beer type: ")
    type = root.gridEntry(createframe, "entry_beertype", row=0, column=3)

    # Set up the "view" frame
    for beernum, beer in enumerate(root.beers):
        buttonname = "button_"+beer._getformattedname()
        root.gridButton(viewframe, buttonname, row=1, column=beernum, text=beer.name, width=10, height=10,
            command=beer.displayInformation)
    return root


if __name__ == "__main__":
    application = setupWindow()
    # print("\n", application, "\n")
    application.app.mainloop()
