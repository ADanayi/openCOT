#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Dec 16 11:00:01 2018

@author: adanayi
"""

#%%
import socket
import common_convs as cc

adr = ('127.0.0.1', 2020)

#%%
sock = socket.socket()
sock.connect(adr)

x = {'name':'abolfazl', 'fname':'danayi', 'age':21}
m = {'USERID':'ADanayi'}
req = cc.packet('EXE', cc.FER_pack(x, m))
sock.send(req)
resp = cc.getPacket(sock)
print(resp)

sock.close()

#%%
sock = socket.socket()
sock.connect(adr)

req = cc.packet('FIN', b'')
sock.send(req)
resp = cc.getPacket(sock)
print(resp)

sock.close()
