#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Dec 16 11:39:15 2018

@author: adanayi
"""

import json

#%%
def packet(primitive, data, size=-1):
    _p = primitive.encode('utf-8')
    if size == -1:
        size = len(data)
        _s = size.to_bytes(4, 'big')
    
    return _p + _s + data


def dePacket(pack):
    _p = pack[0: 3]
    _size = pack[3: 7]
    
    primitive = _p.decode('utf-8')
    size = int.from_bytes(_size, 'big')
    data = pack[7:]
    
    return (primitive, data, size)

#%%
def getPacket(con):
    _hdr = con.recv(7)
    _primitive = _hdr[0:3]
    _size = _hdr[3:]
    
    primitive = _primitive.decode('utf-8')
    size = int.from_bytes(_size, 'big')
    
    data = con.recv(size)
        
    return (primitive, data, size)

#%%
def dict2Bytes(d):
    s=json.dumps(d)
    return s.encode('utf-8')

def bytes2Dict(b):
    return json.loads(b.decode('utf-8'))
    
def FER_pack(x_dict, m_dict):
    argS = {'x':x_dict, 'm':m_dict}
    return dict2Bytes(argS)

def FER_depack(bytesObject):
    return bytes2Dict(bytesObject)
