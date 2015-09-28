# -*- coding: utf-8 -*-
"""
Created on Sun Sep 27 20:00:20 2015

@author: ellie
"""

import shapely
#This represents a dictrict and the polygons that make it up
class District():
    def __init__(self, polygons=[]):
        self.areas=polygons
        self.polygon=shapely.ops.cascaded_union(polygons)
    def addArea(self, newArea):
        
        self.areas.append(newArea)
        self.polygon=self.polygon.union(newArea)
    