from collections import defaultdict
from tkinter import *

class Application(Tk):

    def __init__(self, /, *, title):
        self.app = Tk()
        self.title = title
        self.app.title(title)
        self.items = defaultdict(None)

    def __repr__(self):
        return f'<Application object: title={self.title}>'

    def __str__(self):
        return self.__repr__()

    def gridLabel(self, label_name, *args, text, row, column, **kwargs):
        label = Label(self.app, kwargs, text=text)
        label.grid(row=row, column=column)
        self.items[label_name] = label

def setupWindow():
    root = Application(title="Crown Brewery Recipe Manager")

    root.gridLabel('label_title', text="Recipe Manager", row=0, column=0, font=("Helvetica", 18, "bold"))
    root.gridLabel('label_subtitle', text="by Christian A Loizou", row=1, column=0)

    return root

if __name__ == '__main__':
    application = setupWindow()
    print(application.items)
    application.app.mainloop()
