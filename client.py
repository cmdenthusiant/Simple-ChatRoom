#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys,os,socket,base64,threading,time,random,json,time

words = [
    'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
    'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
    '1', '2', '3', '4', '5', '6', '7', '8', '9', '0'
]

serverIp = "59.149.49.218"

class chatClient:
    def __init__(self) -> None:
        self.username = ""
        self.command = False
        self.PingStartTime = 0
    def run(self):
        client = self.login()
        th = threading.Thread(target=self.recv,args=(client,))
        th.daemon = True
        th.start()
        while True:
            try:
                text = input("")
                if text == "":continue
                if text == "/help":
                    self.help()
                    continue
                if text.startswith("/"):
                    self.send(client,text,True)
                    continue
                self.send(client,text)
            except KeyboardInterrupt:sys.exit(0)
    def login(self):
        s = socket.socket()
        print("Connecting to Server...")
        try:
            s.connect((serverIp,5007))
        except:
            print("Server offline")
            time.sleep(2)
            sys.exit(0)
        print("Connected to ChatServer!")
        while True:
            username = input("Enter your username:")
            if username == "*console*":
                print("This is not a valid name!")
                continue
            if len(username) > 10:
                print("Username is too long!")
                continue
            if username != "":
                self.username = username
                break
        key = self.randomKey()
        try:sended = s.send(str.encode(key+" "+enc("Login:"+username,key)))
        except Exception as e:
            print("Something went wrong: "+e)
            time.sleep(2)
            sys.exit(0)
        if not sended:
            print("Something went wrong...")
            time.sleep(2)
            sys.exit(0)
        data = s.recv(1024)
        if data.decode() == "Logined":
            print("[*console*]Your are in the Chat now! Type /help for commands\n")
            return s
        else:
            print("Something went wrong...")
            time.sleep(2)
            sys.exit(0)
    def randomKey(self):
        key = ""
        for i in range(random.randint(1,15)):key += words[random.randint(0,len(words)-1)]
        return key
    def recv(self,client):
        while True:
            try:
                bdata = client.recv(1024)
                data = bdata.decode()
                text = dec(data.split(" ")[1],data.split(" ")[0])
                objs = json.loads(text)
                sendtext = objs['text']
                fromUser = objs['user']
                if self.command:
                    if sendtext == "Ping:":
                        sendtext += str(round((time.time()-self.PingStartTime)*1000))+"ms"
                    self.command = False
            except:
                continue
            print("["+fromUser+"]: "+sendtext)
            continue
    def send(self,client,text,command=False):
        if command:
            self.command = True
            if text == "/ping":
                startTime = time.time()
                self.PingStartTime = startTime
        key = self.randomKey()
        try:sended = client.send(str.encode(key+" "+enc('{"user":"'+self.username+'","text":"'+text+'"}', key)))
        except:
            print("Disconnected!\nRetrying...")
            self.run()
            return
        if not sended:
            print("Something went wrong...")
            time.sleep(2)
            sys.exit(0)
        return
    def help(self):
        print("="*50+"\n/online :get online members\n/ping :get ping(ms)\n"+"="*50)

def enc(text,key):
    code = ""
    keylen = len(key)
    count = 0
    for c in text:
        if count >= keylen:count = 0
        for i in str(c):
            try:code += chr(ord(str(i))^(ord(key[count])-[keylen,15][keylen>15]))
            except Exception as e:
                print(c,e.args)
                return ""
        count += 1
    c = base64.b64encode(code.encode()).decode()
    return c

def dec(bcode, key):
    code = base64.b64decode(bcode.encode()).decode()
    text = ""
    keylen = len(key)
    count = 0
    for c in code:
        if count >= keylen:count = 0
        text += chr(ord(c)^(ord(key[count])-[keylen,15][keylen>15]))
        count += 1
    return text

chatClient().run()
