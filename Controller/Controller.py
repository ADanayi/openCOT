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
    def __init__(self, sPort, asPort, clerkPort='4040'):
        print('Starting the Controller')
        
        self._port_clerk = clerkPort
        self._sPort = sPort
        self._asPort = asPort
        
        pp('Loading ports table: ')
        self._portsTable = self._loadPortsTable()
        pr('Done')
        
        print('Creating Gates: ')
        self.gates = {}
        for imageName in self._portsTable.keys():
            q_port = self._portsTable[imageName][0]
            qPrime_port = self._portsTable[imageName][1]
            print('\t{}: ({}, {})'.format(imageName, q_port, qPrime_port))
            self.gates['imageName'] = Gate.Gate(q_port, qPrime_port, imageName)
        print('Created all gates.')
        
        pp('Starting auto-scaling servers')
        self.autoScaler = AutoScaler.AutoScaler(sPort, asPort)
        pr('done')
        
        pp('Starting Clerk Server: ')
        self.proc_clerk = mp.Process(target=self._wrk_clerkServer, daemon=True)
        self.proc_clerk.start()
        pr('done')
                    
    ######################### AutoScaler
    ######
    def _loadASTable(self):
        Table = {
                    'cluster1': {'echofuncbusy':(4, 0.1), 'echofunc':(2, 0.25)},
                    'cluster2': {'echofuncbusy':(1, 0.1), 'echofunc':(3, 0.25)}
                }
        ret = [Table]
        return ret
    
    def _loadClustersTable(self):
        pass
    
    ######################### Ports Tables
    ######
    def _loadPortsTable(self):
        ret = {'echofunc':(8000, 9000), 'echofuncbusy':(8001, 9001)}
        return ret
    
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
        elif msg == 'ports?':
            ret = {'msg':'ports', 'ports':self._getPortsTable()}
        elif msg == 'asPorts?':
            ret = {'msg':'asPorts', 'ports':(self._sPort, self._asPort)}
        else:
            ret = {'msg':'ERR'}
        return ret


#%%
if __name__ == '__main__':
    cont = Controller(4030, 4031, 4040)
