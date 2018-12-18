#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 18 18:56:27 2018

@author: root
"""

import zmq

class AutoScaler:
    def __init__(self, signalsPort, asPort, autoScaleCtrCutOff=1000):
        self.sPort = signalsPort
        self.asPort = asPort
        
        self.sContext = zmq.Context()
        self.asContext = zmq.Context()
        
        self.sSocket = self.sContext.socket(zmq.PUB)
        self.sSocket.bind("tcp://*:{}".format(signalsPort))
        
        self.asSock = self.asContext.socket(zmq.PUSH)
        self.asSock.bind("tcp://*:{}".format(asPort))
        
        self.autoScaleCtr = 0
        self.autoScaleCtrCutOff = autoScaleCtrCutOff

    def getAutoScaleCtr(self):
        return self.autoScaleCtr

    def autoScale(self, tableList):
        self.autoScaleCtr += 1
        self.autoScaleCtr %= self.autoScaleCtrCutOff
        self.sScoket.send_json({'msg':'ev_as', 'ctr':self.autoScaleCtr})
        
        for As in tableList:
            self.asSocket.send_json({'msg':'table', 'ctr':self.autoScaleCtr, 'table':As})
            