# -*- coding: utf-8 -*-
"""
Created on Mon Sep 21 13:03:09 2015

@author: ellie
"""
import sys
import math
sys.path.append('/home/ellie/anaconda')
import shapely.geometry
import matplotlib.pyplot as plt
import fiona
from descartes import PolygonPatch
from matplotlib.collections import PatchCollection
def mainIso(save=false):

    mp=shapely.geometry.MultiPolygon([shapely.geometry.shape(pol['geometry']) for pol in fiona.open('data/Texas_VTD.shp')])
    
    # We can now do GIS-ish operations on each borough polygon!
    # we could randomize this by dumping the polygons into a list and shuffling it
    # or we could define a random colour using fc=np.random.rand(3,)
    # available colour maps are here: http://wiki.scipy.org/Cookbook/Matplotlib/Show_colormaps
    cm = plt.get_cmap('YlOrRd')
    num_colours=5
#    num_colours = len(mp)
#    p=shapely.geometry.Polygon([(0,0), (1, 0), (1,1)])
#    p.
    fig = plt.figure()
    ax = fig.add_subplot(111)
    minx, miny, maxx, maxy = mp.bounds
    w, h = maxx - minx, maxy - miny
    ax.set_xlim(minx - 0.2 * w, maxx + 0.2 * w)
    ax.set_ylim(miny - 0.2 * h, maxy + 0.2 * h)
    ax.set_aspect(1)
    
    patches = []
    
    for idx, p in enumerate(mp):
        quo=isoperi(p)
        colour=cm(getColour(quo, num_colours))
#        colour = cm(1. * idx / num_colours)
        patches.append(PolygonPatch(p, fc=colour, ec='#555555', lw=0.2, alpha=1., zorder=1))
    ax.add_collection(PatchCollection(patches, match_original=True))
    ax.set_xticks([])
    ax.set_yticks([])
    plt.title("Shapefile polygons rendered using Shapely")
    plt.tight_layout()
    if (save):
        plt.savefig('data/texas_by_isoperi_shp.png', alpha=True, dpi=300)
    plt.show()
def mainDistricts(save=false):

    mp=shapely.geometry.MultiPolygon([shapely.geometry.shape(pol['geometry']) for pol in fiona.open('data/Texas_VTD.shp')])
    
    # We can now do GIS-ish operations on each borough polygon!
    # we could randomize this by dumping the polygons into a list and shuffling it
    # or we could define a random colour using fc=np.random.rand(3,)
    # available colour maps are here: http://wiki.scipy.org/Cookbook/Matplotlib/Show_colormaps
    cm = plt.get_cmap('Paired')
#    num_colours=5
    num_colours = len(mp)
#    p=shapely.geometry.Polygon([(0,0), (1, 0), (1,1)])
#    p.
    fig = plt.figure()
    ax = fig.add_subplot(111)
    minx, miny, maxx, maxy = mp.bounds
    w, h = maxx - minx, maxy - miny
    ax.set_xlim(minx - 0.2 * w, maxx + 0.2 * w)
    ax.set_ylim(miny - 0.2 * h, maxy + 0.2 * h)
    ax.set_aspect(1)
    
    patches = []
    
    for idx, p in enumerate(mp):
        #print(p)
        quo=isoperi(p)
#        colour=cm(getColour(quo, num_colours))
        colour = cm(1. * idx / num_colours)
        patches.append(PolygonPatch(p, fc=colour, ec='#555555', lw=0.2, alpha=1., zorder=1))
    ax.add_collection(PatchCollection(patches, match_original=True))
    ax.set_xticks([])
    ax.set_yticks([])
    plt.title("Shapefile polygons rendered using Shapely")
    plt.tight_layout()
    if (save):
        plt.savefig('data/texas_from_shp.png', alpha=True, dpi=300)
    plt.show()
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

mainIso()
mainDistricts()