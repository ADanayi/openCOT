#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Dec 16 22:36:10 2018

@author: adanayi
"""

import time
import zmq
import docker
import socket

import sys
sys.path.append('./../FEU')
import common_convs as cc

class Node:
    def __init__(self, pretext='\tNode'):
        self._currentSupportedFuncs = []
        self._currentFEUs = {}
        self._client = docker.from_env()
        self.pretext = pretext
        self.cpu_period = int(10000)
        self.__poolAllowed = True
        self.pr("Initialized node")
        
    def pr(self, txt):
        print("{}::{}".format(self.pretext, txt))

    #% Node: Task scheduling functions
    def invoke_polling(self, imageName, x, m):
        while self.__poolAllowed:
            for tup in self._currentFEUs[imageName]:
                if tup[1] == True:
                    tup[1] = False
                    req = cc.packet('EXE', cc.FER_pack(x, m))
                    sock = socket.socket()
                    sock.connect(('127.0.0.1', tup[0]))
                    sock.send(req)
                    resp = cc.getPacket(sock)
                    sock.close()
                    val = cc.bytes2Dict(resp[1])
                    tup[1] = True
                    return val
                    
            
    #% Node: FEU lifecycle functions
    def _newFEU(self, name, imageName, port, P=0.1, iport=2020): # Returns -1 on error, number of imageName FEUs otherwise
        self.pr('Crated FEU instance of {} for port {}, named: {}'.format(imageName, port, name))
        quota = int(P*self.cpu_period)
        cnt = self._client.containers.run(imageName, detach=True, ports={'{}/tcp'.format(iport):'{}'.format(port)}, cpu_shares=int(P*1024), name=name,
                                                                        cpu_period = self.cpu_period, cpu_quota = quota)
        
        if cnt != -1:
            if not imageName in self._currentSupportedFuncs:
                self._currentSupportedFuncs.append(imageName)
                self._currentFEUs[imageName] = []
            self._currentFEUs[imageName].append([port, True, cnt])
            return len(self._currentFEUs[imageName])
        else:
            return -1
        
    def _delFEU(self, cnt, force=True):
        cnt.remove(force=True)
        self.pr('Deleted FEU instane: {}'.format(cnt.name))
        
    def _list(self):
        return self._client.containers.list()
        
    def _delAll(self, force=True):
        self.pr('Deleting all FEUs')
        for cnt in self._list():
            self._delFEU(cnt, force)

#%%
node = Node()
node._delAll()
cnt1 = node._newFEU('cont', 'echofuncbusy', 8005, 0.2)
cnt2 = node._newFEU('cont2', 'echofuncbusy', 8006, 0.5)
cnt2 = node._newFEU('cont3', 'echofuncbusy', 8006, 0.5)
cnt2 = node._newFEU('cont3', 'echofuncbusy', 8006, 0.5)

#%%
while True:
    x = {'name':'abolfazl', 'fname':'danayi', 'age':24}
    m = {'USERID':'ADanayi'}
    output = node.invoke_polling('echofuncbusy', x, m)
    print("Invoked and got: {}".format(output))

#%%
node._delFEU(cnt1)
node._delFEU(cnt2)
