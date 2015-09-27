from matplotlib import pyplot
from descartes import PolygonPatch
import numpy as np
from matplotlib.collections import PatchCollection
from shapely.geometry import MultiPolygon, Polygon

fig = pyplot.figure()
ax = fig.add_subplot(111)
minx, miny, maxx, maxy = 0, 0, 5, 5
w, h = maxx - minx, maxy - miny
ax.set_xlim(minx - 0.1 * w, maxx + 0.1 * w)
ax.set_ylim(miny - 0.1 * h, maxy + 0.1 * h)
ax.set_aspect(1)

poly = Polygon([(1,2), (3,4), (3, 2)])

import os.path
print os.path.isfile("result.p") 

patches = []
patches.append(PolygonPatch(poly, fc='red', lw=0, alpha=1, zorder=2))
ax.add_collection(PatchCollection(patches, match_original=True))
x, y = poly.exterior.xy
ax.plot(x, y, color='black', alpha=1,linewidth=2, solid_capstyle='round', zorder=1)
ax.set_xticks([])
ax.set_yticks([])
pyplot.tight_layout()
pyplot.show()
