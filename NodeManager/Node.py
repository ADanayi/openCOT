#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 18 17:02:17 2018

@author: root
"""

import NodeService
import NodeFER
import zmq
import multiprocessing as mp

class Node:
    def __init__(self, cluster, nid, controllerIP, controllerClerkPort=4040, pretext='Node'):
        self._nid = nid
        self._cIP = controllerIP
        self._cluster = cluster
        self._controllerClerkPort = controllerClerkPort
        self.nodeS = NodeService.NodeService()
        self.pretext = pretext
        if self._boot():
            self.pr('[Boot completed]')
        else:
            self.pr('[Boot error]')
        
    def pr(self, txt):
        print('{}::{}'.format(self.pretext, txt))
        
    def _boot(self):
        self.pr('Booting up node')
        self.pr('\tChecking clerk server:')
        rep = self.__req_clerk({'msg':'chk'})
        if rep['msg'] != 'OK':
            self.pr('\t\t[Error]')
            return False
        self.pr('\t\t[OK]')
        
        self.pr('\tGetting Ports from clerk server:')
        ret = self._req_clerk_ports()
        if ret is None:
            self.pr('\t\t[Error]')
            return False
        else:
            self.pr('\t\t[OK]')
        self._portsTable = ret
        
        self.pr('\tGetting asPorts from clerk server:')
        ret = self._req_clerk_asPorts()
        if ret is None:
            self.pr('\t\t[Error]')
            return False
        else:
            self.pr('\t\t[OK]')
        self._sPort = ret[0]
        self._asPort = ret[1]
        
        return True
    
    def _req_clerk_asPorts(self):
        ret = self.__req_clerk({'msg':'asPorts?'})
        if ret['msg'] != 'asPorts':
            return None
        ports = ret['ports']
        return ports
    
    def _req_clerk_ports(self):
        ret = self.__req_clerk({'msg':'ports?'})
        if ret['msg'] != 'ports':
            return None
        ports = ret['ports']
        return ports
        
    def __req_clerk(self, req):
        context = zmq.Context()
        self.pr("\tConnecting to Clerk server...")
        socket = context.socket(zmq.REQ)
        socket.connect("tcp://{}:{}".format(self._cIP, self._controllerClerkPort))
        socket.send_json(req)
        resp = socket.recv_json()
        return resp

#%%
node = Node('cluster1', 0, '127.0.0.1', 4040)
