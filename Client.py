import os
import sys
import argon2
import string
import random as rd
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

# Definizione del PasswordHasher
argon2Hasher = argon2.PasswordHasher(
    time_cost=3,            # numero di iterazioni
    memory_cost=64 * 1024,  # 64mb
    parallelism=1,          # thread paralleli da utilizzare
    hash_len=32,            # dimensione della chiave derivata
    salt_len=16             # dimensione del salt casuale generato in byte
)

# Definizione funzione write_onscreen
def write_onscreen(message):
    ChatFill.configure(state="normal")
    ChatFill.insert(INSERT, str(message))
    ChatFill.configure(state="disabled")

# Definizione della funzione on_connect
def on_connect(client, userdata, flags, rc):
    global nickname
    flag = True

    status_decoder = {
        0: "Connessione stabilita",
        1: "Connessione rifiutata: Versione protocollo errata",
        2: "Connessione rifiutata: Identificatore client non valido",
        3: "Connessione rifiutata: Server non disponibile",
        4: "Connection refused: Bad Username/Password",
        5: "Connessione rifiutata: Non autorizzato",
    }

    # Creazione instanza Tk()
    msg = tkinter.Tk()
    msg.withdraw()

    # Viene chiesto di inserire un nickname
    nickname = simpledialog.askstring(
        "Nickname", "Scegli un nickname", parent=msg)

    # Controllo della validità del nickname
    if nickname is None or bool(nickname) == False:
        flag = False
        disconnection("no_nick")
    else:
        # Controllo che il nick non sia bannato
        with open('./bans.txt', 'r') as f:
            bans = f.readlines()
            
        # Se il nome viene trovato, l'utente viene disconnesso
        if nickname+'\n' in bans:
            flag = False
            disconnection("ban")

        # Controllo che non ci sia già lo stesso nickname
        with open('./online.txt', 'r') as f:
            online = f.readlines()
        # Se il nome viene trovato, l'utente viene disconnesso
        if nickname+'\n' in online:
            flag = False
            disconnection("taken")
        
        # Viene chiesta la password
        if nickname == 'admin':
            password = simpledialog.askstring(
                "Password", "Inserisci la password", parent=msg, show='*')
            try:
                # Si verifica la correttezza della password
                argon2Hasher.verify(pwd, password)
            except:
                # Se la password è sbagliata, l'utente viene disconnesso
                flag = False
                disconnection("pass_error")

        if flag == True:
            conn_text = ("System>> {} è connesso al broker con lo stato: \n\t{}.\n".format(nickname,
                                                                                            status_decoder.get(rc)))
            # Iscrizione del Client al topic del Broker
            client.subscribe(ROOM)

            write_onscreen(conn_text)
            # Il nickname viene inserito nella lista degli utenti online
            with open('./online.txt', 'a') as f:
                f.write(f'{nickname}\n')

# Definizione della funzione on_message
def on_message(client, user_data, msg):
    global dummy
    global nickname
    decrypted_message = cipher.decrypt(msg.payload)
    message = decrypted_message.decode("utf-8")

    # Verifica della presenza ed esecuzione del comando "kick"
    if message.find('/kick') >= 0 and msg.payload != dummy:
        user = message.partition('/kick ')[2]
        if user.strip('\n') == nickname:
            # L'utente viene viene disconnesso
            disconnection("kick")
    # Verifica della presenza ed esecuzione del comando "ban"
    elif message.find('/ban') >= 0 and msg.payload != dummy:
        user = message.partition('/ban ')[2]
        if user.strip('\n') == nickname:
            
            # Il nickname viene inserito nella lista dei ban
            with open('./bans.txt', 'a') as f:
                f.write(f'{user}\n')

            # L'utente viene viene disconnesso
            disconnection("ban")
    # Se il messaggio si trova già nella chat, non viene scritto una seconda volta
    elif msg.payload == dummy:
        pass
    else:
        write_onscreen(message)

