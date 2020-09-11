from collections import defaultdict
from tkinter import *

class Application(Tk):

    def __init__(self, /, *, title, size='800x600+400+200'):
        self.app = Tk()
        self.title = title
        self.rows, self.cols = 1, 1
        self.app.title(title)
        self.app.geometry(size)
        self.app.minsize(800, 600)
        self.items = defaultdict(None)

    def __repr__(self):
        return f'<Application object: (title={repr(self.title)}, children={len(self.app.children)}, ...)>'

    def __str__(self):
        return self.__repr__()

    def packLabelledFrame(self, master, frame_name, *args, gkws=None, **kwargs):
        frame = LabelFrame(master, kwargs)
        if gkws: frame.pack(gkws)
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

    def gridButton(self, button_name, text, *args, row, column, gkws=None, **kwargs):
        if row > self.rows: self.rows = row
        if column > self.cols: self.cols = column
        button = Button(self.app, *kwargs, text=text)
        if gkws: button.grid(row=row, column=column, **gkws)
        else: button.grid(row=row, column=column)
        self.items[button_name] = button
        return button

def setupWindow():
    root = Application(title="Crown Brewery Recipe Manager")
    titleframe = root.gridFrame(root.app, 'frame_titleframe', row=0, column=0, highlightbackground='black', highlightthickness=1,
        height=65, gkws={'sticky':'new', 'columnspan':3})
    bodyframe = root.gridFrame(root.app, 'frame_bodyframe', row=1, column=0,
        gkws={'sticky':'nsew', 'columnspan':3})
    createframe = root.packLabelledFrame(bodyframe, 'frame_createframe', text='Create New Recipe',
        highlightbackground='black', highlightthickness=1,
        gkws={'fill':'both'})
    viewframe = root.packLabelledFrame(bodyframe, 'frame_viewframe', text='View Recipes',
        highlightbackground='black', highlightthickness=1,
        gkws={'fill':'both'})

    root.gridLabel(titleframe, 'label_title', row=0, column=0, text="Recipe Manager", font=("Helvetica", 18, "bold"),
        gkws={'sticky':'nsew'})
    root.gridLabel(titleframe, 'label_subtitle', row=1, column=0, text="by Christian A Loizou")
    
    for c in range(1, 4):
        for frame in (createframe, viewframe):
            root.gridLabel(frame, 'label_placeholder', row=0, column=c, text=' ')
    for i in range(root.rows): root.app.grid_rowconfigure(i, weight=i)
    for i in range(root.cols): root.app.grid_columnconfigure(i, weight=i)

    return root

if __name__ == '__main__':
    application = setupWindow()
    print('\n', application, '\n')
    application.app.mainloop()
