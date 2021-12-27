#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys,threading,socket,os,base64,select,json,random,time

words = [
    'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
    'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
    '1', '2', '3', '4', '5', '6', '7', '8', '9', '0'
]

class chatServer:
    def __init__(self) -> None:
        self.users = []
    def run(self):
        server = socket.socket()
        server.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        server.bind(('0.0.0.0',5007))
        server.listen(200)
        while True:
            try:
                s = server.accept()[0]
                th = threading.Thread(target=self.recv,args=(s,))
                th.daemon = True
                th.start()
            except KeyboardInterrupt:sys.exit(0)
            except RuntimeError:
                s.sendall("ChatRoom is full now!\nPlease try later.")
                s.close()
    def randomKey(self):
        key = ""
        for i in range(random.randint(1,15)):key += words[random.randint(0,len(words)-1)]
        return key
    def recv(self,client):
        while True:
            try:
                bdata = client.recv(1024)
            except:
                for user in self.users:
                    if client in user:self.users.remove(user)
                    break
                client.close()
                break
            try:
                data = bdata.decode()
                text = dec(data.split(" ")[1],data.split(" ")[0])
            except:continue
            print(str(text))
            if text.startswith("Login:"):
                client.sendall(str.encode("Logined"))
                key = self.randomKey()
                username = text.split(":")[1]
                self.send(key+" "+enc('{"user":"*console*","text":"'+username+' is online!"}',key))
                self.users.append((client,username))
                continue
            try:
                objs = json.loads(text)
                sendtext = dec(objs['text'],data.split(" ")[0])
                fromUser = objs['user']
            except:continue
            if sendtext.startswith("/"):
                returns = self.commands(sendtext)
                if returns != "":
                    key = self.randomKey()
                    text = '{"user":"*console*","text":"%s"}'%enc(returns,key)
                    client.sendall(str.encode(key+" "+enc(text,key)))
                    continue
            self.send(data)
        #key = "ajdsckjn"
        #client.sendall(str.encode(key+' '+enc("Received data:"+text,key)))
        
    def send(self,data):
        for user in self.users:
            while True:
                try:
                    th = threading.Thread(target=self.thsend,args=(user,data))
                    th.daemon = True
                    th.start()
                    break
                except RuntimeError:continue
    def thsend(self,user,data):
        try:
            sended = user[0].send(data.encode())
            if not sended:self.users.remove(user)
        except:
            try:self.users.remove(user)
            except:pass
    def commands(self,cmd):
        
        if cmd == "/online":
            usernames = ""
            for user in self.users:
                usernames += user[1] +", "
            return ('onlines('+str(len(self.users))+'): '+usernames)
        elif cmd == "/ping":
            return 'Ping:'
        else: return ""

def enc(text,key):
    code = ""
    keylen = len(key)
    count = 0
    for c in text:
        if count >= keylen:count = 0
        try:code += chr((ord(c)+(ord(key[count])))-[keylen,15][keylen>15])
        except TypeError as e:
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
        text += chr((ord(c)+[keylen,15][keylen>15])-(ord(key[count])))
        count += 1
    return text

chatServer().run()
