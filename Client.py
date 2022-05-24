import os
import threading
#import tkinter
from tkinter import *
import tkinter.scrolledtext
from tkinter import Button, Entry, Frame, Tk, simpledialog
import paho.mqtt.client as mqtt

RoomName = "ProBoScIdE"
global DummyVar
DummyVar = "\n"
nickname = "FRANK"

HOST = "mqtt.eclipseprojects.io"
PORT = 1883
conn_status = True  # Flag stato connessione

# Definizione della funzione on_connect
def on_connection(client, user_data, flag, rc):
    global conn_status  # global variable in this file
    status_decoder = {  # swtich case in python style using dictionary
        0: "Successfully Connected",
        1: "Connection refused: Incorrect Protocol Version",
        2: "Connection refused: Invalid Client Identifier",
        3: "Connection refused: Server Unavailable",
        4: "Connection refused: Bad Username/Password",
        5: "Connection refused: Not Authorized",
    }

    # Connessione al Broker avvenuta con successo
    if rc == 0:
        #client.flag = True
        #conn_status = True
        #flag
        # Creazione simpledialog per nickname e validazione password
        nickname = login()
        """
        msg1 = tkinter.Tk()
        msg1.withdraw()

        nickname = simpledialog.askstring("Nickname", "Please choose a nickname", parent=msg1)
        if nickname == 'admin':
            password = simpledialog.askstring("Password", "Insert a password", parent=msg1, show='*')
            if password == '1234':
                pass
            else:
                print("error")"""
        """
        conn_text = ("System>>{} has connected to broker with status: \n\t{}.\n".format(nickname, 
                                                                                        status_decoder.get(rc)))
        
        ChatFill.configure(state="normal")
        ChatFill.insert(INSERT, str(conn_text))
        client.subscribe(RoomName)
        conn_status = True
        ChatFill.configure(state="disabled")"""
    else:
        #client.flag = False
        conn_status = False
        #flag= False

def login():
    msg = tkinter.Tk()
    msg.withdraw()

    nickname = simpledialog.askstring("Nickname", "Please choose a nickname", parent=msg)
    if nickname == 'admin':
        password = simpledialog.askstring("Password", "Insert a password", parent=msg, show='*')
        if password == '1234':
            pass
        else:
            print("error")
        
        return nickname


def on_message(client, user_data, msg):
    # check incoming payload to prevent owner echo text
    global incoming_massage
    incoming_massage = msg.payload.decode("utf-8")
    if incoming_massage.find(DummyVar) >= 0:
        pass
    else:
        ChatFill.configure(state="normal")
        ChatFill.insert(INSERT, str(incoming_massage))
        ChatFill.configure(state="disabled")

def send_message():
    global DummyVar
    get_message = str(MassageFill.get("1.0", END))
    if get_message == " ":
        pass
    else:
        send_message = "\n{}>>\t{}".format(nickname, get_message)
        DummyVar = send_message
        ChatFill.configure(state="normal")
        client.publish(RoomName, send_message)
        ChatFill.insert(INSERT, str(send_message))
        MassageFill.delete("1.0", END)
        ChatFill.configure(state="disabled")

# GUI
window = Tk()
window.title("Chat room")
window.minsize(600, 400)
window.resizable(0, 0)

Frame1 = LabelFrame(window, text="Chat Window", width=600, height=300)
Frame1.place(y=0, x=0)
Frame2 = LabelFrame(window, text="Enter Massage", width=600, height=100)
Frame2.place(y=300, x=0)

YChatFillScroll = Scrollbar(Frame1)
YChatFillScroll.place(y=0, x=550, height=250)
XChatFillScroll = Scrollbar(Frame1, orient=HORIZONTAL)
XChatFillScroll.place(y=251, x=0, width=550)

ChatFill = Text(Frame1, yscrollcommand=YChatFillScroll.set, xscrollcommand=XChatFillScroll.set)
ChatFill.place(x=0, y=0, width=550, height=250)
ChatFill.configure(state="disabled")
YChatFillScroll.config(command=ChatFill.yview)
XChatFillScroll.config(command=ChatFill.xview)

MassageFill = Text(Frame2, font=("", 16))
MassageFill.place(x=0, y=0, width=475, height=75)

SendButton = Button(Frame2, text="Send", command=send_message)  # send_message
SendButton.place(x=480, y=0, width=100, height=75)

# Istanzio l'oggetto    
client = mqtt.Client()

# Specifico i metodi
client.on_connect = on_connection
client.on_message = on_message

# Connessione al Broker
client.connect(HOST, PORT)

# Esecuzione del client
client.loop_start()

# Esecuzione della GUI
window.mainloop()

try:
    while conn_status:
        print("Va tutto bene")
except:
    print("Error1")

