# -*- coding: utf-8 -*-
"""
SpykeDemo.py  creates a Layer of neurons and a connection matrix and steps 
it through several iterations with an injected current.

Created on Sun Oct 04 23:26:52 2015
This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 3 of the License, or
any later version.
@author: Corey
"""
from Spyke import *

L = layer(100,0.1) # 100 neurons with a maximum connection weight of 0.1
recordIdx = {}
recordTimes = {}
recordNeurons = {}
for l in xrange(len(L.neurons)):
    recordNeurons[l] = list()
for l in xrange(50):
    L.update(10.0)  # global drive  = 10.0
    fired = []
    for num_n,n in enumerate(L.neurons):
        if n.spike == True:
            fired.append(num_n)
            recordNeurons[num_n].append(n.time)
    recordIdx[l] = fired # dictionary of neurons that have fired, indexed by time index.
    recordTimes[n.time] = fired