# Definizione della funzione send_message
def send_message():
    global dummy
    global nickname

    # Il testo viene acquisito dalla casella di testo
    get_message = MassageFill.get("1.0", END)
    get_message.encode('utf-8')

    # Controllo che il testo non contenga solo spaziature o ritorni a capo
    if get_message == '\n' or get_message == '\t\n' or get_message == '\n\n': 
        pass
    else:
        # Si controlla l'utilizzo errato del comando "kick" da parte di utenti non admin
        if get_message.find('/kick') >= 0 and nickname != "admin":
            message = "\nSystem>> You are not the chat admin!\n"
            write_onscreen(message)
            MassageFill.delete("1.0", END)
        # Si controlla l'utilizzo errato del comando "ban" da parte di utenti non admin
        elif get_message.find('/ban') >= 0 and nickname != "admin":
            message = "\nSystem>> You are not the chat admin!\n"
            write_onscreen(message)
            MassageFill.delete("1.0", END)
        else:
            # Il messaggio viene cifrato e inviato nella chat
            message1 = message2 = "{}: {}".format(nickname, get_message)
            message1 = bytes(message1, encoding='utf8')
            encrypted_message = cipher.encrypt(message1) 
            out_message = encrypted_message.decode()
            dummy = encrypted_message

            client.publish(ROOM, out_message)

            write_onscreen(message2)
            MassageFill.delete("1.0", END)

# Definizione della funzione disconnection
def disconnection(flag):
    send_all = True
    search = False

    # In base al motivo della disconnessione viene visualizzato un specifico 
    if flag == "no_nick":
        message = "Non hai impostato un nickname!\n\tChiudi la chat e connettiti di nuovo.\n"
    elif flag == "pass_error":
        send_all = False
        message = nickname + " hai sbagliato password!\n\tChiudi la chat e connettiti di nuovo.\n"
    elif flag == "taken":
        send_all = False
        message = nickname + \
            " è nickname già in uso!\n\tChiudi la chat e connettiti con un nuovo nickname\n"
    elif flag == "kick":
        message = nickname + " è stato rimosso dall'admin della chat!\n\n"
    elif flag == "ban":
        message = nickname + " è stato bannato dall'admin della chat!\n\n"

        # Controllo se il nickname sia stato già bannato
        with open('./bans.txt', 'r') as f:
            bans = f.readlines()

        if nickname+'\n' in bans:
            search = True
    else:
        message = "Si è verificato un problema e sei stato disconnesso\n\n"

    send_message = m = "\n{}>> {}".format("System", message)

    # Controllo se il messaggio deve essere inviato a tutti i partecipanti della chat
    if send_all == True:
        if search == False:
            # Il messaggio viene cifrato
            send_message = bytes(send_message, encoding='utf8')
            encrypted_message = cipher.encrypt(send_message)
            out_message = encrypted_message.decode()

            # Il messaggio viene pubblicato 
            client.publish(ROOM, out_message)
        else:
            pass

        # Si controlla se la chat è stata chiusa per volere dell'utente
        if flag == "exit":
            # Disconnessione dal Broker
            client.disconnect()
            # Si ferma l'esecuzione del Client
            client.loop_stop()

            # Viene cancellato l'utente che non è più online
            with open("./online.txt", 'r+') as input:
                with open("temp.txt", "w") as output:
                    # si itera su tutte le righe di "input"
                    for line in input:
                        # se il nickname corrisponde, non si scrive
                        if line.strip("\n") != nickname:
                            output.write(line)

            #Si sostituisce il file con il nome originale
            os.replace('temp.txt', 'online.txt')

            # Si ferma l'esecuzione del processo
            sys.exit(0)
        else:
            # Il messaggio viene visualizzato solo dall'utente disconnesso
            write_onscreen(m)

            # Disconnessione dal Broker
            client.disconnect()
            # Si ferma l'esecuzione del Client
            client.loop_stop()
    else:
        # Il messaggio viene visualizzato solo dall'utente disconnesso
        write_onscreen(m)
        #MassageFill.delete("1.0", END)

        # Disconnessione dal Broker
        client.disconnect()
        # Si ferma l'esecuzione del Client
        client.loop_stop()

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
YChatFillScroll.place(y=0, x=570, height=270)

ChatFill = Text(Frame1, yscrollcommand=YChatFillScroll.set) # xscrollcommand=XChatFillScroll.set
#ChatFill = tkinter.scrolledtext.ScrolledText(window)
ChatFill.place(x=0, y=0, width=570, height=270)
#ChatFill.pack(padx=20, pady=5)
ChatFill.configure(state="disabled")
YChatFillScroll.config(command=ChatFill.yview)

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
window.protocol("WM_DELETE_WINDOW", disconnection("exit"))
