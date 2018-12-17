#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 17 16:28:34 2018

@author: root
"""

class NodeFER:
    def __init__(self, Id, imageName, x, m):
        self.id = Id
        self.imageName = imageName
        self.x = x
        self.m = m
        self.state = 'node'
        self.ret = None
        
    def setRetObject(self, ret):
        self.state = 'feu'
        self.ret = ret
        
    def isExecuted(self):
        if self.ret is None:
            return False
        if self.ret.ready():
            self.state = 'node_done'
            return True
    
    def getValue(self):
        if not self.isExecuted():
            return None
        return self.ret.get()
