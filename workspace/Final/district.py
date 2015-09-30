# -*- coding: utf-8 -*-
"""
Created on Sun Sep 27 20:00:20 2015

@author: ellie
"""

import shapely
#This represents a dictrict and the polygons that make it up
class District():
    def __init__(self, objects=[]):
        self.objects=objects
        self.population=0
        for obj in objects:
            self.population+=obj.population()
#        self.polygon=shapely.geometry.MultiPolygon(self.areas)
        self.polygon=shapely.ops.cascaded_union(self.objects)
    def addArea(self, newArea):
        
        self.objects.append(newArea)
        self.polygon=self.polygon.union(newArea)
    