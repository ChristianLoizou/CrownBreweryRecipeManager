import tkinter as tk

def setup():
    root = tk.Tk()
    root.title("Crown Brewery Recipe Maker")
    return root

if __name__ == '__main__':
    application = setup()
    application.mainloop()
