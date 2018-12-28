#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Dec 16 12:40:15 2018

@author: adanayi
"""

"""
Note: This is only a test sample function. the structure must be followed.
"""

import time

def f(FER):
    print("Hey! I am a function!")
    print("You have called me with this args: {}".format(FER['x']))
    print("And this metadata: {}".format(FER['m']))
    print("So! For now, you have to wait for 1 sec!")
    t = time.time()
    while True:
        if time.time() - t > 1:
            break
    print("Then I echo it back to yourself!!!")
    return FER['x']

