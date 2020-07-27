from tkinter import *
from pushcraft_scraper import comment_module

import datetime as dt

class MyWindow:
    def __init__(self, win):
        self.lbl1=Label(win, text='Thread URL')
        self.t1=Entry()


        self.lbl1.place(x=80, y=50)
        self.t1.place(x=200, y=50)

        self.b1=Button(win, text='Run', command=self.run)
        self.b1.place(x=250, y=100)


    def run(self):
        url = self.t1.get()
        comment_module.comment_module(url)


window=Tk()
mywin=MyWindow(window)
window.title('Reddit Ticker Scraper (Comments)')
window.geometry("500x300+10+10")
window.mainloop()
