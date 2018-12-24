#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec 22 21:06:27 2018

@author: root
"""

import docker
import shutil
import os

class Deployer:
    def __init__(self, buildPath, basePath):
        self.client = docker.from_env()
        self.client.containers.prune()
        self.buildPath = buildPath
        self.basePath = basePath
        
    def getListOfAllImages(self):
        l1 = self.client.images.list()
        l2 = []
        for image in l1:
            tags = image.tags
            if len(tags) > 0:
                l2.append(tags[0].split(':')[0])
        return l2
    
    def prune(self):
        self.client.images.prune()
    
    def removeAllImages(self):
        self.prune()
        l1 = self.client.images.list()
        for ll in l1:
            self.client.images.remove(ll.id, force=True)
            
    def deployNewImage(self, functionData, requirementsData, fname):
        path = os.path.join(self.buildPath, fname)
        if not os.path.exists(path):
            os.mkdir(path)
        with open(os.path.join(path, 'func.py'), 'w') as file:
            file.write(functionData)
        with open(os.path.join(path, 'requirements.txt'), 'w') as file:
            file.write(requirementsData)
        for file in os.listdir(self.basePath):
            src = os.path.join(self.basePath, file)
            shutil.copy2(src, path)
        self.client.images.build(path=path, tag=fname)        
