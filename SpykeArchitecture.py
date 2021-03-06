# -*- coding: utf-8 -*-
"""
Created on Mon Sep 28 01:45:58 2015
@author: Corey Hart
This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 3 of the License, or
any later version.
"""

import numpy as np
import pylab as pl
import os,binascii
#import multiprocessing as mp
import multiprocessing 
from SpykeUtils import utils as su


def collector(neuronNum,occupancy,netw):
    N,M = np.shape(occupancy)
    summedCurrents = np.zeros(N)
    for n in range(N):
         for m in range(M):
             if occupancy[n,m] == 1:
                 wts = netw.projections.lookup(n,m,len(netw.layers))
                 for nn,ne in enumerate(netw.layers[n].neurons):
                     for nn2,ne2 in enumerate(netw.layers[m].neurons):
                         summedCurrents[n]+= ne2.spike*wts[nn,nn2] #ic is internal current 
    return summedCurrents

class projection(object):
    #weights = np.array()
    def __init__(self,size):
        self.weights = []
        for j in range(size):
            for k in range(size):
                self.weights.append(0)
    def populate(self,idx1,idx2,size,scalemat,layers):
        index = idx1*(size) + idx2
        self.weights[index] = scalemat[idx1,idx2]*np.random.rand(len(layers[idx1].neurons),len(layers[idx2].neurons))
        
    def lookup(self,idx1,idx2,size):
        index = idx1*(size) + idx2
        return self.weights[index]        
        
        
class networks(object):
    def __init__(self,nnvec,pscvec,scvec,occupancy):
        self.layers = []
        self.projections = projection(2)
        for l,numNeurons in enumerate(nnvec):
            self.layers.append(layer(numNeurons,scvec[l]))          
        for l,numNeurons in enumerate(nnvec):           
            for m,numNeurons2 in enumerate(nnvec):
                if m != l and occupancy[l,m] == 1:
                    self.projections.populate(m,l,len(nnvec),pscvec,self.layers)

class connection(object):
    #weights = np.array()
    def __init__(self,size,scale):
        
        self.weights = scale*np.random.rand(size,size)
        
    def update(self,history,currenttime,timestep,stepmax,params,learning_rule = 'STDP',neurons = None,reward = None):
        if learning_rule == 'STDP':
            for t in pl.frange(timestep,stepmax,timestep):
                if t < currenttime:
                    self.weights[np.array(history[currenttime],int).reshape((-1,1)),np.array(history[currenttime - t],int)] +=  params[0]*np.exp(-params[1]*(currenttime - timestep))
        ###
        #STDP with a global reinforcement signal, a la Florian 2005
        ### GLOBAL REINFORCEMENT CODE UNDER DEVELOPMENT
        if learning_rule == 'STDP_GLOBAL_REINFORCEMENT': 
            beta, gamma,tau,tau_sigma = params
            #print(neurons)
            #neurons.sort()
            #loop through all neurons
            eta = np.zeros(np.shape(self.weights))
            z =   np.zeros(np.shape(self.weights))
            sigma = []
            for num_n,n in enumerate(neurons):
                ss = (n.dt/tau_sigma)*np.exp(beta*(n.Vm - n.Vth))
                if ss < 1:
                    sigma.append(ss)
                else:
                    sigma.append(0.99)
                if n.spike == True:
                    for num_m,m in enumerate(neurons):
                        for k in range(int(currenttime/n.dt)):  
                            eta[num_n,num_m] += beta*np.exp(-( (k-1)*n.dt/tau  ))  #
                            self.weights[num_n,num_m] += gamma*reward*z[num_n,num_m]
                            self.weights[num_m,num_n] -= gamma*reward*z[num_m,num_n]
                            z[num_n,num_m] = beta*z[num_n,num_m] + eta[num_n,num_m]
                else:
                    for num_m,m in enumerate(neurons):
                        for k in range(int(currenttime/n.dt)):
                            eta[num_n,num_m] -= ((beta*sigma[num_n]/(1 - sigma[num_n])))*np.exp(-( (k-1)*n.dt/tau  ))
                            self.weights[num_n,num_m] += gamma*reward*z[num_n,num_m]
                            self.weights[num_m,num_n] -= gamma*reward*z[num_m,num_n]
                            z[num_n,num_m] = beta*z[num_n,num_m] + eta[num_n,num_m]
                

class neuron(object):
    
    def __init__(self,Vm,initAct):
        
      ## setup parameters and state variables
        self.T       = 50                  # total time to simulate (msec)
        self.dt      = 0.125               # simulation time step (msec)
        self.time    = 0   #np.arange(0, self.T+self.dt, self.dt) # time array
        self.t_rest  = 0                   # initial refractory time
        self.last_t  = 0                   # last time
        ## LIF properties
        self.Vm      = np.random.rand()    # potential (V) trace over time
        self.Rm      = 10             # resistance (kOhm)
        self.Cm      = 1           # capacitance (uF)
        self.tau_m   = self.Rm*self.Cm               # time constant (msec)
        self.tau_ref = 1                   # refractory period (msec)
        self.Vth     = 0.8                # spike threshold (V)
        self.V_spike = 0.5                 # spike delta (V)
        self.act = initAct
        self.noise_amp = 0.05
        self.spike = False;
        ## Stimulus 
        self.I       = 1.5                 # input current (A) 
        self.id = binascii.b2a_hex(os.urandom(15)) 
        while self.id in su.gKeyStore:
            self.id = binascii.b2a_hex(os.urandom(15)) 
        self.report(self.id) #  reports key to database
        
    def report(self,id):
        su.gKeyStore.append(id)
        
    def update(self,I):
       ## iterate over each time step
        self.Vm += self.noise_amp*(np.random.rand()-0.5)*2
        if self.spike == True:
            self.spike = False
        
        if self.Vm >= self.Vth:
            self.spike = True
            self.t_rest = self.time + self.tau_ref
            self.Vm = 0
        if self.time >= self.t_rest:
            self.Vm= self.Vm + (-self.Vm + I*self.Rm) / self.tau_m *self.dt
        self.time += self.dt
        if self.spike:
            return 1.0
        else:
            return 0.0
        
class layer(object):
    
    def __init__(self, N,weightscale,multip = False):
        self.neurons = []
        self.features = []
        for l in range(N):
            self.neurons.append(neuron(0,0))
        print(N,weightscale)
        self.cnxns = connection(N,weightscale)
        """if multip == True:
            p = mp.Pool(neuron(0,0))
            self.neurons = p"""
    def findspikes(self,neurons):
           return neurons.spike
    def update(self,I_init,extProj = None):
        
        for nn,n in enumerate(self.neurons):
            ic = 0
            for nn2,ne in enumerate(self.neurons):
               ic += ne.spike*self.cnxns.weights[nn2,nn] #ic is internal current 
            #a_pool = multiprocessing.Pool()
            #a_pool.map(self.findspikes,self.neurons )
            #ic = np.dot(np.array(pooled_spikes),self.cnxns.weights[:,nn])
                #if ic != 0  and self.neurons[nn].Vm != 0:
                #    print('%%%%%%%%%%%%%%%%',nn,ic + I_init,self.neurons[nn2].Vm,'############')
            if extProj != None:
             
                ec = collector(nn,occupancy,netw)
                self.neurons[nn].update(ic + I_init + ec) # ec is external current
                
            else:
                
                self.neurons[nn].update(ic + I_init)
               
            
   
        
        
