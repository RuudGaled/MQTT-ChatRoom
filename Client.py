import os
import time 
import sys
import argon2
import string
import random as rd
import tkinter.scrolledtext
from tkinter import *
import tkinter.scrolledtext
from tkinter import simpledialog
from settings import cipher_key, pwd
from cryptography.fernet import Fernet
import paho.mqtt.client as mqtt

HOST = "mqtt.eclipseprojects.io"
PORT = 1883
ROOM = "provaChat"
global dummy
dummy = "\n"

argon2Hasher = argon2.PasswordHasher(
    time_cost=3,  # number of iterations
    memory_cost=64 * 1024,  # 64mb
    parallelism=1,  # how many parallel threads to use
    hash_len=32,  # the size of the derived key
    salt_len=16  # the size of the random generated salt in bytes
)

def write_onscreen(mess):
    ChatFill.configure(state="normal")
    ChatFill.insert(INSERT, str(mess))
    MassageFill.delete("1.0", END)
    ChatFill.configure(state="disabled")

# Definizione della funzione on_connect
def on_connect(client, userdata, flags, rc):
    global nickname
    flag = True

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
    
    # Controllo che il nick non sia bannato
    with open('./bans.txt', 'r') as f:
        bans = f.readlines()

    if nickname+'\n' in bans:
        flag = False
        disconnessione("ban")

    # Controllo che non ci sia già lo stesso nickname
    with open('./online.txt', 'r') as f:
        online = f.readlines()
    
    if nickname+'\n' in online:
        flag = False
        disconnessione("same")

    # Chiedo la password
    if nickname == 'admin':
        password = simpledialog.askstring(
            "Password", "Insert a password", parent=msg, show='*')
        try:
            argon2Hasher.verify(pwd, password)
        except:
            flag = False
            disconnessione("pass")

    if flag == True:
        conn_text = ("System>> {} has connected to broker with status: \n\t{}.\n".format(nickname,
                                                                                         status_decoder.get(rc)))

        client.subscribe(ROOM)
        write_onscreen(conn_text)
        with open('./online.txt', 'a') as f:
            f.write(f'{nickname}\n')

# Definizione della funzione on_message
def on_message(client, user_data, msg):
    global dummy
    global nickname

    decrypted_message = cipher.decrypt(msg.payload)
    msg1 = decrypted_message.decode("utf-8")

    if msg1.find('/kick') >= 0 and msg.payload != dummy:
        user = msg1.partition('/kick ')[2]
        if user.strip('\n') == nickname:
            disconnessione("kick")
    elif msg1.find('/ban') >= 0 and msg.payload != dummy:
        user = msg1.partition('/ban ')[2]
        if user.strip('\n') == nickname:
            
            with open('./bans.txt', 'a') as f:
                f.write(f'{user}\n')

            disconnessione("ban")
    elif msg.payload == dummy:
        pass
    else:
        write_onscreen(msg1)

def crittografia(send_message):
    send_message = bytes(send_message, encoding='utf8')
    encrypted_message = cipher.encrypt(send_message)
    out_message = encrypted_message.decode()
    client.publish(ROOM, out_message)

    return encrypted_message

# Definizione della funzione disconnessione
def disconnessione(causa):
    send_to_all = "True"
    search = False

    if causa == "pass":
        send_to_all = "False"
        message = nickname + " hai sbagliato password!\n\tChiudi la chat e connettiti di nuovo.\n"
    elif causa == "same":
        send_to_all = "False"
        message = nickname + \
            " è nickname già in uso!\n\tChiudi la chat e connettiti con un nuovo nickname\n"
    elif causa == "kick":
        message = nickname + " è stato rimosso dall'admin della chat!\n\n"
    elif causa == "ban":
        message = nickname + " è stato bannato dall'admin della chat!\n\n"
    else:
        message = nickname + " si è disconnesso\n\n"

    send_message = m = "\n{}>> {}".format("System", message)

    # Controllo che il nick non sia bannato
    with open('./bans.txt', 'r') as f:
        bans = f.readlines()

    if nickname+'\n' in bans:
        search = True

    if send_to_all == "True":
        if search == False:
            send_message = bytes(send_message, encoding='utf8')
            encrypted_message = cipher.encrypt(send_message)
            out_message = encrypted_message.decode()
            client.publish(ROOM, out_message)
        else:
            pass
            
        if causa == "exit":
            client.disconnect()
            client.loop_stop()

            with open("./online.txt", 'r+') as input:
                with open("temp.txt", "w") as output:
                    # iterate all lines from file
                    for line in input:
                        # if text matches then don't write it
                        if line.strip("\n") != nickname:
                            output.write(line)

            # replace file with original name
            os.replace('temp.txt', 'online.txt')

            os._exit(0)
        else:
            write_onscreen(m)

            client.disconnect()
            client.loop_stop()
    else:
        write_onscreen(m)
        MassageFill.delete("1.0", END)

        client.disconnect()
        client.loop_stop()

# Definizione della funzione send_message
def send_message():
    global dummy
    global nickname

    get_message = MassageFill.get("1.0", END)
    get_message.encode('utf-8')
    if get_message == '\n' or get_message == '\t\n' or get_message == '\n\n': 
        pass
    else:
        if get_message.find('/kick') >= 0 and nickname != "admin":
            message = "\nSystem>> You are not the chat admin!\n"
            write_onscreen(message)
            #MassageFill.delete("1.0", END)
        elif get_message.find('/ban') >= 0 and nickname != "admin":
            message = "\nSystem>> You are not the chat admin!\n"
            write_onscreen(message)
            #MassageFill.delete("1.0", END)
        else:
            message1 = message2 = "{}: {}".format(nickname, get_message)
            #message1 = bytes(message1, encoding='utf8')

            #encrypted_message = cipher.encrypt(message1) 
            #out_message = encrypted_message.decode()
            x = crittografia(message1)
            dummy = x
            #dummy = encrypted_message
            #client.publish(ROOM, out_message)
            write_onscreen(message2)
            #MassageFill.delete("1.0", END)

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
YChatFillScroll.place(y=0, x=570, height=250)
XChatFillScroll = Scrollbar(Frame1, orient=HORIZONTAL)
XChatFillScroll.place(y=251, x=0, width=570)

ChatFill = Text(Frame1, yscrollcommand=YChatFillScroll.set,
                xscrollcommand=XChatFillScroll.set)
#ChatFill = tkinter.scrolledtext.ScrolledText(window)
ChatFill.place(x=0, y=0, width=570, height=250)
#ChatFill.pack(padx=20, pady=5)
ChatFill.configure(state="disabled")
YChatFillScroll.config(command=ChatFill.yview)
XChatFillScroll.config(command=ChatFill.xview)

MassageFill = Text(Frame2, font=("Arial", 16))
MassageFill.place(x=0, y=0, width=475, height=75)

SendButton = Button(Frame2, text="Send", command=send_message)  
SendButton.place(x=480, y=0, width=100, height=75)

# Creazione id univoco per il Client
client_id = 'Client-' + \
    ''.join(rd.choices(string.ascii_uppercase + string.digits, k=9))
client = mqtt.Client(client_id)

# Specifico i metodi
client.on_connect = on_connect
client.on_message = on_message

# Metodo per cifrare i messaggi
cipher = Fernet(cipher_key)

# Connessione al Broker
client.connect(HOST, PORT)

# Esecuzione del client
client.loop_start()

# Esecuzione della GUI
window.mainloop()

# Chiusura della Chat
window.protocol("WM_DELETE_WINDOW", disconnessione("exit"))
