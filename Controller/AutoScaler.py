#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 18 18:56:27 2018

@author: root
"""

import zmq
import threading as thd

class AutoScaler:
    def __init__(self, signalsPort, asPorts):
        self.sPort = signalsPort
        self.asPorts = asPorts
        
        self.lock = thd.Lock()
        
        self.sContext = zmq.Context()        
        self.sSocket = self.sContext.socket(zmq.PUB)
        self.sSocket.bind("tcp://*:{}".format(signalsPort))

        self.asServers = {}
        for cluster in asPorts.keys():
            port = asPorts[cluster]
            self.asServers[cluster] = self._get_asServer(port, cluster)
            self.asServers[cluster].start()
    
    def pr(self, txt):
        print("\tAutoscaler::{}".format(txt))

    def _get_asServer(self, port, cluster):
        self.pr("Creating asServer for cluster:{} on port {}".format(cluster, port))
        server = thd.Thread(target=self._as_server_wrk, args=(port, cluster), daemon=True)
        return server
        
    def _as_server_wrk(self, port, cluster):
        self.pr('AS@{}: Creating server on {}'.format(cluster, port))
        
        Context = zmq.Context()
        Sock = Context.socket(zmq.REP)
        Sock.bind("tcp://*:{}".format(port))
        self.pr('AS@{}: Server binded.'.format(cluster))
        while True:
            req = Sock.recv_json()
            self.pr('AS@{}: Got request: {}'.format(cluster, req))
            result = self.__asServer(req, cluster)
            self.pr('AS@{}: Sending response: {}'.format(cluster, result))
            Sock.send_json(result)
    
    def __asServer(self, req, cluster):
        if req['msg'] != 'as?':
            return {'msg':'ERR'}
        item = self.getNextInClusterWithPop(cluster)
        if item is None:
            return {'msg':'as.', 'icIndex':-1}
        return {'msg':'as.', 'icIndex':item[0], 'table':item[1]}

    def setNewAutoScaling(self, asTableObj): 
        with self.lock:
            self.asTableDS = {}
            for cluster in asTableObj.keys():
                self.asTableDS[cluster] = {}
                clusterReq = asTableObj[cluster]
                icCtr = 0
                for nodesReq in clusterReq:
                    N = nodesReq[0]
                    table = nodesReq[1]
                    for _ in range(N):
                        self.asTableDS[cluster][icCtr] = table
                        icCtr += 1
            
            self.sSocket.send_json({'as':'ev_newAs'})
        
    def getNextInClusterWithPop(self, cluster):
        with self.lock:
            if len(self.asTableDS[cluster]) == 0:
                return None
            else:
                ret = self.asTableDS[cluster].popitem()
                if len(self.asTableDS[cluster]) == 0:
                    print('AS@{}: Cluster completely scaled.'.format(cluster))
                return ret