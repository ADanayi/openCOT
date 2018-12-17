#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Dec 16 22:36:10 2018

@author: adanayi
"""

import time
#import zmq
import docker
#import socket
import FEUService
import NodeFER

import sys
sys.path.append('./../FEU')
#import common_convs as cc


class Node:
    def __init__(self, pretext='\tNode'):
        self._client = docker.from_env()
        self._client.containers.prune()
        self.pretext = pretext
        self.cpu_period = int(10000)
        
        self._FEUs = []
        self._freeFEUs = {}
        self._uaFERs = []
        self._aFERs = []
        
        self.__imageIDCtrs = {}
        
        self.__poolAllowed = True
        self.__sleepTime = 3
        self.pr("Initialized node")
        
    def pr(self, txt):
        print("{}::{}".format(self.pretext, txt))
        
    #########################% Node: Allocation and scaling functions
    def allocateTable(self, table, firstFlush=True, allContainers=True):
        if firstFlush:
            self.flushNode(allContainers)
        for imageName in table.keys():
            
            
            self.newFEU(name, imageName, )

            ######
    def _imageIDCtr_getInitVal(self, imageName):
        return 0
    
    def _imageIDCtr_iterate(self, imageName):
        if imageName in self.__imageIDCtrs.keys():
            self.__imageIDCtrs[imageName] += 1
        else:
            self.__imageIDCtrs[imageName] = self._imageIDCtr_getInitVal(imageName)
        return self.__imageIDCtrs[imageName]
            
            ######
    def _getNewFEUName(self, imageName):
        imageIDCtr = self._imageIDCtr_iterate(imageName)
        name = 'FEU::{}.{}'.format(imageName, imageIDCtr)
        return name
        

    #########################% Node: Task scheduling functions
    def addNewFER(self, fer):
        self._uaFERs.append(fer)
        
    def _findFEU(self, fer, remFromFrees=True):
        fFEUs = self._freeFEUs[fer.imageName]
        if len(fFEUs) == 0:
            return None
        else:
            ret = fFEUs[0]
            if remFromFrees:
                del fFEUs[0]
            return ret
        
    def schedFER(self, lid): # lid is the linear ID in the _uaFERs list
        fer = self._uaFERs[lid]
        feu = self._findFEU(fer)
        if feu is None:
            return None
        del self._uaFERs[lid]
        ret = feu.exe(fer.x, fer.m)
        fer.setRetObject(ret)
        self._aFERs.append(fer)
        return feu
    
    #########################% Node: FEU management
    def flushNode(self, allContainers=True):
        self.pr('Deleting all FEUs')
        if allContainers:
            List = self._listCnts()
            for cnt in List:
                cnt.remove(force=True)
        else:
            List = self._FEUs
            for feu in List:
                while feu.isBusy():
                    time.sleep(0.001)
                feu.fin()
        self._FEUs = []
        self._freeFEUs = {}
        self._uaFERs = []
        self._aFERs = []
            
    def newFEU(self, name, imageName, port, P=0.1, iport=2020):
        self.pr('Adding new FEU={} with f={}, P={}'.format(name, imageName, P))
        cnt = self._newCnt(name, imageName, port, P, iport)
        feu = FEUService.FEUService(cnt, imageName, port, P)
        
        if not imageName in self._freeFEUs.keys():
            self._freeFEUs[imageName] = []
        self._freeFEUs[imageName].append(feu)
        self._FEUs.append(feu)
        
        time.sleep(self.__sleepTime)
        self.pr('[FEU Added]'.format(name, imageName, P))
        return feu
        
    #########################% Node: cnt lifecycle functions
    def _newCnt(self, name, imageName, port, P=0.1, iport=2020): # Returns -1 on error, number of imageName FEUs otherwise
        self.pr('Crated FEU instance of {} for port {}, named: {}'.format(imageName, port, name))
        quota = int(P*self.cpu_period)
        cnt = self._client.containers.run(imageName, detach=True, ports={'{}/tcp'.format(iport):'{}'.format(port)}, cpu_shares=int(P*1024), name=name,
                                                                        cpu_period = self.cpu_period, cpu_quota = quota, 
                                                                        auto_remove=True)
        
        if cnt != -1:
            return cnt
        else:
            return -1
    
    def _delCnt(self, cnt, force=True):
        cnt.remove(force=True)
        self.pr('Deleted FEU instane: {}'.format(cnt.name))
        
    def _listCnts(self):
        return self._client.containers.list(all = True)
        
    def _delAllCnts(self, force=True):
        self.pr('Deleting all FEUs')
        for cnt in self._listCnts():
            self._delCnt(cnt, force)

#%%
node = Node()
node.flushNode()
feu = node.newFEU('feu1', 'echofuncbusy', 8000)
#%%
x = {'name':'abolfazl', 'fname':'danayi', 'age':24}
m = {'USERID':'ADanayi'}
fer = NodeFER.NodeFER('11223344', 'echofuncbusy', x, m)
node.addNewFER(fer)
node.schedFER(0)

#%%
node.flushNode()
