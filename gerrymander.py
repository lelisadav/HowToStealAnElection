
class State:

	def __init__(self,path):
		from shapefile import Reader
		self.r = Reader(path)
		self._points = None
		self._position = None

	def iterPrecincts(self):
		return (Precinct(self,shapeRec) for shapeRec in self.r.iterShapeRecords())

	def precincts(self):
		return list(self.iterPrecincts())

	def bbox(self):
		return self.r.bbox

	def position(self):
		if(self._position != None):
			return self._position
		self._position = centroid(self.points())
		return self._position

	def points(self):
		if(self._points != None):
			return self._points
		from scipy.spatial import ConvexHull
		import numpy
		allUniquePoints = reduce(set.union,(p.points() for p in self.iterPrecincts()),set())
		pointsArr = numpy.array([p for p in allUniquePoints])
		hull = ConvexHull(pointsArr)
		self._points = tuple(tuple(point) for point in hull.points[hull.vertices])
		return self._points

def centroid(points):
	def adjPoints():
		return ((points[x-1],points[x])
			for x
			in xrange(0,len(points)))

	signedArea = 0.5*sum(p[0]*pNext[1] - pNext[0]*p[1]
				for (p, pNext)
				in adjPoints())
	sx = sum((p[0] + pNext[0])*(p[0]*pNext[1] - pNext[0]*p[1])
			for (p, pNext)
			in adjPoints())
	sy = sum((p[1] + pNext[1])*(p[0]*pNext[1] - pNext[0]*p[1])
			for (p, pNext)
			in adjPoints())
	return (sx/(6.0*signedArea),sy/(6.0*signedArea))


class Precinct:

	def __init__(self,state,shapeRecord):
		self._shapeRecord = shapeRecord
		self.state = state
		self._adjacent = None
		self._shapeRecord.shape.points = tuple(tuple(point) for point in self._shapeRecord.shape.points)
		self._position = centroid(self.points())

	def position(self):
		return self._position

	def points(self):
		return tuple(self._shapeRecord.shape.points)

	def population(self):
		return self._shapeRecord.record[20]

	def adjacent(self):
		if(self._adjacent != None):
			return self._adjacent
		points = set(self.points())
		self._adjacent = (p for p in self.state.iterPrecincts() if ((p.position() != self.position()) and len(points.intersection(p.points())) > 0))
		return self._adjacent

# creates a list where the element at index i is equal to the sum
# of all of the precincts at index 0-i
def cumulativePop(precincts):
	retval = [0]*len(precincts)
	for n in xrange(0,len(precincts)):
		retval[n] = retval[n-1] + precincts[n].population()
	return retval

def lineSort(precincts,angle):
	import math
	sin = math.sin(angle)
	cos = math.cos(angle)
	def dot(pos):
		return cos*pos[0] + sin*pos[1]
	return sorted(precincts,lambda x, y: cmp(dot(x.position()),dot(y.position())))

# returns partitions that are splitted by a split line at the specified angle
def splitLine(ratio,precincts,angle):
	from itertools import groupby
	from bisect    import bisect
	from math      import pi
	precincts = lineSort(precincts,angle+pi)  # sort precincts by position along the line
	pops = cumulativePop(precincts)           # get cumulative population for precincts, following the line
	goalAmt = ratio*pops[-1]
	i = bisect(pops,goalAmt)                  # get index that partitions precincts by population by the ratio
	i = min((abs(pops[i]-goalAmt),i),(abs(pops[i-1]-goalAmt),i-1))[1] if i > 0 else i

if __name__ == "__main__":
	import sys
	from matplotlib import pyplot
	state = None
	try:
		state = State(sys.argv[1])
	except IndexError:
		print('specify a shapefile (*.shp) for a state')
		sys.exit(0)

	precincts = state.precincts()
	for rec in r.iterShapeRecords():
		points = rec.shape.points
		cp = centroid(points)
		pyplot.scatter(cp[0],cp[1])
		for p in points:
			pyplot.scatter(p[0],p[1])
		pyplot.show()

