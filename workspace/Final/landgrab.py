# -*- coding: utf-8 -*-
"""
Created on Mon Sep 28 21:22:07 2015

@author: ellie
"""
from matplotlib import pyplot
from shapely.geometry import Polygon
from shapely.geometry import MultiPolygon
from shapely.geometry import LineString
import shapely.geos
import numpy as np
from descartes import PolygonPatch
from matplotlib.collections import PatchCollection
import math
import time
import gerrymander as gerry
def isoperi(polygon):
    area=polygon.area
    perim=polygon.length
    num=4*math.pi*area
    denom=perim**2
    quo=num/denom
    return quo
def distance(p1,p2):
    return math.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)

# sorts precincts by position with respect to the specified angle
def lineSortPrecincts(precincts,angle):
    sin = math.sin(angle)
    cos = math.cos(angle)
    def dot(pos):
        return cos*pos[0] + sin*pos[1]
    def comp(x,y):
        return cmp(dot(x.position()),dot(y.position()))
    precincts = sorted(precincts,comp)
    return precincts
def landgrab(precincts,districts,startTime=time.time()):
#    print('hi')
    if(districts == 1):
        dist = gerry.District(precincts)
        return [dist]
    print('splitting an area into', districts, 'districts...','at', time.time()-startTime, 'seconds')
    lowAmt = int(districts/2.0)
    ratio = lowAmt/float(districts-lowAmt)

    from random import sample

#    def findFarthest():
#        i=0
#        def findMax(p1):
#            return max((isoperi(p),p) for p in precincts)[1]
#        p1 = sample(precincts,1)[0]
#        ls=[]
#        while i<districts:
#            
#            nextP=findMax(p1)
#            ls.append(nextP)
#            p1=nextP
#            i+=1
#            
#        
#        return ls
#    def findFarthest():
#		def findMax(p1):
#			return max((distance(p.position(),p1.position()),p) for p in precincts)[1]
#		p1 = sample(precincts,1)[0]
#		precinct1 = findMax(p1)
#		precinct2 = findMax(precinct1)
#		return precinct1,precinct2
    def findFarthest():
        precinctsS=sorted(precincts, cmp=lambda x,y: cmp(len(x.adjacent()), len(y.adjacent())))
        hi=precinctsS[1]
        lo=precinctsS[0]
        return hi,lo

    def toTup(district, precinct):
        try:
           
            polygon=district.union(precinct)
            return (1-isoperi(polygon), precinct)
          
        except shapely.geos.TopologicalError:
           return 0
           
           
#        return (-distance(precinct.position(),p1.position()),p1)

    def closestPop():
        precinctsS=sorted(precincts, cmp=lambda x,y: cmp(x.population(), y.population()))
        mid=len(precinctsS)//2
        hi=precinctsS[mid+1]
        lo=precinctsS[mid]
        return hi,lo

    def highestPopDiff():
        hi = max((p.population(),p) for p in precincts)[1]
        lo = min((p.population(),p) for p in precincts)[1]
        return hi,lo

    def highestDensityDiff():
        hi = max((p.population()/p.area,p) for p in precincts)[1]
        lo = min((p.population()/p.area,p) for p in precincts)[1]
        return hi,lo


    def byLineSort():
        from random import random
        angle = random()*2*math.pi
        s = lineSortPrecincts(precincts)
        return s[0],s[-1]
#    precinctList = findFarthest()
    precinct1, precinct2 = closestPop()
#    precinct1, precinct2 = 
    import heapq
    these = set(precincts)
#    d=[]
#    f=[]
#    for p in precinctList:
#        d0=gerry.District([p])
#        f0=[toTup(d0, p2) for p2 in p.adjacent() if p in these]
#        d.append(d0)
#        f.append(f0)
    d1=gerry.District([precinct1])
    d2=gerry.District([precinct2])
    f1 = [toTup(d1,p) for p in precinct1.adjacent() if p in these]
    f2 = [toTup(d2,p) for p in precinct2.adjacent() if p in these]
    heapq.heapify(f1)
    heapq.heapify(f2)
#    for fn in f:
#        heapq.heapify(fn)
#    parts=[]
#    pops=[]
#    for p in precinctList:
#        part=set([p])
#        pop=p.population()
#        parts.append(part)
#        pops.append(pop)
    part1 = set([precinct1])
    part2 = set([precinct2])
    pop1 = precinct1.population()
    pop2 = precinct2.population()
    i=0
    delta=100
    start=50
    def lengthOK():
        for fn in f:
            if (len(fn)>0):
                return True
        return False
    def inParts(nextP):
        for part in parts:
            if nextP in part:
                return True
        return False
                    
                    
