#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 18 17:02:17 2018

@author: root
"""

import NodeService
import zmq
import threading as thd

class Node:
    def __init__(self, cluster, nid, controllerIP, controllerClerkPort=4040, pretext='Node'):
        self._nid = nid
        self._cIP = controllerIP
        self._cluster = cluster
        self._icIndex = None
        self._asCtr = None
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
        self.pr('PortsTable={}'.format(self._portsTable))
        
        self.pr('\tGetting asPorts from clerk server:')
        ret = self._req_clerk_asPorts()
        if ret is None:
            self.pr('\t\t[Error]')
            return False
        else:
            self.pr('\t\t[OK]')
        self._sPort = ret[0]
        self._asPort = ret[1]
        self.pr('sPort={}, asPort={}'.format(self._sPort, self._asPort))
        
        self.pr('\tSubscribing for AS events')
        self.sub = thd.Thread(target=self._subScriber_wrk, args=(self._sPort,))
        self.sub.start()
        
        self.pr('\tRequesting for initial AS')
        iAS = self._req_AS_as()
        if iAS is None:
            self.pr('Server does not need scaling this node.')
        else:
            self.nodeS.allocateTable(iAS['table'])
            self._icIndex = iAS['icIndex']
            
        return True
    
    ######################################## AS
    def __beforeAS(self):
        pass
    
    def _req_AS_as(self):
        ret = self.__req_AS({'msg':'as?'})
        if ret['msg'] == 'as.':
            if ret['icIndex'] == -1:
                return None
            AS = {'icIndex': ret['icIndex'], 'table': ret['table']}
        else:
            AS = None
        return AS
        
    def __req_AS(self, req):
        context = zmq.Context()
        self.pr("\tConnecting to As server...")
        socket = context.socket(zmq.REQ)
        socket.connect("tcp://{}:{}".format(self._cIP, self._asPort))
        socket.send_json(req)
        resp = socket.recv_json()
        return resp
    
    def _subScriber_wrk(self, sPort):
        self.pr('Sub:Starting on port:{}'.format(sPort))
        context = zmq.Context()
        socket = context.socket(zmq.SUB)
        socket.connect ("tcp://localhost:%s" % sPort)
        self.pr('Sub:Joint')
        while True:
            ev = socket.recv()
            self.pr('Sub:Got {}'.format(ev))
    
    ######################################## Clerk
    def _req_clerk_asPorts(self):
        ret = self.__req_clerk({'msg':'asPortsTable?'})
        if ret['msg'] != 'asPortsTable':
            return None
        sPort = ret['sPort']
        asPorts = ret['asPortsTable']
        if not self._cluster in asPorts.keys():
            print('\nTHIS CLUSTER IS NOT SUBMITTED TO THE CONTROLLER.\n')
            return None
        return (sPort, asPorts[self._cluster])
    
    def _req_clerk_ports(self):
        ret = self.__req_clerk({'msg':'portsTable?'})
        if ret['msg'] != 'portsTable':
            return None
        ports = ret['portsTable']
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
