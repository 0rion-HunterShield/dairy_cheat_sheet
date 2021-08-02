import tkinter as tk
from threading import Thread
import sys,os
import queue,time

class GuiClient(tk.Frame):
    def quit(self):
        self.endApp()
        self.master.destroy()
        
    def process_updates(self):
        while self.queue.qsize():
            try:
                print('process_updates()')
                self.rcvd=self.queue.get()
                if type(self.rcvd) == type(dict()):
                    if 'time' in self.rcvd.keys():
                        self.label['text']=self.rcvd.get('time')
                print(self.rcvd)
                self.queue.task_done()
            except Exception as e:
                print(e)
                raise e
                self.quit()

    def __init__(self,master,queue,endApp,*args,**kwargs):
        self.master=master
        self.queue=queue
        self.endApp=endApp
        self.setup_base()

    def setup_base(self):
        self.label=tk.Label(master=self.master)
        self.label['text']='clock'
        self.label.pack()

class ThreadedClient:
    def __init__(self,master):
        self.master=master
        self.queue=queue.Queue()
        self.master.protocol("WM_DELETE_WINDOW",self.endApp)
        self.gui=GuiClient(master=master,queue=self.queue,endApp=self.endApp)
        self.running=True

        self.thread=Thread(target=self.poller)
        self.thread.start()
        self.periodicCall()

    def periodicCall(self):
        self.gui.process_updates()
        if not self.running:
            sys.exit(1)
        self.master.after(100,self.periodicCall)

    def long_runners(self):
        self.queue.put(dict(time=time.ctime()))
        
    def poller(self):
        #do something after a period
        while self.running:
            time.sleep(0.1)
            self.long_runners()

    def endApp(self):
        self.running=False

if __name__ == "__main__":
    window=tk.Tk()
    window.geometry('400x400')
    framed=ThreadedClient(master=window)
    window.mainloop()