#    while lengthOK():
##        if (i>=50 and i%delta==0):
##            checkForEnclaves(unassigned)
#        for d1 in range(districts):
#            f1=f[d1]
#            pop1=pops[d1]
#            part1=parts[d1]
#            for d2 in range(districts):
#                if (d1==d2):
#                    break
#                f2=f[d2]
#                pop2=pops[d2]
#                part2=parts[d2]
#                while((len(f1) == 0 or pop2/float(pop1+1) < 1.0/ratio) and len(f2) > 0):
#                    t=heapq.heappop(f[d2])
#                    print(t)
#                    if (type(t) is int):
#                        continue
#                    nextP = t[1]
#                    if(inParts(nextP)):
#                        continue
#                    parts[d2].add(nextP)
#                    pops[d2] = pops[d2] + nextP.population()
#                    new = [toTup(d[d2],p) for p in nextP.adjacent() if p in these and not inParts(p)]
#                    for p in new:
#                        heapq.heappush(f2,p)
               
#        print 'lengths:','p1:',len(part1),'p2:',len(part2)
    while len(f1) > 0 or len(f2) > 0:
        while((len(f1) == 0 or pop2/float(pop1+1) < 1.0/ratio) and len(f2) > 0):
            t=heapq.heappop(f2)
#            print(t)
            if (type(t) is int):
                break
            nextP = t[1]
            if(nextP in part1 or nextP in part2):
                continue
            part2.add(nextP)
            pop2 = pop2 + nextP.population()
            new = [toTup(precinct1,p) for p in nextP.adjacent() if p in these and p not in part1 and p not in part2]
            for p in new:
                heapq.heappush(f2,p)
        while((len(f2) == 0 or pop1/float(pop2+1) < ratio) and len(f1) > 0):
            t=heapq.heappop(f1)
#            print(t)
            if (type(t) is int):
                break
            nextP = t[1]
            if(nextP in part1 or nextP in part2):
                continue
            part1.add(nextP)
            pop1 = pop1 + nextP.population()
            new = [toTup(precinct2,p) for p in nextP.adjacent() if p in these and p not in part1 and p not in part2]
            for p in new:
                heapq.heappush(f1,p)

    """pop1 = sum(p.population() for p in part1)
    pop2 = sum(p.population() for p in part2)"""
    """lowAmt = (min(pop1,pop2)*districts)/(pop1+pop2)"""
    """if(pop1 > pop2):
        part1, part2 = part2, part1"""
    dists = [gerry.District(part1),gerry.District(part2)]
#    dists=d
#    for dis in range(districts):
#        print('part', str(dis+1),'has pop:', dists[dis].population())
    drawAsher(dists, time.ctime(), '')
    print('part 1 has pop:',dists[0].population(),'part 2 has pop:',dists[1].population())
#    return dists
#    sm=[]
#    for part in parts:
#        sm = sm+landgrab(part, lowAmt, startTime, fileName, title)
#    return sm
    leftSplit = landgrab(part1,lowAmt,startTime)
    rightSplit = landgrab(part2,districts-lowAmt,startTime)
    return leftSplit + rightSplit
def drawLE(districts,  fileName, title):
    mp=shapely.geometry.MultiPolygon([district.asPolygon() for district in districts])
    cm = pyplot.get_cmap('YlOrRd')
    num_colours=len(mp)
##    num_colours = len(mp)
##    p=shapely.geometry.Polygon([(0,0), (1, 0), (1,1)])
##    p.
    fig = pyplot.figure()
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
    pyplot.title(title)
    pyplot.tight_layout()
#    print('heelo')
    pyplot.savefig(fileName+'v1.png', alpha=True, dpi=300)
    pyplot.show()
def drawAsher(result, fileName, title):
    mp = MultiPolygon([district.asPolygon() for district in result])
    fig = pyplot.figure()
    ax = fig.add_subplot(111)
    num_colours = len(result)
    minx, miny, maxx, maxy = mp.bounds
    w, h = maxx - minx, maxy - miny
    ax.set_xlim(minx - 0.1 * w, maxx + 0.1 * w)
    ax.set_ylim(miny - 0.1 * h, maxy + 0.1 * h)
    ax.set_aspect(1)

    maxPop = max(max(precinct.population()/precinct.area for precinct in district.precincts()) for district in result)

    patches = []
    for i in range(len(result)):
	    #patches.append(PolygonPatch(result[i][1], ec='black', lw=1.0, alpha=1, zorder=1))
        color = np.random.rand(3,)
        for polygon in result[i].precincts():
            patches.append(PolygonPatch(polygon, fc=color, alpha=min(pow(float(polygon.population()/polygon.area) / maxPop,1.0/3.0)*4+0.4,1.0), lw=0, zorder=1))
    ax.add_collection(PatchCollection(patches, match_original=True))
    for i in range(len(result)):
        x,y = result[i].asPolygon().exterior.xy
        ax.plot(x, y, color='black', alpha=1,linewidth=1, solid_capstyle='round', zorder=1)
    ax.set_xticks([])
    ax.set_yticks([])
    pyplot.title(title)
    pyplot.tight_layout()
    pyplot.savefig(fileName+'v2.png', alpha=True, dpi=300)
    pyplot.show()