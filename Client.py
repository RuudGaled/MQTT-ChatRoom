import os
import string
import random as rd
import tkinter.scrolledtext
from tkinter import *
import tkinter.scrolledtext
from tkinter import simpledialog
from cryptography.fernet import Fernet
import paho.mqtt.client as mqtt

HOST = "mqtt.eclipseprojects.io"
PORT = 1883
ROOM = "provaChat"
global dummy
dummy = "\n"

#def reset():
#ret = client.publish(ROOM, "", 0, True)


def on_log(client, userdata, level, buf):
    print(buf)


def on_connect(client, userdata, flags, rc):
    global nickname

    status_decoder = {
        0: "Successfully Connected",
        1: "Connection refused: Incorrect Protocol Version",
        2: "Connection refused: Invalid Client Identifier",
        3: "Connection refused: Server Unavailable",
        4: "Connection refused: Bad Username/Password",
        5: "Connection refused: Not Authorized",
    }

    msg = tkinter.Tk()
    msg.withdraw()

    nickname = simpledialog.askstring(
        "Nickname", "Please choose a nickname", parent=msg)
    if nickname == 'admin':
        password = simpledialog.askstring(
            "Password", "Insert a password", parent=msg, show='*')
        if password == '1234':
            pass
        else:
            client.loop_stop()
            client.disconnect()

    conn_text = ("System>> {} has connected to broker with status: \n\t{}.\n".format(nickname,
                                                                                     status_decoder.get(rc)))

    client.subscribe(ROOM)
    ChatFill.configure(state="normal")
    ChatFill.insert(INSERT, str(conn_text))
    ChatFill.configure(state="disabled")


def on_message(client, user_data, msg):
    global dummy
    global nickname
    #messaggio = msg.payload.decode("utf-8")

    decrypted_message = cipher.decrypt(msg.payload)
    msg1 = decrypted_message.decode("utf-8")
    # messaggio == dummy: # FUNZIONA
    print(msg.payload)
    print(dummy)
    if msg.payload == dummy:  # msg1 == dummy:
        pass
    else:
        ChatFill.configure(state="normal")
        ChatFill.insert(INSERT, str(msg1))  # messaggio
        ChatFill.configure(state="disabled")

        if msg1.startswith('/kick'):  # messaggio
            user = msg1[6:]   # messaggio
            if user == nickname:

                message = nickname + " is disconnected"
                send_message = "\n{}>> {}".format("System ", message)
                client.publish(ROOM, send_message)
                ChatFill.configure(state="normal")

                ChatFill.insert(INSERT, str(send_message))
                MassageFill.delete("1.0", END)
                ChatFill.configure(state="disabled")

                client.loop_stop()
                client.disconnect()


def send_message():
    global dummy
    global nickname

    get_message = MassageFill.get("1.0", END)
    get_message.encode('utf-8')
    if get_message == '\n' or get_message == '\t\n' or get_message == '\n\n':  # FUNZIONA
        pass
    else:
        #send_message = "{}: {}".format(nickname, get_message) #\n
        #send_message = bytes(send_message, encoding='utf8')
        message1 = message2 = "{}: {}".format(nickname, get_message)
        #message1  = "{}: {}".format(nickname, get_message)
        #message2 = "{}: {}".format(nickname, get_message)
        message1 = bytes(message1, encoding='utf8')

        encrypted_message = cipher.encrypt(message1)  # send_message
        out_message = encrypted_message.decode()
        #print(encrypted_message)
        #dummy = send_message
        dummy = encrypted_message
        ChatFill.configure(state="normal")
        client.publish(ROOM, out_message)
        ChatFill.insert(INSERT, str(message2))  # send_message
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

ChatFill = Text(Frame1, yscrollcommand=YChatFillScroll.set,
                xscrollcommand=XChatFillScroll.set)
ChatFill.place(x=0, y=0, width=550, height=250)
ChatFill.configure(state="disabled")
YChatFillScroll.config(command=ChatFill.yview)
XChatFillScroll.config(command=ChatFill.xview)

MassageFill = Text(Frame2, font=("", 16))
MassageFill.place(x=0, y=0, width=475, height=75)

SendButton = Button(Frame2, text="Send", command=send_message)  # send_message
SendButton.place(x=480, y=0, width=100, height=75)

client_id = 'Client-' + \
    ''.join(rd.choices(string.ascii_uppercase + string.digits, k=9))
client = mqtt.Client(client_id)

# Specifico i metodi
client.on_connect = on_connect
client.on_message = on_message
client.on_log = on_log

# Metodo per criptare i messaggi
#cipher_key = Fernet.generate_key()
cipher_key = b'WDrevvK8ZrPn8gmiNFjcOp2xovBr40TCwJlZOyI94IY='
cipher = Fernet(cipher_key)

# Connessione al Broker
client.connect(HOST, PORT)

# Esecuzione del client
client.loop_start()

# Esecuzione della GUI
window.mainloop()
#reset()
