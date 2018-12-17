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
    def __init__(self, cnt, imageName, port, P=0.1, pretext='\t\tFEUService'):
        self._cnt = cnt
        self._port = port
        self._P = P
        self._adr = ('127.0.0.1', self._port)
        self._pool = ThreadPool(processes=1)
        self._ret = None
        
        self.pretext=pretext
        self.imageName = imageName
        self.pr("Inited")
        self.state = 'idl'

        
    def pr(self, txt):
        print("{}::{}".format(self.pretext, txt))
        
    def isBusy(self):
        return self.state != 'idl'
        
    def get(self):
        if self._ret is None:
            return None
        if not self._ret.ready():
            return None
        self.state = 'idl'
        return self._ret.get()
    
    def exe(self, x, m, blocking=False):
        if self._ret != None:
            if not self._ret.ready():
                return None
        if blocking:
            ret = self._exe(x, m)
            self._ret = None
            return ret 
        self.state = 'poo'
        self._ret = self._pool.apply_async(self._exe, (x, m))
        return self._ret
        
    def _exe(self, x, m):
        if self.state != 'idl' and self.state != 'poo':
            return None
        self.state = 'req'
        self.pr('EXE:requesting')
        req = cc.packet('EXE', cc.FER_pack(x, m))
        sock = socket.socket()
        sock.connect(self._adr)
        sock.send(req)
        resp = cc.getPacket(sock)
        sock.close()
        val = cc.bytes2Dict(resp[1])
        self.pr('EXE:got resp')
        self.state == 'rep'
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
