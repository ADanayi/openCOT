#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 17 09:33:48 2018

@author: adanayi
"""

from multiprocessing.pool import ThreadPool
import sys
sys.path.append('./../FEU')
import common_convs as cc
import socket

class FEUService:
    def __init__(self, name, cnt, imageName, port, P=0.1, pretext='\t\tFEUService'):
        self._cnt = cnt
        self._port = port
        self._P = P
        self._name = name
        self._adr = ('127.0.0.1', self._port)
        self._pool = ThreadPool(processes=1)
        self._ret = None
        
        self.pretext=pretext
        self.imageName = imageName
        self.pr("Inited")

    def pr(self, txt):
        print("{}::{}".format(self.pretext, txt))
        
    def isInvoked(self):
        if self._ret == None:
            return False
        return True

    def check(self):
        self._ret = None
        
    def exe(self, x, m):
        if self.isInvoked():
            return None
        self._ret = self._pool.apply_async(self.__exe, (x, m))
        return self._ret        
    
    def __exe(self, x, m):
        self.pr('EXE:requesting')
        req = cc.packet('EXE', cc.FER_pack(x, m))
        sock = socket.socket()
        sock.connect(self._adr)
        sock.send(req)
        resp = cc.getPacket(sock)
        sock.close()
        val = cc.bytes2Dict(resp[1])
        self.pr('EXE:got resp')
        return val
    
    def fin(self):
        req = cc.packet('FIN', b'0')
        sock = socket.socket()
        sock.connect(self._adr)
        sock.send(req)
        resp = cc.getPacket(sock)
        sock.close()
        self.pr('FIN done')
        return resp
