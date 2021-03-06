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
from SpykeUtils import *


L = layer(30,0.3) # 100 neurons with a maximum connection weight of 0.1
recordIdx = {}
recordTimes = {}
recordNeurons = {}

#initial neuron objects
for l in range(len(L.neurons)):
    recordNeurons[l] = list()
    
# store original weight matrix
w = np.zeros((30,30))
for el in range(30):
    for el2 in range(30):
        w[el,el2] = L.cnxns.weights[el,el2]  # original weights

#loop through time index        
for l in range(100):
    L.update(10.0)  # global drive  = 10.0
    fired = []
    for num_n,n in enumerate(L.neurons):
        if n.spike == True:
            fired.append(num_n)
            recordNeurons[num_n].append(n.time)
    
    recordIdx[l] = fired # dictionary of neurons that have fired, indexed by time index.
    recordTimes[n.time] = fired
    beta = 0.8
    gamma  = 0.1
    tau = 0.1
    tau_sigma = 10
    params = [beta, gamma,tau,tau_sigma]
    #L.cnxns.update(recordTimes,n.time,n.dt,6.25, params,learning_rule = 'STDP_GLOBAL_REINFORCEMENT',neurons = L.neurons,reward = 0.001*(np.random.rand()>0.5))
