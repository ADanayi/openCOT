#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 18 17:06:18 2018

@author: root
"""

import zmq
import multiprocessing as mp
import Gate
import AutoScaler

def pp(txt):
    print(txt, end='')
    
def pr(txt):
    print('[{}]'.format(txt))
    
class Controller:
    def __init__(self, sPort, clerkPort='4040', initPath=''):
        print('Starting the Controller')
        
        self._port_clerk = clerkPort
        self._sPort = sPort
        
        pp('Loading initial configurations...')
        self._loadInits(initPath)
        pr('Done')
        
        print('Creating Gates: ')
        self.gates = {}
        for imageName in self._portsTable.keys():
            q_port = self._portsTable[imageName][0]
            qPrime_port = self._portsTable[imageName][1]
            print('\t{}: ({}, {})'.format(imageName, q_port, qPrime_port))
            self.gates['imageName'] = Gate.Gate(q_port, qPrime_port, imageName)
        print('Created all gates.')
        
        pr('Starting auto-scaling servers: ')
        self.autoScaler = AutoScaler.AutoScaler(self._sPort, self._asPortsTable)
        pr('done')
        
        pp('Starting Clerk server: ')
        self.proc_clerk = mp.Process(target=self._wrk_clerkServer, daemon=True)
        self.proc_clerk.start()
        pr('done')
        
        pp('Initial scaling...')
        self.autoScaler.setNewAutoScaling(self._initialASTable)
        pr('done')
                  
        
    def _loadInits(self, path=''):
        with open('init_clusters.oct', 'r') as file:
            lines = file.readlines()
        clustersInfo = {}
        for l in lines:
            ll = l.split('\n')[0]
            ls = ll.split(':')            
            if len(ls) > 2:
                clustersInfo[ls[0]] = {'NodesNumer':int(ls[1]), 'ASPort':int(ls[2])}
        with open('init_Ports.oct', 'r') as file:
            lines = file.readlines()
        self._portsTable = {}
        for l in lines:
            ll = l.split('\n')[0]
            ls = ll.split('\:')
            if len(ls) > 2:
                self._portsTable[ls[0]] = (int(ls[1]), int(ls[2]))
                
        self._asPortsTable = {}
        for cluster in clustersInfo.keys():
            self._asPortsTable[cluster] = clustersInfo[cluster]['ASPort']
            
        self._clustersInfo = clustersInfo
        
        with open('init_ASTable.oct', 'r') as file:
            lines = file.readlines()
        self._initialASTable = {}
        for l in lines:
            ll = l.split('\n')[0]
            if len(ll) == 0:
                continue
            ls = ll.split(':')            
            cluster = ls[0]
            N = int(ls[1])
            _Table = ls[2]
            Table = {}
            #{'echofuncbusy':(5, 0.1), 'echofunc':(2, 0.25)}
            tt = _Table.split(';')
            for t in tt:
                if len(t) == 0:
                    continue
                a = t.split(',')
                Table[a[0]] = (int(a[1]), float(a[2]))
                
            if not cluster in self._initialASTable.keys():
                self._initialASTable[cluster] = []
            self._initialASTable[cluster].append((N, Table))
                
    ######################### AutoScaler
    
    ######################### Ports Tables
    ######
    ######    
    def _getPortsTable(self):
        return self._portsTable
    
    
    ######################### Clerk Server
    def _wrk_clerkServer(self):
        context = zmq.Context()
        socket = context.socket(zmq.REP)
        socket.bind("tcp://*:%s" % self._port_clerk)
        while True:
            req = socket.recv_json()
            print('\tClerk: Got request: {}'.format(req))
            result = self.__clerkServer(req)
            print('\tClerk: Sending response: {}'.format(result))
            socket.send_json(result)
            
    def __clerkServer(self, req):
        msg = req['msg']
        if msg == 'chk':
            ret = {'msg':'OK'}
        elif msg == 'portsTable?':
            ret = {'msg':'portsTable', 'portsTable':self._getPortsTable()}
        elif msg == 'asPortsTable?':
            ret = {'msg':'asPortsTable', 'sPort':self._sPort, 'asPortsTable':self._asPortsTable}
        else:
            ret = {'msg':'ERR'}
        return ret


#%%
if __name__ == '__main__':
    cont = Controller(4041, 4040)
