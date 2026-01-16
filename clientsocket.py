import socket
import threading
from protocol import protocol as mp
import json
import datetime
import time
import sys

HOST = "127.0.0.1"
PORT = "8500"

if sys.argv[1] == "prod":
    HOST = "62.60.178.229"


def receive_messages():
    while True:
        message = mp.recv_information(socket)
        print(message)
        if message[0] == "JSN":
            data = json.loads(message[1])
            if data["sender_username"] == req_user:
                print(data["message"])
            else:
                print(f"New Message from {data["sender_username"]}")
        elif message[0] == "TXT":
            if message[1] == "Ok Exit":
                break


def get_history(socket):
    all_chats = mp.recv_information(socket)[1]
    return json.loads(all_chats)

def get_users_in_string(history):
    all_users = ""
    user_number = 1
    for username in history:
        all_users += f"{user_number}. {username}\n"
        user_number += 1
    return all_users

def get_history_of_choosen_user(username, history):
    history = history[username]
    message_ids = []
    for b in history:
        message_ids.append(b["message_id"])
    print(message_ids)
    mp.send_jason(socket, message_ids)
    message = ""
    for a in history:
        if a["is_sent"] == True:
            message += f"                                  {a["message"]}\n"
        else:
            message += f"{a["message"]}\n"
    return message


socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket.connect((HOST, PORT))
for a in range(1, 4):
    try:
        file = open("cookies.json", "r", encoding="utf-8")
        cookies = json.load(file)
        file.close()
        username = cookies["username"]
        password = cookies["password"]
        date = cookies["date"].split("-")
        date = datetime.date(int(date[0]), int(date[1]), int(date[2]))
        date_today = datetime.date.today()
        delta = date_today - date
        last_time_login = delta.days
        if last_time_login > -3:
            raise Exception()
    except:
        username = input("What is your username?")
        password = input("What is your password?")

    mp.send_text(socket, username)
    mp.send_text(socket, password)
    accepted = mp.recv_information(socket)[1]
    if accepted == "0":
        if a == 3:
            raise ConnectionError("Authentication Failed")
    else:
        file = open("cookies.json", "w", encoding="utf-8")
        dict_to_write = {"username": username, "password": password, "date": str(datetime.date.today())}
        json.dump(dict_to_write, file, ensure_ascii=False, indent=4)
        file.close()
        break

history = get_history(socket)

while True:
    users = get_users_in_string(history)
    print(users)
    while True:
        req_user = input("With who do you want to chat not today?")
        if req_user in history or req_user == "exit":
            break
    if req_user == "exit":
        dicti = {"message": message_sent, "receiver_username": req_user}
        mp.send_jason(socket, dicti)
        break
    history_of_choosen_user = get_history_of_choosen_user(req_user, history)
    print(history_of_choosen_user)


    thread = threading.Thread(target=receive_messages)
    thread.start()

    while True:
        message_sent = input("")
        if message_sent == "exit":
            break
        else:
            dicti = {"message": message_sent, "receiver_username": req_user}
            mp.send_jason(socket, dicti)

time.sleep(0.5)
socket.close()
