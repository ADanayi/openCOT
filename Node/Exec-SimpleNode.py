#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 18 18:04:21 2018

@author: root
"""

from Node import Node

cluster = input('Please enter the cluster name: ')
CIP = input('Please enter the Server IP: ')
node = Node(cluster, 0, CIP, 4040)
