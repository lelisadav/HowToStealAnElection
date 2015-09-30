# -*- coding: utf-8 -*-
"""
Created on Mon Sep 21 13:03:09 2015

@author: ellie
"""
import sys
import math

sys.path.append('/home/ellie/anaconda')
import geopandas
import shapely.geometry
import matplotlib.pyplot as plt
import fiona
import requests
import json
import Astar
import dataObject
import populationDict
from descartes import PolygonPatch
import gerrymander as gerry
from matplotlib.collections import PatchCollection
#def mainIso(save=False):
#
#    mp=shapely.geometry.MultiPolygon([shapely.geometry.shape(pol['geometry']) for pol in fiona.open('data/Texas_VTD.shp')])
#    
#    # We can now do GIS-ish operations on each borough polygon!
#    # we could randomize this by dumping the polygons into a list and shuffling it
#    # or we could define a random colour using fc=np.random.rand(3,)
#    # available colour maps are here: http://wiki.scipy.org/Cookbook/Matplotlib/Show_colormaps
#    cm = plt.get_cmap('YlOrRd')
#    num_colours=5
##    num_colours = len(mp)
##    p=shapely.geometry.Polygon([(0,0), (1, 0), (1,1)])
##    p.
#    fig = plt.figure()
#    ax = fig.add_subplot(111)
#    minx, miny, maxx, maxy = mp.bounds
#    w, h = maxx - minx, maxy - miny
#    ax.set_xlim(minx - 0.2 * w, maxx + 0.2 * w)
#    ax.set_ylim(miny - 0.2 * h, maxy + 0.2 * h)
#    ax.set_aspect(1)
#    
#    patches = []
#    
#    for idx, p in enumerate(mp):
#        quo=isoperi(p)
#        colour=cm(getColour(quo, num_colours))
##        colour = cm(1. * idx / num_colours)
#        patches.append(PolygonPatch(p, fc=colour, ec='#555555', lw=0.2, alpha=1., zorder=1))
#    ax.add_collection(PatchCollection(patches, match_original=True))
#    ax.set_xticks([])
#    ax.set_yticks([])
#    plt.title("Shapefile polygons rendered using Shapely")
#    plt.tight_layout()
#    if (save):
#        plt.savefig('data/texas_by_isoperi_shp.png', alpha=True, dpi=300)
#    plt.show()
#def mainDistricts(save=False):
#
#    mp=shapely.geometry.MultiPolygon([shapely.geometry.shape(pol['geometry']) for pol in fiona.open('data/Texas_VTD.shp')])
#    
#    # We can now do GIS-ish operations on each borough polygon!
#    # we could randomize this by dumping the polygons into a list and shuffling it
#    # or we could define a random colour using fc=np.random.rand(3,)
#    # available colour maps are here: http://wiki.scipy.org/Cookbook/Matplotlib/Show_colormaps
#    cm = plt.get_cmap('Paired')
##    num_colours=5
#    num_colours = len(mp)
##    p=shapely.geometry.Polygon([(0,0), (1, 0), (1,1)])
##    p.
#    fig = plt.figure()
#    ax = fig.add_subplot(111)
#    minx, miny, maxx, maxy = mp.bounds
#    w, h = maxx - minx, maxy - miny
#    ax.set_xlim(minx - 0.2 * w, maxx + 0.2 * w)
#    ax.set_ylim(miny - 0.2 * h, maxy + 0.2 * h)
#    ax.set_aspect(1)
#    
#    patches = []
#    
#    for idx, p in enumerate(mp):
#        #print(p)
#        quo=isoperi(p)
##        colour=cm(getColour(quo, num_colours))
#        colour = cm(1. * idx / num_colours)
#        patches.append(PolygonPatch(p, fc=colour, ec='#555555', lw=0.2, alpha=1., zorder=1))
#    ax.add_collection(PatchCollection(patches, match_original=True))
#    ax.set_xticks([])
#    ax.set_yticks([])
#    plt.title("Shapefile polygons rendered using Shapely")
#    plt.tight_layout()
#    if (save):
#        plt.savefig('data/texas_from_shp.png', alpha=True, dpi=300)
#    plt.show()
#  
#
#def readSplitLine(shapeFile='data/Texas_VTD.shp',name='result.p'):
#    from shapefile import Reader
#    r = Reader(shapeFile)
#    for item in r.iterShapeRecords():
#        print(item.record[1])
#        break
# 
def isoperiHeur(searchState):
    count=len(searchState.districts)
    if (count==0):
        return 0
    ratio=0
    pop=0
    pops=[]
    for d in searchState.districts:
        ratio+=isoperi(d.polygon)
        pop+=d.population
        pops.append(d.population)
    quo= ratio/count
    popquo=pop/count
    popDiff=0
    for p in pops:
        popDiff=abs(p-popquo)
    return quo+popDiff
    
