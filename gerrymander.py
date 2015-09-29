#! /usr/bin/env python2

from matplotlib import pyplot
from shapely.geometry import Polygon
from shapely.geometry import MultiPolygon
from shapely.geometry import LineString
import math
import time
import heapq
from random import random, sample

class State(MultiPolygon):

	def __init__(self,path):
		from shapefile import Reader
		r = Reader(path)
		self._precincts = tuple(Precinct(shapeRec) for shapeRec in r.iterShapeRecords())
		self._polygon = None
		MultiPolygon.__init__(self,self._precincts)

	def asPolygon(self):
		if(self._polygon == None):
			poly = self.buffer(0)
			if(poly.type != 'Polygon'):
				raise ValueError('state has invalid shape')
			self._polygon = poly
		return self._polygon

	def plot(self,fig=pyplot,color='b'):
		poly = self.asPolygon()
		xs,ys = poly.exterior.xy
		fig.plot(xs,ys,color=color)

	def population(self):
		return sum(p.population() for p in self._precincts)

	def position(self):
		return self.centroid.coords[0]

	def iterPrecincts(self):
		return iter(self._precincts)

	def precincts(self):
		return self._precincts

	def shortestSplitLine(self,districts,sample):
		return shortestSplitLine(self.precincts(),districts,self.asPolygon(),sample)

	def splitLine(self,ratio,angle):
		return SplitLine(self._precincts,ratio,angle,self.buffer(0)) # we may want to store the polygon version of texas

	# calculates every precinct's adjacent precincts, much faster than relying on
	# each precinct to lazily evaluate their adjacent precincts when using
	# Precinct.adjacent() on a lot of precincts.
	def buildGraph(self,capacity=16):

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
				for j in xrange(i+1,len(precincts)):
					oPrecinct = precincts[j]
					if(not intersects(precinct[0],oPrecinct[0])):
						continue
					if(len(precinct[1].intersection(oPrecinct[1])) < 2):
						continue
					oPrecinct[3].append(precinct[2])
					precinct[3].append(oPrecinct[2])

		# builds the graph by checking for adjacency between precincts paired together
		# from seperate lists
		def mergeBuild(ps1,ps2):
			for p1 in ps1:
				for p2 in ps2:
					if(not intersects(p1[0],p2[0])):
						continue
					if(len(p1[1].intersection(p2[1])) < 2):
						continue
					p1[3].append(p2[2])
					p2[3].append(p1[2])

		def vertBuild(ps):
			def vertSort(x,y):
				return cmp(x[0][1],y[0][1])
			ps.sort(vertSort)
			for lo in xrange(len(ps)-1):
				loP = ps[lo]
				for hi in xrange(lo+1,len(ps)):
					hiP = ps[hi]
					if(hiP[0][1] > loP[0][3]):
						break
					if(len(hiP[1].intersection(loP[1])) < 2):
						continue
					loP[3].append(hiP[2])
					hiP[3].append(loP[2])

		def horizBuild(ps):
			def horizSort(x,y):
				return cmp(x[0][0],y[0][0])
			ps.sort(horizSort)
			for left in xrange(len(ps)-1):
				leftP = ps[left]
				for right in xrange(left+1,len(ps)):
					rightP = ps[right]
					if(rightP[0][0] > leftP[0][2]):
						break
					if(len(leftP[1].intersection(rightP[1])) < 2):
						continue
					leftP[3].append(rightP[2])
					rightP[3].append(leftP[2])

		# builds the graph by recursively splitting lists of precincts into shorter lists based
		# on their bounding boxes. Once the list of precincts is small enough, baseBuild is used
		# to build the graph
		def recursiveBuild(bbox,precincts):
			if(len(precincts) <= capacity):
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
				minX, minY, maxX, maxY = precinct[0]
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
			for ps in (topMid,botMid,mid):
				vertBuild(ps)
			for ps in (midLeft,midRight):
				horizBuild(ps)
			for ps in (topMid,botMid,midLeft,midRight):
				mergeBuild(mid,ps)
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

		tups = [(p.bounds,set(p.points()),p,[]) for p in self.precincts()]
		recursiveBuild(self.bounds,tups)
		for p in tups:
			p[2]._adjacent = tuple(p[3])

class Precinct(Polygon):

	def __init__(self,shapeRecord=None):
		if(shapeRecord == None):
			return
		self._record = shapeRecord.record
		self._adjacent = None
		Polygon.__init__(self,shapeRecord.shape.points + shapeRecord.shape.points[-1:])

	def population(self):
		return self._record[20]

	def position(self):
		return self.centroid.coords[0];

	def points(self):
		return self.exterior.coords

	def adjacent(self):
		if(self._adjacent != None):
			return self._adjacent
		points = set(self.points())
		self._adjacent = tuple(p for p in self.state.iterPrecincts() if ((p.position() != self.position()) and len(points.intersection(p.points())) > 0))
		return self._adjacent

	def plot(self,fig=pyplot,color='blue'):
		xs,ys = self.exterior.xy
		fig.plot(xs,ys,color,linewidth='3')

