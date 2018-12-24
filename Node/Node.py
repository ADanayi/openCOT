#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 18 17:02:17 2018

@author: root
"""

import NodeService
import zmq
import threading as thd
import NodeFER
import time
import os

import sys
sys.path.append('Deployer/')
import Deployer

class Node:
    def __init__(self, cluster, nid, controllerIP, controllerClerkPort=4040, pretext='Node'):
        self._nid = nid
        self._cIP = controllerIP
        self._cluster = cluster
        self._icIndex = None
        self._asCtr = None
        self._controllerClerkPort = controllerClerkPort
        self._imageNames = []
        self._agentThreads = []
        self._finishAll = False
        self.nodeS = NodeService.NodeService()
        self.pretext = pretext
        self.lock = thd.Lock()
        self.rootAdr = os.getcwd()
        self.dpl = Deployer.Deployer(os.path.join(self.rootAdr, 'ImagesBuild'), os.path.join(self.rootAdr, 'Base'))
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
        self._AS()
        
        return True
    
    ######################################## Function Deployment
    def __downloadAndDeploy_Function(self, fname):
        self.pr('Requesting clerk for function: {}'.format(fname))
        ret = self._req_clerk_function(fname)
        if ret is None:
            self.pr('Error: Could not download the source of {} from the Clerk server'.format(fname))
            return None
        func = ret['func']
        req = ret['req']
        self.pr('Now deploying {}'.format(fname))
        self.dpl.deployNewImage(func, req, fname)
        self.pr('\tDone.')
        return True
    
    ######################################## AS
    def allocateTable(self, table):
        with self.lock:
            self.nodeS.allocateTable(table)
            self._createAgentThreads()
    
    def _AS(self):
        self.pr('Handling the auto-scaling event')
        self.__AS_finThrds()
        iAS = self._req_AS_as()
        if iAS is None:
            self.pr('Server does not need scaling this node.')
            return None
        self.__AS_check(iAS['table'])
        self.allocateTable(iAS['table'])
        self._icIndex = iAS['icIndex']
        
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
            ev = socket.recv_json()
            self.pr('Sub:Got {}'.format(ev))
  
    def __AS_finThrds(self):
        self.pr('\t\tPreScale: Waiting for threads to finish')
        self.__finishPoolAllAgents()
        self.pr('\t\t\tPreScale: Done')
        
    def __AS_check(self, table):
        self.pr('\t\tPreScale: Checking the list of functions')
        with self.lock:
            self._imageNames = []
            for imageName in table.keys():
                self._imageNames.append( (imageName, table[imageName][0]) )
        currentImages = self.dpl.getListOfAllImages()
        for image in self._imageNames:
            if not image[0] in currentImages:
                self.__downloadAndDeploy_Function(image[0])

    def _req_AS_as(self):
        ret = self.__req_AS({'msg':'as?'})
        if ret['msg'] == 'as.':
            if ret['icIndex'] == -1:
                return None
            AS = {'icIndex': ret['icIndex'], 'table': ret['table']}
        else:
            AS = None
        return AS
        
    ######################################### FERs and Agents    
    def _createAgentThreads(self):
        for imageN in self._imageNames:
            image = imageN[0]
            N = imageN[1]
            for i in range(N):
                thrd = thd.Thread(target=self._agentThread_Worker, args=(image, i), daemon=False)
                self._agentThreads.append(thrd)
                thrd.start()
    
    def __finishPoolAllAgents(self):
        with self.lock:
            self._finishAll = True
        while True:
            for i in range(len(self._agentThreads)):
                th = self._agentThreads[i]
                if not th.isAlive():
                    del self._agentsThread[i]
                    break
            if len(self._agentThreads) == 0:
                break
        self._finishAll = False
    
    def __poolForAvailableFEU_CPUFriendly(self, imageName):
        while True:
            #self.lock.acquire()
            feu = self.nodeS.findAvailableFEU(imageName)
            #self.lock.release()
            if feu is None:
                time.sleep(0.001)
            else:
                break
        return feu
    
    def _agentThread_Worker(self, imageName, ctr):
        T = time.time()
        self.pr('Agent@{}-{}${}:Starting agent service'.format(imageName, ctr, T))
        portQ = self._portsTable[imageName][0]
        portQP = self._portsTable[imageName][1]
        contextQ = zmq.Context(2)
        Q = contextQ.socket(zmq.REQ)
        Q.connect("tcp://{}:{}".format(self._cIP, portQ))
        contextQP = zmq.Context(2)
        QP = contextQP.socket(zmq.PUSH)
        QP.connect("tcp://{}:{}".format(self._cIP, portQP))
        while True:
            self.pr('Agent@{}-{}${}: Joining Q'.format(imageName, ctr, time.time() - T))
            Q.send_string('?')
            _fer = Q.recv_json()
            if _fer['id'] != -1:
                self.pr('Agent@{}-{}${}: Got a FER: {}'.format(imageName, ctr, time.time() - T, _fer))
            else:
                self.pr('Agent@{}-{}${}: No FERs'.format(imageName, ctr, time.time() - T))
                time.sleep(0.5)
                continue
                
            self.lock.acquire()
            fer = NodeFER.NodeFER(_fer['id'], imageName, _fer['x'], _fer['m'])
            self.lock.release()
            
            feu = self.__poolForAvailableFEU_CPUFriendly(imageName)
            self.pr('Agent@{}-{}${}: Free feu={}'.format(imageName, ctr, time.time() - T, feu._name))
                
            self.lock.acquire()
            retObj = self.nodeS.schedFERonFEU(fer, feu)
            self.pr('Agent@{}-{}${}: Scheduled. Joining...'.format(imageName, ctr, time.time() - T, feu._name))
            self.lock.release()
            
            ret = retObj.get()
            self.pr('Agent@{}-{}${}: Got the result'.format(imageName, ctr, time.time() - T))
            
            #self.lock.acquire()
            feu.check()
            #self.lock.release()
            
            _ret = {'id':_fer['id'], 'r':ret}                
            self.pr('Agent@{}-{}${}: Sending the result: {}'.format(imageName, ctr, time.time() - T, _ret))
            QP.send_json(_ret)
            self.pr('Agent@{}-{}${}: Sent.'.format(imageName, ctr, time.time() - T, _ret))
            if self._finishAll:
                break
        self.pr('Agent@{}-{}${}: Finishing...'.format(imageName, ctr, time.time() - T))
    
    def _agentThread_Worker_pull(self, imageName, ctr):
        T = time.time()
        self.pr('Agent@{}-{}${}:Starting agent service'.format(imageName, ctr, T))
        portQ = self._portsTable[imageName][0]
        portQP = self._portsTable[imageName][1]
        contextQ = zmq.Context()
        Q = contextQ.socket(zmq.PULL)
        Q.connect("tcp://{}:{}".format(self._cIP, portQ))
        contextQP = zmq.Context()
        QP = contextQP.socket(zmq.PUSH)
        QP.connect("tcp://{}:{}".format(self._cIP, portQP))
        while True:
            self.pr('Agent@{}-{}${}: Joining Q'.format(imageName, ctr, time.time() - T))
            _fer = Q.recv_json()
            self.pr('Agent@{}-{}${}: Got a FER: {}'.format(imageName, ctr, time.time() - T, _fer))
            continue
                
            self.lock.acquire()
            fer = NodeFER.NodeFER(_fer['id'], imageName, _fer['x'], _fer['m'])
            self.lock.release()
            
            feu = self.__poolForAvailableFEU_CPUFriendly(imageName)
            self.pr('Agent@{}-{}${}: Free feu={}'.format(imageName, ctr, time.time() - T, feu._name))
                
            self.lock.acquire()
            retObj = self.nodeS.schedFERonFEU(fer, feu)
            self.pr('Agent@{}-{}${}: Scheduled. Joining...'.format(imageName, ctr, time.time() - T, feu._name))
            self.lock.release()
            
            ret = retObj.get()
            self.pr('Agent@{}-{}${}: Got the result'.format(imageName, ctr, time.time() - T))
            
            #self.lock.acquire()
            feu.check()
            #self.lock.release()
            
            _ret = {'id':_fer['id'], 'r':ret}                
            self.pr('Agent@{}-{}${}: Sending the result: {}'.format(imageName, ctr, time.time() - T, _ret))
            QP.send_json(_ret)
            self.pr('Agent@{}-{}${}: Sent.'.format(imageName, ctr, time.time() - T, _ret))
            if self._finishAll:
                break
        self.pr('Agent@{}-{}${}: Finishing...'.format(imageName, ctr, time.time() - T))
                
    ######################################## Clerk
    def _req_clerk_function(self, fname):
        ret = self.__req_clerk({'msg':'function?', 'func':fname})
        if ret['msg'] != 'function.':
            return False
        else:
            return ret
    
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
        self.pr("\t\tWaiting for response")
        resp = socket.recv_json()
        return resp

#%%
node = Node('cluster1', 0, '127.0.0.1', 4040)
