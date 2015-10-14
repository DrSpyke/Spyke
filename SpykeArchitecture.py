
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
import multiprocessing as mp
from SpykeUtils import utils as su

class connection(object):
    #weights = np.array()
    def __init__(self,size,scale):
        self.weights = scale*np.random.rand(size,size)
        
    def update(self,history,currenttime,timestep,stepmax,params,learning_rule = 'STDP',neurons = None,reward = None):
        if learning_rule == 'STDP':
            for t in pl.frange(timestep,stepmax,timestep):
                if t < currenttime:
                    print history[currenttime],history[currenttime - t]
                    self.weights[np.array(history[currenttime],int).reshape((-1,1)),np.array(history[currenttime - t],int)] +=  params[0]*np.exp(-params[1]*(currenttime - timestep))
        ###
        #STDP with a global reinforcement signal, a la Florian 2005
        # GLOBAL REINFORCEMENT CODE UNDER DEVELOPMENT
        # Need to vectorize this next!!!!
        ###
        if learning_rule == 'STDP_GLOBAL_REINFORCEMENT': 
            beta, gamma,tau,tau_sigma = params
            neurons.sort()
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
                        for k in xrange(int(currenttime/n.dt)):  
                            eta[num_n,num_m] += beta*np.exp(-( (k-1)*n.dt/tau  ))  #
                            self.weights[num_n,num_m] += gamma*reward*z[num_n,num_m]
                            self.weights[num_m,num_n] -= gamma*reward*z[num_m,num_n]
                            z[num_n,num_m] = beta*z[num_n,num_m] + eta[num_n,num_m]
                else:
                    for num_m,m in enumerate(neurons):
                        for k in xrange(int(currenttime/n.dt)):
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
        self.Rm      = 1                   # resistance (kOhm)
        self.Cm      = 10                  # capacitance (uF)
        self.tau_m   = self.Rm*self.Cm               # time constant (msec)
        self.tau_ref = 4                   # refractory period (msec)
        self.Vth     = 0.8                 # spike threshold (V)
        self.V_spike = 0.5                 # spike delta (V)
        self.act = initAct
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
        if self.spike == True:
            self.spike = False
        if self.time > self.t_rest:
            self.Vm= self.Vm + (-self.Vm + I*self.Rm) / self.tau_m *self.dt
        if self.Vm >= self.Vth:
            self.spike = True
            self.t_rest = self.time + self.tau_ref
            self.Vm = 0
        self.time += self.dt
        if self.spike:
            return 1.0
        else:
            return 0.0
        
class layer(object):
    
    def __init__(self, N,weightscale,multip = False):
        self.neurons = []
        for l in xrange(N):
            self.neurons.append(neuron(0,0))
        self.cnxns = connection(N,weightscale)
        """if multip == True:
            p = mp.Pool(neuron(0,0))
            self.neurons = p"""
            
    def update(self,I_init):
        
        for nn,ne in enumerate(self.neurons):
            for nn2 in xrange(len(self.neurons)):
                ic = ne.spike*self.cnxns.weights[nn2,nn]
            print ne.Vm,ic
            self.neurons[nn].update(ic + I_init)
            
        
        
        
