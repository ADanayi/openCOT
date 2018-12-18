#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 18 18:23:00 2018

@author: root
"""

import zmq
import multiprocessing as mp

class Gate:
    def __init__(self, q_port, qPrime_port, funcName):
        self._QPort = q_port
        self._QPPort = qPrime_port
        
        self.Q = mp.Queue()
        self.QP = mp.Queue()
        
        self.proc_Q = mp.Process(target=self._wrk_Q, args=(self.Q,), daemon=True)
        self.proc_QP = mp.Process(target=self._wrk_QP, args=(self.QP,), daemon=True)
        
    def _wrk_Q(self, Q):
        context = zmq.Context()
        zmq_socket = context.socket(zmq.PUSH)
        zmq_socket.bind("tcp://*:{}".format(self._QPort))
        while True:
            zmq_socket.send_json(Q.get())
                
    def _wrk_QP(self, QP):
        context = zmq.Context()
        zmq_socket = context.socket(zmq.PULL)
        zmq_socket.bind("tcp://*:{}".format(self._QPort))
        while True:
                feu = zmq_socket.get_json()
                QP.put(feu)
