from tkinter import *
from pushcraft_scraper import main

import datetime as dt

class MyWindow:
    def __init__(self, win):
        self.lbl1=Label(win, text='Subreddits (comma-separated)')
        self.lbl2=Label(win, text='Start Date (YYYY-mm-dd HH:MM:SS)')
        self.lbl3=Label(win, text='End Date (YYYY-mm-dd HH:MM:SS)')
        self.lbl4=Label(win, text='Query')
        self.lbl5=Label(win, text='Bucket Duration (hrs)')
        self.t1=Entry()
        self.t2=Entry()
        self.t3=Entry()
        self.t4=Entry()
        self.t5=Entry()

        self.lbl1.place(x=80, y=50)
        self.t1.place(x=350, y=50)
        self.lbl2.place(x=80, y=100)
        self.t2.place(x=350, y=100)
        self.lbl3.place(x=80, y=150)
        self.t3.place(x=350, y=150)
        self.lbl4.place(x=80, y=200)
        self.t4.place(x=350, y=200)
        self.lbl5.place(x=80, y=250)
        self.t5.place(x=350, y=250)

        self.b1=Button(win, text='Run', command=self.run)
        self.b1.place(x=250, y=300)


    def run(self):
        subs = [x.strip() for x in self.t1.get().split(',')]
        start = dt.datetime.strptime(self.t2.get(), "%Y-%m-%d %H:%M:%S")
        end = dt.datetime.strptime(self.t3.get(), "%Y-%m-%d %H:%M:%S")
        query = self.t4.get()
        bucketDur = self.t5.get()
        if (bucketDur == ""):
            bucketDur = None
        else:
            bucketDur = dt.timedelta(hours = int(bucketDur))

        for sub in subs:
            main(sub, start, end, query, bucketDur)


window=Tk()
mywin=MyWindow(window)
window.title('Reddit Ticker Scraper')
window.geometry("600x400+10+10")
window.mainloop()
