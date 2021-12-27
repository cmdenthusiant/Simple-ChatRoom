import sys,threading,socket,os,base64,select,json,random

words = [
    'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
    'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
    '1', '2', '3', '4', '5', '6', '7', '8', '9', '0'
]

class chatServer:
    def __init__(self) -> None:
        self.conns = []
        self.users = []
    def run(self):
        server = socket.socket()
        server.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        server.bind(('0.0.0.0',5007))
        server.setblocking(0)
        server.listen(200)
        self.conns.append(server)
        while True:
            try:rb,_,er = select.select(self.conns,[],self.conns,1)
            except KeyboardInterrupt:return
            except:continue
            for s in rb:
                if s is server:
                    try:
                        client,addr = s.accept()
                        client.setblocking(0)
                        self.conns.append(client)
                    except:pass
                else:
                    try:
                        th = threading.Thread(target=self.recv,args=(s,))
                        th.daemon = True
                        th.start()
                    except:pass
            for s in er:
                s.close()
    def randomKey(self):
        key = ""
        for i in range(random.randint(1,15)):key += words[random.randint(0,len(words)-1)]
        return key
    def recv(self,client):
        try:
            bdata = client.recv(1024)
            data = bdata.decode()
            addr = client.getsockname()
            text = dec(data.split(" ")[1],data.split(" ")[0])
        except:return
        print(str(text))
        if text.startswith("Login:"):
            while True:
                ranPort = random.randint(1,60000)
                for i in self.users:
                    if i == (addr[0],ranPort):continue
                break
            client.sendall(str.encode("Logined,port:"+str(ranPort)))
            key = self.randomKey()
            self.send(key+" "+enc('{"user":"*console*","text":"'+text.split(":")[1]+' is online!"}',key))
            self.users.append((addr[0],ranPort))
            self.conns.remove(client)
            client.close()
            return
        try:
            objs = json.loads(text)
            sendtext = objs['text']
            fromUser = objs['user']
        except:return
        self.conns.remove(client)
        client.close()
        self.send(data)
        #key = "ajdsckjn"
        #client.sendall(str.encode(key+' '+enc("Received data:"+text,key)))
        
    def send(self,data):
        for user in self.users:
            try:
                s = socket.socket()
                s.settimeout(1)
                s.connect((user))
                sended = s.send(data.encode())
                if not sended:self.users.remove(user)
                s.close()
            except:
                self.users.remove(user)
                s.close()

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

chatServer().run()