from claptrap.claptrap import Zero
import tkinter as tk
from smuggler_lib import *
from tkinter import font
from GUI.MKCODES import *
import base64,pyqrcode
from io import BytesIO
import requests
import threading
from queue import Queue
import time,string

class ChatMan(tk.Frame):
    def quit(self):
        self.end()
        self.master.destroy()


    def process_updates(self):
        while self.queue.qsize():
            try:
                msg=self.queue.get(0)

                uncode=base64.b64decode(msg.json().get('msg_latest').get('msg'))
                bio=BytesIO(uncode)
                data=decodeOneQrCode.remote(bio)
                qr=ray.get(data)[0]
                print(qr.data)
                text=qr.data.decode('utf-8')
                msg='[{address}{date}]{data}'.format(**msg.json().get('msg_latest'),data=text)
                self.rx_text(msg)
            except Exception as e:
                raise e
                self.quit()

    row=0
    column=0

    def updateW_H(self,widget):
        self.update()
        self.MYHEIGHT+=widget.winfo_height()
    def updateW_W(self,widget):
        self.update()
        self.MYWIDTH+=widget.winfo_width()

    def __init__(self,master,queue,endApplication,*args,**kwargs):
        super().__init__(master=master,*args,**kwargs)
        self.queue=queue
        self.current_font=font.nametofont('TkDefaultFont')
        self.font_attr=self.current_font.actual()
        self.MYHEIGHT=0
        self.MYWIDTH=0
        self.end=endApplication

        def mkEntryFIELDS():
            #since the next two widgets are on the same column do not update Height
            self.recieving_entry_field=tk.Text(master,height=self.font_attr.get('size')*5,width=self.font_attr.get('size')*10)
            self.recieving_entry_field.grid(row=self.row,column=self.column)
            self.recieving_entry_field.config(state="disabled")
            self.updateW_H(self.recieving_entry_field)
            self.MYWIDTH=self.recieving_entry_field.winfo_width()

            self.transmitting_entry_field=tk.Text(master,height=self.font_attr.get('size')*5,width=self.font_attr.get('size')*10)
            self.transmitting_entry_field.grid(row=self.row,column=self.column+1)
            self.transmitting_entry_field.bind('<Escape>',lambda x:self.send_text())
            self.updateW_W(self.transmitting_entry_field)
            self.row+=1

            self.send_button=tk.Button(text="send",command=self.send_text)
            self.send_button.grid(row=self.row,column=self.column+1)
            self.updateW_H(self.send_button)

        def mkSERVER():
            self.row+=1
            self.HOST=None
            self.HOST_LABEL=None
            self.HOST_BUTTON=None
            self.HOST,self.HOST_LABEL,self.HOST_BUTTON=MkCode.setDefaultsEntryBrowse(
            master,
            self.HOST,
            "127.0.0.1",
            self.column,
            self.row,
            "Server",
            self.HOST_LABEL,
            self.HOST_BUTTON,
            lambda: print('cleared field host'),
            "X",
            return_BUTTON=True,
            return_LABEL=True,
            )
            self.updateW_H(self.HOST)
            self.updateW_W(self.HOST_BUTTON)

            self.GEO="{width}x{height}".format(height=self.MYHEIGHT+20,width=self.MYWIDTH+20)

            self.row+=1
            self.PORT=None
            self.PORT_LABEL=None
            self.PORT_BUTTON=None
            self.PORT,self.PORT_LABEL,self.PORT_BUTTON=MkCode.setDefaultsEntryBrowse(
            master,
            self.PORT,
            "8000",
            self.column,
            self.row,
            "Port",
            self.PORT_LABEL,
            self.PORT_BUTTON,
            lambda: print('cleared field PORT'),
            "X",
            return_BUTTON=True,
            return_LABEL=True,
            )
            self.updateW_H(self.PORT)
            self.updateW_W(self.PORT_BUTTON)

        mkEntryFIELDS()
        mkSERVER()
        self.row+=1
        self.console = tk.Button(master, text='Done', command=self.end)
        self.console.grid(row=self.row,column=self.column+1)

        self.updateW_H(self.console)
        self.GEO="{width}x{height}".format(height=self.MYHEIGHT+20,width=self.MYWIDTH+20)

        print(self.GEO)
        self.master.geometry(self.GEO)


    def send_msg(self,msg,scale=10):
        host=self.HOST.get()
        port=self.PORT.get()
        bio=BytesIO(b'')
        qr=pyqrcode.QRCode(msg)
        imgd=qr.png(bio,scale=scale)
        bio.seek(0)
        b64encoded=base64.b64encode(bio.read())
        response=requests.post("http://{host}:{port}/msgr/".format(host=host,port=port),headers={'Content-Type':'application/json'},json={'msg':b64encoded.decode('utf-8')})
        print(response.json())
        return response.json()

    def rx_text(self,msg):
        print(msg)
        self.recieving_entry_field.config(state="normal")
        self.recieving_entry_field.delete('0.0',tk.END)
        self.recieving_entry_field.insert(self.recieving_entry_field.index("end"),msg)
        self.recieving_entry_field.config(state="disabled")

    def send_text(self):
        print(self.transmitting_entry_field.get(1.0,tk.END),self.font_attr)
        msg=self.transmitting_entry_field.get(1.0,tk.END)
        self.send_msg(msg)
        msg="[TRANSMITTING]{msg}".format(msg=msg)
        self.recieving_entry_field.config(state="normal")
        self.recieving_entry_field.insert(self.recieving_entry_field.index("end"),msg)
        self.recieving_entry_field.config(state="disabled")
        self.transmitting_entry_field.delete('0.0',tk.END)

class ThreadedClient:
    def __init__(self,master):
        self.master=master
        self.master.protocol("WM_DELETE_WINDOW",self.endApplication)
        self.queue=Queue()

        self.gui=ChatMan(master=master,queue=self.queue,endApplication=self.endApplication)
        self.running=1
        self.thread1=threading.Thread(target=self.poller,args=(self.gui.HOST.get(),self.gui.PORT.get()))
        self.thread1.start()
        self.periodicCall()

    def periodicCall(self):
        self.gui.process_updates()
        if not self.running:
            import sys
            sys.exit(1)
        self.master.after(100, self.periodicCall)

    def poller(self,host,port):
        while self.running:
            response=requests.get("http://{host}:{port}/msgr".format(host=host,port=port))
            print(response)
            self.queue.put(response)
            time.sleep(3)

    def endApplication(self):
        self.running = 0


if __name__ == "__main__":
    window=tk.Tk()
    window.geometry("800x500")
    boxed=ThreadedClient(master=window)
    window.mainloop()
