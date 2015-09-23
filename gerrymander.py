#! /usr/bin/env python2

from matplotlib import pyplot

class State:

	def __init__(self,path):
		from shapefile import Reader
		self.r = Reader(path)
		self._points = None
		self._position = None
		self.r.bbox = tuple(self.r.bbox)
		self._precincts = tuple(Precinct(self,shapeRec) for shapeRec in self.r.iterShapeRecords())

	def iterPrecincts(self):
		return iter(self._precincts)

	def precincts(self):
		return self._precincts

	def bbox(self):
		return self.r.bbox

	def position(self):
		if(self._position != None):
			return self._position
		self._position = centroid(self.points())
		return self._position

	def splitLine(self,ratio,angle):
		return splitLine(ratio,self.iterPrecincts(),angle);

	# calculates every precinct's adjacent precincts, much faster than relying on each precinct to lazily evaluate
	# their adjacent precincts when using Precinct.adjacent() on a lot of precincts.
	def buildGraph(self):

		# get corner points from bounding box
		def points(bbox):
			minX, minY, maxX, maxY = bbox
			return [(minX,minY),(minX,maxY),(maxX,minY),(maxX,maxY)]

		# returns True if the point is inside or on the bounding box
		def contains(bbox,point):
			minX, minY, maxX, maxY = bbox
			x,y = point
			return x >= minX and x <= maxX and y >= minY and y <= maxY

		# returns True if the bounding boxes intersect
		def intersects(bbox1,bbox2):
			for p in points(bbox1):
				if(contains(bbox2, p)):
					return True
			for p in points(bbox2):
				if(contains(bbox1, p)):
					return True
			return False

		# brute force builds the graph by checking every pair in the list of precincts
		def baseBuild(precincts):
			for i in xrange(len(precincts)):
				precinct = precincts[i]
				points = set(precinct.points())
				for j in xrange(i+1,len(precincts)):
					oPrecinct = precincts[j]
					if(not intersects(precinct.bbox(),oPrecinct.bbox())):
						continue
					if(points.isdisjoint(oPrecinct.points())):
						continue
					oPrecinct._adjacent.append(precinct)
					precinct._adjacent.append(oPrecinct)

		# builds the graph by checking for adjacency between precincts paired together from seperate lists
		def mergeBuild(ps1,ps2):
			for p1 in ps1:
				points = set(p1.points())
				for p2 in ps2:
					if(not intersects(p1.bbox(),p2.bbox())):
						continue
					if(points.isdisjoint(p2.points())):
						continue
					p1._adjacent.append(p2)
					p2._adjacent.append(p1)

		# builds the graph by recursively splitting lists of precincts into shorter lists based on their
		# bounding boxes. Once the list of precincts is small enough, baseBuild is used to build the graph
		def recursiveBuild(bbox,precincts):
			if(len(precincts) <= 16):
				baseBuild(precincts)
				return
			minX, minY, maxX, maxY = bbox
			splitX   = (maxX+minX)/2
			splitY   = (maxY+minY)/2
			topLeft  = []
			topRight = []
			botLeft  = []
			botRight = []
			midLeft  = []
			midRight = []
			topMid   = []
			botMid   = []
			mid      = []
			for precinct in precincts:
				minX, minY, maxX, maxY = precinct.bbox()
				if(minX <= splitX):
					if(maxX >= splitX):
						if(minY <= splitY):
							if(maxY >= splitY):
								mid.append(precinct)
							else:
								botMid.append(precinct)
						else:
							topMid.append(precinct)
					elif(minY <= splitY):
						if(maxY >= splitY):
							midLeft.append(precinct)
						else:
							botLeft.append(precinct)
					else:
						topLeft.append(precinct)
				elif(minY <= splitY):
					if(maxY >= splitY):
						midRight.append(precinct)
					else:
						botRight.append(precinct)
				else:
					topRight.append(precinct)
			
			recursiveBuild((minX,minY,splitX,splitY),botLeft)
			recursiveBuild((splitX,splitY,maxX,maxY),topRight)
			recursiveBuild((minX,splitY,splitX,maxY),topLeft)
			recursiveBuild((splitX,minY,maxX,splitY),botRight)
			for ps in (topMid,botMid,midLeft,midRight,mid):
				baseBuild(ps)
			for ps in (topMid,botMid,midLeft,midRight):
				mergeBuild(ps,mid)
			for vertMid in (topMid,botMid):
				for horizMid in (midLeft,midRight):
					mergeBuild(vertMid,horizMid)
			for ps in (midLeft,mid,botMid):
				mergeBuild(ps,botLeft)
			for ps in (midLeft,mid,topMid):
				mergeBuild(ps,topLeft)
			for ps in (midRight,mid,botMid):
				mergeBuild(ps,botRight)
			for ps in (midRight,mid,topMid):
				mergeBuild(ps,topRight)

		precincts = self.precincts()
		for p in precincts:
			p._adjacent = []
		recursiveBuild(self.bbox(),precincts)
		for p in precincts:
			p._adjacent = tuple(p._adjacent)

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
		self._shapeRecord.shape.bbox = tuple(self._shapeRecord.shape.bbox)
		self._position = centroid(self.points())

	def position(self):
		return self._position

	def points(self):
		return tuple(self._shapeRecord.shape.points)

	def population(self):
		return self._shapeRecord.record[20]

	def bbox(self):
		return self._shapeRecord.shape.bbox

	def adjacent(self):
		if(self._adjacent != None):
			return self._adjacent
		points = set(self.points())
		self._adjacent = tuple(p for p in self.state.iterPrecincts() if ((p.position() != self.position()) and len(points.intersection(p.points())) > 0))
		return self._adjacent