def isoperi(polygon):
    area=polygon.area
    perim=polygon.length
    num=4*math.pi*area
    denom=perim**2
    quo=num/denom
#    print('Quo', quo)
    return quo
def getColour(quo, num_colours):
    rg=1./num_colours
#    print('Num_colours', num_colours)
#    print('Split', rg)
    if (quo//rg==5.0):
        print(5.0)
    return ((quo//rg)/num_colours)+.1
def getPopColour(pop, num_colours, minP, maxP):
    rng=maxP-minP
    section=rng/num_colours
    
    quo=(pop-minP)//section
    
    q2=quo/(1. * num_colours)
#    print(pop, section, quo, q2, num_colours)
    return q2
#    rg=1./num_colours
##    print('Num_colours', num_colours)
##    print('Split', rg)
#    if (quo//rg==5.0):
#        print(5.0)
#    print(pop, quo,((quo//rg)/num_colours)+.1 )
#    return ((quo//rg)/num_colours)+.1

#def getPopulation(block, state, county, tract):
#    url='http://api.census.gov/data/2010/sf1?get=P0010001&for=block:'+block+'&in=state:'+state+'+county:'+county+'+tract:'+tract+'&key=3491625ba162b732cd9cf659d4d4d4aee437c7f5'
#    
##    print(data)    
#    #'http://api.census.gov/data/2010/sf1?key=3491625ba162b732cd9cf659d4d4d4aee437c7f5&get=P0010001,NAME&for=state:'
##    url = 'http://ES_search_demo.com/document/record/_search?pretty=true'
#    #data = '{"query":{"bool":{"must":[{"text":{"record.document":"SOME_JOURNAL"}},{"text":{"record.articleTitle":"farmers"}}],"must_not":[],"should":[]}},"from":0,"size":50,"sort":[],"facets":{}}'
#    response = requests.get(url)
##    print(response.json())
#    if(response.ok):
#
#    # Loading the response data into a dict variable
#    # json.loads takes in only binary or string variables so using content to fetch binary content
#    # Loads (Load String) takes a Json file and converts into python data structure (dict or list, depending on JSON)
#        jData = json.loads(response.content)
#
#        i=0
#        for key in jData:
#            if (i==1):
#                return key[0]
#            i+=1
#            
##            print key + " : " + jData[key]
#    else:
#  # If response code is not ok (200), print the resulting http error code with description
#        response.raise_for_status()
def createPopulationDictTract():
    f453='tract453_shape.json'
    data=fiona.open('data/'+f453)
    pDict=populationDict.PopulationDictTract()
    tDict=dict()
    for pol in data:
    
        odict=pol['properties']
        state=odict['STATEFP10']
        county=odict['COUNTYFP10']
#        tract=odict['TRACTCE10']
        if (not tDict.has_key(county)):
            pDict.fillPopulation(state, county)
            tDict[county]=True
    pDict.writeMaxMin()
    pDict.writeToFile('data/populationsTract.json')
def createPopulationDictBlock():
    f453='block453_shape.json'
    data=fiona.open('data/'+f453)
    pDict=populationDict.PopulationDictBlock()
    tDict=dict()
    for pol in data:
    
        odict=pol['properties']
        state=odict['STATEFP10']
        county=odict['COUNTYFP10']
        tract=odict['TRACTCE10']
        if (not tDict.has_key(county+tract)):
            pDict.fillPopulation(state, county, tract)
            tDict[county+tract]=True
    pDict.writeMaxMin()
    pDict.writeToFile('data/populationsBlock.json')
def createPopulationDictCounty():
    f453='county_shape.json'
    data=fiona.open('data/'+f453)
    pDict=populationDict.PopulationDictCounty()
    pDict.fillPopulation('48')
    pDict.writeMaxMin()
    pDict.writeToFile('data/populationsCounty.json')
        
def mainIsoTest(save=False):
#    f209='tl_2010_48209_tabblock00.shp'
     f453='Texas_VTD.shp'
    #fpop='tabblock2010_48_pophu.shp'
    
#    f491='block453_shape.json'
#    f209='block209_shape.json'
#    f453='block453_shape.json'
#    f491='block491_shape.json'
     f='precincts'
#    data= fiona.open('data/texas.json')
#    i=0
#    for pol in data:
        
#    data=fiona.open('data/tl_2013_48_place.shp', 'r')
#    print(data.items)
#    for f in data:
#        print(f)
#    
#    
#    mp453=shapely.geometry.MultiPolygon([shapely.geometry.shape(pol['geometry']) for pol in fiona.open('data/'+f453)])
##    print(data.schema)
#    mp209=shapely.geometry.MultiPolygon([shapely.geometry.shape(pol['geometry']) for pol in fiona.open('data/'+f209)])
#     data=gerry.State('data/'+f453, [453, 491, 209])
     number=3
     data=gerry.State('data/'+f453)
     data.buildGraph()
     precincts = data.precincts()
     import landgrab
     import time
     fileName='data/results/texasVTD'+time.ctime()
     title='Texas voting districts'
     dists=landgrab.landgrab(precincts, 8,time.time())
     landgrab.drawAsher(dists, fileName, title)
##     dists2a=landgrab.landgrab(dists[0].precincts(), 2, time.time())
##     landgrab.drawAsher(dists2a, fileName+'2a', title)
#     dists2b=landgrab.landgrab(dists[1].precincts(), 2, time.time())
#     landgrab.drawAsher(dists2b, fileName+'2b', title)
#     dists2ba=landgrab.landgrab(dists2b[0].precincts(), 2, time.time())
#     landgrab.drawAsher(dists2ba, fileName+'2ba', title)
#     dists2bb=landgrab.landgrab(dists2b[1].precincts(), 2, time.time())
#     landgrab.drawAsher(dists2bb, fileName+'2bb', title)
     
    
#     landgrab.drawAsher(ls, fileName, title)
#     landgrab.drawLE(ls, fileName, title)
#     i+=1

#     objects=[]
##     polygons=[]
#    
#    
#    
#     for pol in data.precincts():
#         
#         objects.append(pol)
#         polygons.append(obj.polygon)
#    minP=pDict.getMin()
#    maxP=pDict.getMax()
#    print(minP)
#    print(maxP)
#    mp453=shapely.geometry.MultiPolygon(polygons)
#       
##        mp453=shapely.geometry.MultiPolygon([shapely.geometry.shape(pol['geometry']) for pol in fiona.open('data/'+f453)])
##    mp491=shapely.geometry.MultiPolygon([shapely.geometry.shape(pol['geometry']) for pol in fiona.open('data/'+f491)])
##    mp209=shapely.geometry.MultiPolygon([shapely.geometry.shape(pol['geometry']) for pol in fiona.open('data/'+f209)])
##    mp453=shapely.geometry.MultiPolygon([shapely.geometry.shape(pol['geometry']) for pol in fiona.open('data/'+f453)])
##    mp491=shapely.geometry.MultiPolygon([shapely.geometry.shape(pol['geometry']) for pol in fiona.open('data/'+f491)])
##    
#    # We can now do GIS-ish operations on each borough polygon!
#    # we could randomize this by dumping the polygons into a list and shuffling it
#    # or we could define a random colour using fc=np.random.rand(3,)
#    # available colour maps are here: http://wiki.scipy.org/Cookbook/Matplotlib/Show_colormaps
#    cm = plt.get_cmap('YlOrRd')
#    num_colours=5
##    num_colours = len(mp)
##    p=shapely.geometry.Polygon([(0,0), (1, 0), (1,1)])
##    p.
#    fig = plt.figure()
#    ax = fig.add_subplot(111)
#    
##    minx9, miny9, maxx9, maxy9 = mp209.bounds
##    minx3, miny3, maxx3, maxy3 = mp453.bounds
##    minx1, miny1, maxx1, maxy1 = mp491.bounds
##    minx=min(minx9, minx3, minx1)
##    miny= min(miny9, miny3, miny1)
##    maxx=max(maxx9, maxx3, maxx1)
##    maxy =max(maxy9, maxy3, maxy1)
#    minx, miny, maxx, maxy = mp453.bounds
#    
#    w, h = maxx - minx, maxy - miny
#    ax.set_xlim(minx - 0.2 * w, maxx + 0.2 * w)
#    ax.set_ylim(miny - 0.2 * h, maxy + 0.2 * h)
#    ax.set_aspect(1)
#    
#    patches = []
##    
##    for idx, p in enumerate(mp209):
##        quo=isoperi(p)
##        colour=cm(getColour(quo, num_colours))
###        colour = cm(1. * idx / num_colours)
##        patches.append(PolygonPatch(p, fc=colour, ec='#555555', lw=0.2, alpha=1., zorder=1))
#    for idx, obj in enumerate(objects):
#        p=obj.polygon
##        print(obj.population)
##        print(obj.population)
##        quo=isoperi(p)
#        colour=cm(1. * getPopColour(obj.population, num_colours, minP, maxP))
##        colour = cm(1. * idx / num_colours)
#        patches.append(PolygonPatch(p, fc=colour, ec='#555555', lw=0.2, alpha=1., zorder=1))
##    for idx, p in enumerate(mp491):
##        quo=isoperi(p)
##        colour=cm(getColour(quo, num_colours))
###        colour = cm(1. * idx / num_colours)
##        patches.append(PolygonPatch(p, fc=colour, ec='#555555', lw=0.2, alpha=1., zorder=1))
#        
#    ax.add_collection(PatchCollection(patches, match_original=True))
#    ax.set_xticks([])
#    ax.set_yticks([])
#    plt.title("Shapefile polygons rendered using Shapely")
#    plt.tight_layout()
##    print('heelo')
#    if (save):
#        plt.savefig('data/results/texas_'+f+'.png', alpha=True, dpi=300)
#    plt.show()
#    ds=districtingState(polygons)
#     showSearchResults(Astar.search(objects, number,heuristic=isoperiHeur))

def testing():
    p1=dataObject.DummyDataObject(shapely.geometry.Polygon([(0,0), (0,1), (.5,.5)]))
    p1a=dataObject.DummyDataObject(shapely.geometry.Polygon([(0,1), (.5, .5), (1,1)]))
    p2=dataObject.DummyDataObject(shapely.geometry.Polygon([(.5,.5), (1, 1), (1, 0)]))
    p2a=dataObject.DummyDataObject(shapely.geometry.Polygon([(1, 0), (1,1), (1.5, .5)]))
    p3=dataObject.DummyDataObject(shapely.geometry.Polygon([(0,0), (.5, .5), (1,0)]))
    p3a=dataObject.DummyDataObject(shapely.geometry.Polygon([(0,0),  (.5, -.5), (1, 0)]))
    
    showSearchResults(Astar.search([p1, p1a, p2, p2a, p3, p3a], 2, heuristic=isoperiHeur))
    
        

def showSearchResults(searchState, save=True):
    polygons=[]
    for district in searchState.districts:
        polygons.append(district.polygon)
    mp=shapely.geometry.MultiPolygon(polygons)
    cm = plt.get_cmap('YlOrRd')
    num_colours=len(searchState.districts)
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
    for idx, dis in enumerate(searchState.districts):
        for p in dis.areas:
    
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
    
        

#print(getPopulation('1213','02', '290', '00100'))
#createPopulationDictCounty()
#print('Done')
#mainIsoTest(save=True, tract=True)
#createPopulationDictBlock()
#print('Done')
#testing()
#readSplitLine()
mainIsoTest(save=True)
#mainIso()
#mainDistricts()