def readFile(shapeFile='data/Texas_VTD.shp',name='result.p'):
	import cPickle
	state = State(shapeFile)
	cToP = dict(((precinct.centroid.x,precinct.centroid.y),precinct) for precinct in state.precincts())
	result = cPickle.load(open(name,'rb'))
	dists = []
	for dTup in result:
		precincts = tuple(cToP[(p.centroid.x,p.centroid.y)] for p in dTup)
		d = District(precincts)
		dists.append(d)
	return tuple(dists)

class District(MultiPolygon):

	def __init__(self,precincts = None):
		self._polygon = None
		if(precincts != None):
			self._precincts = tuple(precincts)
			MultiPolygon.__init__(self,self._precincts)

	def asPolygon(self):
		if(self._polygon == None):
			poly = self.buffer(0)
			if(poly.type != 'Polygon'):
				raise ValueError('district has invalid shape')
			self._polygon = poly
		return self._polygon

	def precincts(self):
		return self._precincts

	def population(self):
		return sum(p.population() for p in self._precincts)

	def plot(self,fig=pyplot,color='b'):
		poly = self.asPolygon()
		xs, ys = poly.exterior.xy
		fig.plot(xs,ys,color=color)

	def isoperimetricRatio(self):
		poly = self.asPolygon()
		area = poly.area
		perim = poly.exterior.length
		return 4*math.pi*area/(perim**2)

def shortestSplitLineJagged(precincts,districts,poly=None,sample=1,startTime=time.time()):
	if(districts == 1):
		dist = District(precincts)
		dist._polygon = poly
		return (dist,)
	if(poly == None):
		print 'merging precincts to get outside border...','at', time.time()-startTime, 'seconds'
		poly = MultiPolygon(precincts).buffer(0)
	print 'splitting an area into', districts, 'districts...','at', time.time()-startTime, 'seconds'
	lowAmt = int(districts/2.0)
	ratio = lowAmt/float(districts)
	smallest = None
	for angle in (i*2*math.pi/sample for i in xrange(sample)):
		# print 'trying split line at angle', angle
		try:
			spl = SplitLine(precincts,ratio,angle,poly)
		except ValueError:
			print 'value error for angle:',angle,'with ratio',ratio
			continue

		if(smallest == None or spl.length < smallest.length):
			c1 = MultiPolygon(spl.leftPart).buffer(0)
			c2 = MultiPolygon(spl.rightPart).buffer(0)
			if(c1.type == 'Polygon' and c2.type == 'Polygon'):
				child1 = c1
				child2 = c2
				smallest = spl
			else:
				print 'too many partitions'
				continue
	leftChild, rightChild = None, None
	if(child1.contains(smallest.leftPart[len(smallest.leftPart)/2].centroid)):
		leftChild, rightChild = child1, child2
	else:
		rightChild, leftChild = child1, child2
	leftSplit = shortestSplitLineJagged(smallest.leftPart,lowAmt,leftChild,sample,startTime)
	rightSplit = shortestSplitLineJagged(smallest.rightPart,districts-lowAmt,rightChild,sample,startTime)
	return leftSplit + rightSplit


def shortestSplitLine(precincts,districts,poly=None,sample=1,angleStart=0,startTime=time.time()):
	if(districts == 1):
		dist = District(precincts)
		dist._polygon = poly
		return (dist,)
	if(poly == None):
		print 'merging precincts to get outside border...','at', time.time()-startTime, 'seconds'
		poly = MultiPolygon(precincts).buffer(0)
	print 'splitting an area into', districts, 'districts...','at', time.time()-startTime, 'seconds'
	lowAmt = int(districts/2.0)
	ratio = lowAmt/float(districts)
	smallest = None
	for angle in (i*2*math.pi/sample + angleStart for i in xrange(sample)):
		# print 'trying split line at angle', angle
		try:
			spl = SplitLine(precincts,ratio,angle,poly)
		except ValueError:
			print 'value error for angle:',angle,'with ratio',ratio
			continue

		if(smallest == None or spl.length < smallest.length):
			try:
				child1, child2 = tuple(poly.difference(spl.buffer(0.000000001)).geoms)
				smallest = spl
			except ValueError:
				print 'too many partitions'
				continue
	leftChild, rightChild = None, None
	if(child1.contains(smallest.leftPart[len(smallest.leftPart)/2].centroid)):
		leftChild, rightChild = child1, child2
	else:
		rightChild, leftChild = child1, child2
	leftSplit = shortestSplitLine(smallest.leftPart,lowAmt,leftChild,sample,angleStart,startTime)
	rightSplit = shortestSplitLine(smallest.rightPart,districts-lowAmt,rightChild,sample,angleStart,startTime)
	return leftSplit + rightSplit

