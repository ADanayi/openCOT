#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Dec 16 12:38:34 2018

@author: adanayi
"""

from core import Core
from func import f

with open('./boot', 'r') as b:
    lines = b.readlines()
    IP = lines[0]
    Port = int(lines[1])
    Pretext = lines[2]

core = Core(f, Port, IP, Pretext)
core.join()

print("FEU exited.")
