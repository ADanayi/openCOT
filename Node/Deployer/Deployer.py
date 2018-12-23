#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec 22 21:06:27 2018

@author: root
"""

import docker

class deployer:
    def __init__(self):
        self.client = docker.from_env()
        self.client.containers.prune()
        
    def getListOfAllImages(self):
        l1 = self.client.images.list()
        l2 = []
        for image in l1:
            tags = image.tags
            if len(tags) > 0:
                l2.append(tags[0].split(':')[0])
        return l2
    
#%%
Dpl = deployer()
Dpl.getListOfAllImages()
