# -*- coding: utf-8 -*-
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
import xlrd
import matplotlib.pyplot as plt



class utils:
    gKeyStore = []
   
    def featurizer(self,record):
        R = len(record)
        merged = list(itertools.chain.from_iterable(record.values()))
        f = np.zeros((len(np.unique(merged)),R))
        for r in range(R):
            print(record[r])
            f[np.array(record[r],int).reshape((-1,1)),r] = 1
        return f
    
class inputs:
    
    inweights = np.array
    activation = np.array
    def __init__(self,data,numFeatures,sc):
        self.inweights = sc*np.ones(numFeatures)
        self.activation = np.zeros(numfeatures)
    
    
def open_excel(path,lencols):
    """
    Open and read an Excel file
    """
    book = xlrd.open_workbook(path)
  
    first_sheet = book.sheet_by_index(0)
    out = []
    # read a row slice
    for rowx in range(first_sheet.nrows):
        out.append([first_sheet.row_slice(rowx,
                                col,col+1)[0].value for col in xrange(lencols)])
    out = np.array(out)
    return out
    

class plots:
    def raster(times_struct):
        ###
        #do nothing
        return 0