# creates a list where the element at index i is equal to the sum
# of all of the precincts at index 0 to i
def cumulativePop(precincts):
	retval = [0]*len(precincts)
	for n in xrange(0,len(precincts)):
		retval[n] = retval[n-1] + precincts[n].population()
	return retval

# sorts precincts by position with respect to the specified angle
def lineSort(precincts,angle,mutate=False):
	import math
	sin = math.sin(angle)
	cos = math.cos(angle)
	def dot(pos):
		return cos*pos[0] + sin*pos[1]
	def comp(x,y):
		return cmp(dot(x.position()),dot(y.position()))
	if(mutate):
		precincts.sort(comp)
	else:
		precincts = sorted(precincts,comp)
	return precincts

def plotPoints(points,color='b'):
	for p in points:
		pyplot.scatter(p[0],p[1],c=color)

def plotPrecincts(ps,color='b'):
	for p in ps:
		pos = p.position()
		pyplot.scatter(pos[0],pos[1],c=color)

def plotPrecinctsPoints(ps,color='b'):
	for p in ps:
		for point in p.points():
			pyplot.scatter(point[0],point[1],c=color)

# returns partitions that are splitted by a split line at the specified angle and ratio
def splitLine(ratio,precincts,angle,mutate=False):
	from bisect    import bisect
	from math      import pi
	precincts = lineSort(precincts,angle+pi/2,mutate)
	pops = cumulativePop(precincts)           # get cumulative population for precincts, following the line
	goalAmt = ratio*pops[-1]
	i = bisect(pops,goalAmt)                  # get index that partitions precincts by population by the ratio
	i = min((abs(pops[i]-goalAmt),i),(abs(pops[i-1]-goalAmt),i-1))[1] if i > 0 else i
	return (precincts[0:i+1], precincts[i+1::])


if __name__ == "__main__":
	import sys
	state = None
	try:
		state = State(sys.argv[1])
	except IndexError:
		print('specify a shapefile (*.shp) for a state')
		sys.exit(0)

	print "building graph"
	state.buildGraph()
	precincts = state.precincts()
	for p in precincts:
		plotPrecinctsPoints(p.adjacent(),'b')
		plotPrecincts(p.adjacent(),'black')
		plotPrecinctsPoints([p],'r')
		plotPrecincts([p],'black')
		pyplot.show()

