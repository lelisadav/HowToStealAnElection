# -*- coding: utf-8 -*-
"""
Created on Sun Sep 27 21:13:10 2015

@author: ellie
"""
import util
import gerrymander as gerry
import math
import shapely.geometry
import matplotlib.pyplot as plt
from descartes import PolygonPatch
import dataObject
import random
from matplotlib.collections import PatchCollection
class SearchState():
    def __init__(self, objects, districts=[], cost=0, previous=[]):
        self.objects=objects
        self.districts=districts
        self.cost=cost
        self.previous=previous
    def isFinished(self):
        return (len(self.objects)==0)
    def getSuccessors(self):
        

        successors=[]
        for district in self.districts:
            for obj in district.objects:
                if (findTouching(obj, district.polygon)):
                    poly2=list(self.objects)
                    poly2.remove(obj)
                    districts2=list(self.districts)
                    districts2.remove(district)
                    dis2=list(district.objects)
                    dis2.append(obj)
                    district2=dis.District(dis2)
                    districts2.append(district2)
                    prev=list(self.previous)
                    prev.append(self.districts)
                    newState=SearchState(poly2, districts2, self.cost, prev)
                    successors.append(newState)
        print(len(successors))
        return successors
    def getStart(self, number):
        lsDist=[]
        
        maxMax=-1
        for i in range(number):
            maxIso1=-1
#            maxIso2=-1
#           maxPoly=None
            maxObj1=None
#            maxObj2=None
        
            for o in self.objects:
#                print('i')
               
                if (isoperi(o)>maxIso1):
                    maxIso1=isoperi(o)
#                        maxPoly=p
                    maxObj1=o
            if (maxIso1>maxMax):
                maxMax=maxIso1
            self.objects.remove(maxObj1)
            dist=dis.District([maxObj1])
            
            lsDist.append(dist)
            
        ls=[]
        ls.append(SearchState(list(self.objects), lsDist, maxMax, []))
        return ls
def findTouching(poly1, poly2):
    
#    print(type(poly1))
    p1=set(poly1.points())
    p2=set(poly2.exterior.coords)
    return (len(p1.intersection(p2)) >=2)
#    return ((poly1.position() != poly2.position()) and len(poly2.points.intersection(poly1.points())) > 0)
#    return type(poly1.intersection(poly2)) is shapely.geometry.LineString
##    return poly1.touches(poly2)
#    return (type(poly1.intersection(poly2)) is shapely.geometry.MultiLineString) or (type(poly1.intersection(poly2)) is shapely.geometry.LineString)
#    if (poly1.touches(poly2)):
#        mp=shapely.geometry.MultiPolygon([poly1, poly2])
#        if (not mp.is_valid):
#            return True
#    return False
                    
       
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
        
def search(polygons, num, heuristic=nullHeuristic):
    priorityFunction= lambda item: heuristic(item)
    S=util.PriorityQueueWithFunction(priorityFunction)
    sett=set()
    curr=SearchState(polygons)
    for c in curr.getStart(num):
        S.push(c)
    i=0
    delta=20
    while (S.isEmpty()==False):
        curr=S.pop()
        if (i%delta==0 and not i==0):
#            print(getCurrStateInfo(curr))
            showSearchResults(curr)
        i+=1    
        if (curr.isFinished()):
#            showSearchResults(curr)
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
#                        (print(heuristic(child))
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
#def getCurrStateInfo(state):
#    dist=state.districts
#    s='Unused: '+str(len(state.objects))+', Districts: '
#    for d in dist:
#        s+=str(len(d.areas))+', '
#    return s
