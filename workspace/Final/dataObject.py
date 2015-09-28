# -*- coding: utf-8 -*-
"""
Created on Sun Sep 27 18:12:28 2015

@author: ellie
"""

import shapely

class DataObject():
    def __init__(self, pol, pDict, tract=True):
        self.polygon=shapely.geometry.shape(pol['geometry'])
        odict=pol['properties']
        self.state=odict['STATEFP10']
        self.county=odict['COUNTYFP10']
        self.tract=odict['TRACTCE10']

        if (tract):
            self.population=pDict.getPopulation(self.state, self.county, self.tract)
        else:
            self.block=odict['BLOCKCE10']
            self.population=pDict.getPopulation(self.state, self.county, self.tract, self.block)
class DummyDataObject(DataObject):
    def __init__(self, poly):
        self.polygon=poly
        self.state= 'Testing'
        self.county= 'Testing'
        self.tract= 'Testing'
        self.population=50


    