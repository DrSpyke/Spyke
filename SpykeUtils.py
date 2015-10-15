# -*- coding: utf-8 -*-
"""
Created on Sat Oct 10 17:31:32 2015
This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 3 of the License, or
any later version.
@author: Corey
"""
import itertools
import numpy as np

class utils:
    gKeyStore = []
   
    def featurizer(self,record):
        R = len(record)
        merged = list(itertools.chain.from_iterable(record.values()))
        f = np.zeros((len(np.unique(merged)),R))
        for r in xrange(R):
            print record[r]
            f[np.array(record[r],int).reshape((-1,1)),r] = 1
        return f
    
    
