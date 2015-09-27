numDistricts = 36
numSamples = 359
shapefile = 'Texas_VTD.shp'

print 'importing stuff...'
import gerrymander as gerry
from matplotlib import pyplot
from descartes import PolygonPatch
import numpy as np
from matplotlib.collections import PatchCollection
from shapely.geometry import MultiPolygon
import time
import cPickle as pickle
import os.path

start = time.time()

print 'processing shapefile', shapefile, '...', 'at', time.time()-start, 'seconds'
texas = gerry.State('data/' + shapefile)

if os.path.isfile("result.p"):
    print 'pickle file found in result.p, now opening...','at', time.time()-start, 'seconds'
    input = open("result.p","rb")
    result = pickle.load(input)
    input.close()
    print 'done loading pickle, now drawing...','at', time.time()-start, 'seconds'

else:
    print 'calculating',numDistricts,'district partion via shortest splitline algorithm with',numSamples,'angle samples...','at', time.time()-start, 'seconds'
    result = gerry.shortestSplitLine(texas.precincts(),numDistricts,None,numSamples,False,start)
    print 'done with calculations, now pickling...','at', time.time()-start, 'seconds'
    output = open( "result.p", "wb" )
    pickle.dump( result, output, pickle.HIGHEST_PROTOCOL)
    output.close()
    print 'done pickling, now drawing...','at', time.time()-start, 'seconds'


mp = MultiPolygon([district for (_, district) in result])
fig = pyplot.figure()
ax = fig.add_subplot(111)
num_colours = len(result)
minx, miny, maxx, maxy = mp.bounds
w, h = maxx - minx, maxy - miny
ax.set_xlim(minx - 0.1 * w, maxx + 0.1 * w)
ax.set_ylim(miny - 0.1 * h, maxy + 0.1 * h)
ax.set_aspect(1)

maxPop = max([precinct.population() for precinct in texas.precincts()])

popDict = {(precinct.centroid.x,precinct.centroid.y): precinct.population() for precinct in texas.precincts()}

patches = []
for i in range(len(result)):
    #patches.append(PolygonPatch(result[i][1], ec='black', lw=1.0, alpha=1, zorder=1))
    color = np.random.rand(3,)
    for polygon in result[i][0]:
        patches.append(PolygonPatch(polygon, fc=color, alpha= pow(float(popDict[(polygon.centroid.x,polygon.centroid.y)]) / maxPop,1.0/3), lw=0, zorder=1))

ax.add_collection(PatchCollection(patches, match_original=True))
for i in range(len(result)):
    x,y = result[i][1].exterior.xy
    ax.plot(x, y, color='black', alpha=1,linewidth=2, solid_capstyle='round', zorder=1)
ax.set_xticks([])
ax.set_yticks([])
pyplot.title(shapefile + ' shortest splitline')
pyplot.tight_layout()
print 'All done','at', time.time()-start, 'seconds'
pyplot.show()
