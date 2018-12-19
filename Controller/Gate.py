#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 18 18:23:00 2018

@author: root
"""

import zmq
import multiprocessing as mp
import threading as thd

class Gate:
    def __init__(self, q_port, qPrime_port, funcName):
        self._QPort = q_port
        self._QPPort = qPrime_port
        
        self.Q = mp.Queue()
        self.QP = mp.Queue()
                
        self.proc_Q = thd.Thread(target=Gate._wrk_Q, args=(self.Q, self._QPort, funcName), daemon=True)
        self.proc_QP = thd.Thread(target=Gate._wrk_QP, args=(self.QP, self._QPPort, funcName), daemon=True)
        
        self.proc_Q.start()
        self.proc_QP.start()
        
    def pr(txt):
        print('AGENT: {}'.format(txt))
        
    def _wrk_Q(Q, QPort, fName):
        Gate.pr('Gate: Creating Push server for {} @ {}'.format(fName, QPort))
        context = zmq.Context()
        zmq_socket = context.socket(zmq.PUSH)
        zmq_socket.bind("tcp://*:{}".format(QPort))
        while True:
            obj = Q.get()
            Gate.pr('Gate: Push: got new FER. Sending it.')
            zmq_socket.send_json(obj)
                
    def _wrk_QP(QP, QPPort, fName):
        Gate.pr('Creating Pull server for {} @ {}'.format(fName, QPPort))
        context = zmq.Context()
        zmq_socket = context.socket(zmq.PULL)
        zmq_socket.bind("tcp://*:{}".format(QPPort))
        while True:
                feu = zmq_socket.recv_json()
                Gate.pr('Gate: Pull: Recieved new RET.')
                QP.put(feu)
