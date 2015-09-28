# -*- coding: utf-8 -*-
"""
Created on Sun Sep 27 21:13:10 2015

@author: ellie
"""
import util
import district as dis
import math
import shapely.geometry
import matplotlib.pyplot as plt
from descartes import PolygonPatch
import dataObject
from matplotlib.collections import PatchCollection
class SearchState():
    def __init__(self, objects, districts=[], cost=0, previous=[]):
        self.objects=objects
        self.polygons=[]
        for obj in objects:
            self.polygons.append(obj.polygon)
        self.districts=districts
        self.cost=cost
        self.previous=previous
    def isFinished(self):
        return (len(self.polygons)==0)
    def getSuccessors(self):
#        print(type(self.districts))
        if (len(self.districts)==0):
            maxIso1=-1
#            maxPoly=None
            maxObj1=None
            maxIso2=-1
            maxObj2=None
            for o in self.objects:
                p=o.polygon
                if (isoperi(p)>maxIso1):
                    maxIso1=isoperi(p)
#                    maxPoly=p
                    maxObj1=o
                elif(isoperi(p)>maxIso2):
                    maxIso2=isoperi(p)
                    maxObj2=o
#            print(maxIso)
#            print(maxPoly)
            obj2=list(self.objects)
            obj2.remove(maxObj1)
            obj2.remove(maxObj2)
#            poly2=list(self.polygons)
#            poly2.remove(maxPoly)
            dist=dis.District([maxObj1.polygon])
            dist2=dis.District([maxObj2.polygon])
            lsDist=[]
            lsDist.append(dist)
            lsDist.append(dist2)
            
            ls=[]
            ls.append(SearchState(obj2, lsDist, maxIso1, []))
            return ls
        successors=[]
        for obj in self.objects:
            poly=obj.polygon
            for district in self.districts:
                if (findTouching(poly, district.polygon)):
                    poly2=list(self.objects)
                    poly2.remove(obj)
                    districts2=list(self.districts)
                    districts2.remove(district)
                    dis2=list(district.areas)
                    dis2.append(poly)
                    district2=dis.District(dis2)
                    districts2.append(district2)
                    prev=list(self.previous)
                    prev.append(self.districts)
                    newState=SearchState(poly2, districts2, self.cost, prev)
                    successors.append(newState)
        print(len(successors))
        return successors
def findTouching(poly1, poly2):
    if (poly1.touches(poly2)):
        mp=shapely.geometry.MultiPolygon([poly1, poly2])
        if (not mp.is_valid):
            return True
    return False
                    
       
def nullHeuristic(polygon):
  """
  A heuristic function estimates the cost from the current state to the nearest
  goal in the provided SearchProblem.  This heuristic is trivial.
  """
  return 0        
def isoperi(polygon):
#    return 0
    area=polygon.area
    perim=polygon.length
    num=4*math.pi*area
    denom=perim**2
    quo=num/denom
    return quo
        
def search(polygons, heuristic=nullHeuristic):
    priorityFunction= lambda item: heuristic(item)
    S=util.PriorityQueueWithFunction(priorityFunction)
    sett=set()
    curr=SearchState(polygons)
    S.push(curr)
    i=0
    delta=100
    while (S.isEmpty()==False):
        curr=S.pop()
#        if (i%delta==0):
#            showSearchResults(curr)
#        i+=1    
        if (curr.isFinished()):
            return curr
        else:
            set2=tuple(curr.districts)
            if (set2 not in sett):
                sett.add(set2)
                children=curr.getSuccessors()
#                print(type(children))
                for child in children:
                    
                    
#                     (child[0] not in sett):
#                    var= list(curr[3])
#                #print("Var1:",var)
#                    var.append(curr[1])
#                    
#                    newPriority=curr[2]+child[2]
#               
#                #print("Var2:",var)
##                 print
#                    child=[child[0], child[1], newPriority ,var]
##                 print('child2')     
##                 print child
#                    S.push(child)
                    set3=tuple(child.districts)
                    if (set3 not in sett):
                        var=list(curr.previous)
                        var.append(curr.districts)
                        newPriority=curr.cost+child.cost
                        child=SearchState(child.objects, child.districts, newPriority, var)
                        S.push(child)
def showSearchResults(searchState):
    polygons=[]
    for district in searchState.districts:
        polygons.append(district.polygon)
    mp=shapely.geometry.MultiPolygon(polygons)
    cm = plt.get_cmap('YlOrRd')
    num_colours=len(mp)
##    num_colours = len(mp)
##    p=shapely.geometry.Polygon([(0,0), (1, 0), (1,1)])
##    p.
    fig = plt.figure()
    ax = fig.add_subplot(111)
    if (len(mp)==0):
        minx=0
        miny=0
        maxx=100
        maxy=100
    else:
        minx, miny, maxx, maxy = mp.bounds
        
    w, h = maxx - minx, maxy - miny
    ax.set_xlim(minx - 0.2 * w, maxx + 0.2 * w)
    ax.set_ylim(miny - 0.2 * h, maxy + 0.2 * h)
    ax.set_aspect(1)
    
    patches = []
    for idx, p in enumerate(mp):
    
        colour = cm(1. * idx / num_colours)
        patches.append(PolygonPatch(p, fc=colour, ec='#555555', lw=0.2, alpha=1., zorder=1))
        ax.add_collection(PatchCollection(patches, match_original=True))
    ax.set_xticks([])
    ax.set_yticks([])
    plt.title("Shapefile polygons rendered using Shapely")
    plt.tight_layout()
#    print('heelo')
#    if (save):
#        plt.savefig('data/results/texas_'+f+'.png', alpha=True, dpi=300)
    plt.show()