import socket
import common_convs as cc

class Core:
    def __init__(self, func, port=2020, IP='0.0.0.0', pretext="\tFEU"):
        self.pretext=pretext
        self.adr = (IP, port)
        self.open()
        self.alive = False
        self.func = func
        self.pr("Initialized FEU Core server")
    
    def pr(self, txt):
        print("{}::{}".format(self.pretext, txt))
    
    def join(self):
        self.alive = True
        self.pr("Joint")
        while self.alive:
            self.pr("Listening")
            con, client_address = self.sock.accept()
            self.pr("Got connection from: {}".format(client_address))
            
            req = cc.getPacket(con)
            if req[0] == 'FIN':
                self.alive = False
                self.pr("Got the FIN request")
                resp = cc.packet('FIN', b'')
            elif req[0] == 'EXE':
                resp = cc.packet('RET', self.exec(req[1]))
            
            con.send(resp)
            con.close()
            self.pr("Closed connection of: {}".format(client_address))
        self.alive = False
        self.close()
        
    def exec(self, data):
        FER = cc.FER_depack(data)
        
        self.pr("EXEC::executing function")
        ret = self.func(FER)
        self.pr("EXEC::function retuned")
        if not isinstance(ret, dict):
            self.pr("EXEC::Warning. Returned value is not a dictionary")
            ret = {}
        return cc.dict2Bytes(ret)
    
    def isAlive(self):
        return self.alive
        
    def open(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(self.adr)
        self.sock.listen()
        self.pr("Opened the main Socket on {}".format(self.adr))
        
    def close(self):
        self.sock.close()
        self.pr("Closed the main Socket")
