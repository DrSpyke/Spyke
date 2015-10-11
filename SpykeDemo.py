# -*- coding: utf-8 -*-
"""
SpykeDemo.py  creates a Layer of neurons and a connection matrix and steps 
it through several iterations with an injected current.

Created on Sun Oct 04 23:26:52 2015
This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 3 of the License, or
any later version.
@author: Corey Hart
"""
from SpykeArchitecture import *


L = layer(100,0.1) # 100 neurons with a maximum connection weight of 0.1
recordIdx = {}
recordTimes = {}
recordNeurons = {}

#initial neuron objects
for l in xrange(len(L.neurons)):
    recordNeurons[l] = list()
    
# store original weight matrix
w = np.zeros((100,100))
for el in xrange(100):
    for el2 in xrange(100):
        w[el,el2] = L.cnxns.weights[el,el2]  # original weights

#loop through time index        
for l in xrange(50):
    L.update(10.0)  # global drive  = 10.0
    fired = []
    for num_n,n in enumerate(L.neurons):
        if n.spike == True:
            fired.append(num_n)
            recordNeurons[num_n].append(n.time)
    recordIdx[l] = fired # dictionary of neurons that have fired, indexed by time index.
    recordTimes[n.time] = fired
    L.cnxns.update(recordTimes,n.time,n.dt,6.25, [0.1,1.0,0.5],learning_rule = 'STDP')