def landgrab(precincts,districts,startTime=time.time()):
	if(districts == 1):
		dist = District(precincts)
		return (dist,)
	print 'splitting an area into', districts, 'districts...','at', time.time()-startTime, 'seconds'
	lowAmt = int(districts/2.0)
	ratio = lowAmt/float(districts-lowAmt)

	def findFarthest():
		def findMax(p1):
			return max((distance(p.position(),p1.position()),p) for p in precincts)[1]
		p1 = sample(precincts,1)[0]
		precinct1 = findMax(p1)
		precinct2 = findMax(precinct1)
		return precinct1,precinct2

	def toTup(precinct,p1):
		return (-distance(precinct.position(),p1.position()),p1)

	def highestPopDiff():
		hi = max((p.population(),p) for p in precincts)[1]
		lo = min((p.population(),p) for p in precincts)[1]
		return hi,lo

	def highestDensityDiff():
		hi = max((p.population()/p.area,p) for p in precincts)[1]
		lo = min((p.population()/p.area,p) for p in precincts)[1]
		return hi,lo


	def byLineSort():
		
		angle = random()*2*math.pi
		s = lineSortPrecincts(precincts, angle)
		return s[0],s[-1]
	precinct1,precinct2 = findFarthest()

	
	these = set(precincts)
	f1 = [toTup(precinct2,p) for p in precinct1.adjacent() if p in these]
	f2 = [toTup(precinct1,p) for p in precinct2.adjacent() if p in these]
	heapq.heapify(f1)
	heapq.heapify(f2)
	part1 = set([precinct1])
	part2 = set([precinct2])
	pop1 = precinct1.population()
	pop2 = precinct2.population()
	while len(f1) > 0 or len(f2) > 0:
		#print 'lengths:','p1:',len(part1),'p2:',len(part2)
		while((len(f1) == 0 or pop2/float(pop1+1) < 1.0/ratio) and len(f2) > 0):
			nextP = heapq.heappop(f2)[1]
			if(nextP in part1 or nextP in part2):
				continue
			part2.add(nextP)
			pop2 = pop2 + nextP.population()
			new = [toTup(precinct1,p) for p in nextP.adjacent() if p in these and p not in part1 and p not in part2]
			for p in new:
				heapq.heappush(f2,p)
		while((len(f2) == 0 or pop1/float(pop2+1) < ratio) and len(f1) > 0):
			nextP = heapq.heappop(f1)[1]
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

	#dists = [District(part1),District(part2)]
	#print 'part 1 has pop:',dists[0].population(),'part 2 has pop:',dists[1].population()
	#import asher_script
	#asher_script.draw(dists)
	leftSplit = landgrab(part1,lowAmt,startTime)
	rightSplit = landgrab(part2,districts-lowAmt,startTime)
	return leftSplit + rightSplit

def plotParts(parts,colors=None,fig=pyplot):
	for (part,color) in zip(parts,colors):
		for p in part:
			p.plot(fig,color)

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

class SplitLine(LineString):

	def __init__(self,precincts,ratio,angle,polygon = None):

		# creates a list where the element at index i is equal to the sum
		# of all of the precincts at index 0 to i
		def cumulativePop(precincts):
			retval = [0]*len(precincts)
			for n in xrange(0,len(precincts)):
				retval[n] = retval[n-1] + precincts[n].population()
			return retval

		# sorts precincts by position with respect to the specified angle
		def lineSortPoints(points,angle):
			sin = math.sin(angle)
			cos = math.cos(angle)
			def dot(pos):
				return cos*pos[0] + sin*pos[1]
			def comp(x,y):
				return cmp(dot(x),dot(y))
			precincts.sort(comp)

		from bisect    import bisect
		precincts = lineSortPrecincts(precincts,angle+math.pi/2)
		pops = cumulativePop(precincts)           # get cumulative population for precincts, following the line
		goalAmt = ratio*pops[-1]
		i = bisect(pops,goalAmt)                  # get index that partitions precincts by population by the ratio
		i = min((abs(pops[i]-goalAmt),i),(abs(pops[i-1]-goalAmt),i-1))[1] if i > 0 else i
		self.leftPart = tuple(precincts[0:i+1])
		self.rightPart = tuple(precincts[i+1:])
		self.ratio = ratio
		point = precincts[i].position()
		if(polygon == None):
			polygon = MultiPolygon(precincts).buffer(0)
		minX, minY, maxX, maxY = polygon.bounds
		length = 2*math.sqrt((maxX - minX)**2 + (maxY - minY)**2)
		sin = math.sin(angle)*length
		cos = math.cos(angle)*length
		p1 = (point[0]+cos,point[1]+sin)
		p2 = (point[0]-cos,point[1]-sin)
		line = LineString((p1,p2))
		intersections = polygon.exterior.intersection(line)
		points = tuple(point.coords[0] for point in intersections.geoms)
		try:
			LineString.__init__(self,points)
		except ValueError:
			plotPrecincts(precincts,color='red')
			xs,ys = polygon.exterior.xy
			pyplot.plot(xs,ys)
			xs,ys = line.xy
			pyplot.plot(xs,ys,color='black')
			pyplot.show()
			raise ValueError

	def plot(self,fig = pyplot, color='black'):
		xs, ys = self.xy
		fig.plot(xs,ys,color,linewidth='3')


def plotPoints(points,color='b'):
	for p in points:
		pyplot.scatter(p[0],p[1],c=color)

def plotPrecincts(ps,color='b'):
	for p in ps:
		p.plot(color=color)

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

