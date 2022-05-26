import os
import threading
import random as rd
import string
from time import time
#import tkinter
from tkinter import *
import tkinter.scrolledtext
from tkinter import Button, Entry, Frame, Tk, simpledialog
from numpy import append
import paho.mqtt.client as mqtt

RoomName = "ProBoScIdE"
global DummyVar
DummyVar = "\n"
# nickname = "FRANK"
#nickname = ""

"""nicknames = []
clients = []"""


HOST = "mqtt.eclipseprojects.io"  # mqtt.eclipseprojects.io  broker.hivemq.com
PORT = 1883
conn_status = True  # Flag stato connessione

# Definizione della funzione on_connect
def on_connection(client, user_data, flag, rc):
    global conn_status  # global variable in this file
    global nickname
    

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
        #conn_status = True
        client.connected_flag = True
        

        # Creazione simpledialog per nickname e validazione password
        nickname = login()
        
        """nicknames.append(nickname)
        clients.append(client_id)
        print(clients + " 1")"""
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
        
        conn_text = ("System>>{} has connected to broker with status: \n\t{}.\n".format(nickname, 
                                                                                        status_decoder.get(rc)))
        
        write_onscreen(conn_text)
        """ChatFill.configure(state="normal")
        ChatFill.insert(INSERT, str(conn_text))
        client.subscribe(RoomName)
        conn_status = True
        ChatFill.configure(state="disabled")"""
    else:
        client.connected_flag = False
        #conn_status = False

def login():
    msg = tkinter.Tk()
    msg.withdraw()

    nickname = simpledialog.askstring("Nickname", "Please choose a nickname", parent=msg)
    if nickname == 'admin':
        password = simpledialog.askstring("Password", "Insert a password", parent=msg, show='*')
        if password == '1234':
            pass
        else:
            # messaggio di errore
            message = "Password sbagliata!"
            write_onscreen(message)
            #client.connected_flag = False
            #on_disconnect(client)
        
    return nickname

def on_disconnect(client):
    #global conn_status 
    #conn_status = False
    client.connected_flag = False
    print("Error1")
    #window.destroy()
    client.loop_stop()
    #window.destroy()
    os._exit(0)

def write_onscreen(message):
    ChatFill.configure(state="normal")
    ChatFill.insert(INSERT, str(message))
    ChatFill.configure(state="disabled")

def on_message(client, user_data, msg):
    # check incoming payload to prevent owner echo text
    global incoming_massage
    incoming_massage = msg.payload.decode("utf-8")
    if incoming_massage.find(DummyVar) >= 0:
        pass
    else:
        """ChatFill.configure(state="normal")
        ChatFill.insert(INSERT, str(incoming_massage))
        ChatFill.configure(state="disabled")"""
        write_onscreen(incoming_massage)

def send_message():
    global DummyVar
    global nickname



    get_message = str(MassageFill.get("1.0", END))
    get_message = str(MassageFill.get("1.0", END))
    if get_message == " ":
        pass
    else:
        send_message = "\n{}:\t{}".format(nickname, get_message)
        DummyVar = send_message
        client.publish(RoomName, send_message)
        write_onscreen(send_message)
        MassageFill.delete("1.0", END)
    """if nicknames[clients.index(client_id)] == 'admin':
        if get_message.startswith('/kick'):
            #{get_message[len(nickname)+2+6:]} == 'kick'
            write_onscreen("funziona")
            name_to_kick = get_message[5:]
            write_onscreen(name_to_kick)
            kick_user(name_to_kick)
        else:
            write_onscreen("Non hai il permesso")"""
    
    
    

# Definizione funzione kick_user
"""def kick_user(name):
    if name in nicknames:
        #print(nicknames)
        name_index = nicknames.index(name)
        client_to_kick = clients[name_index]
        clients.remove(client_to_kick)
        print(clients)
        nicknames.remove(name)
        print(nicknames)"""
        #broadcast(f'{name} was kicked by an admin!\n'.encode('utf-8'))

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

# Creazione flag per la connessione
mqtt.Client.connected_flag = False

# Creazione id
#client_id = 'Client-' + ''.join(rd.choices(string.ascii_uppercase + string.digits, k=9))

# Istanzio l'oggetto    
client = mqtt.Client()

# Specifico i metodi
client.on_connect = on_connection
client.on_message = on_message
client.on_disconnect = on_disconnect

# Connessione al Broker
client.connect(HOST, PORT)

# Esecuzione del client
client.loop_start()

# Esecuzione della GUI
window.mainloop()

window.protocol("WM_DELETE_WINDOW", on_disconnect(client))


#try:
    #while client.connected_flag:
        #print("Va tutto bene")
        # time.sleep(1)
        #client.connect(HOST, PORT)
#except:
    #print("Error finale")
    #client.loop_stop()
    #window.destroy()
    #os._exit(0)
    #on_disconnect(client)
    #window.protocol("WM_DELETE_WINDOW", on_disconnect(client))
