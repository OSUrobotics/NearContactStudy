#! /usr/bin/env python
import pdb
import numpy as np
import copy
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from scipy.spatial import ConvexHull

# Author: Ammar Kothari
# Last Editted: 8/20/17
class BuildPolytope(object):
	# This object is mean to analyze survey data results
	# It can plot data, build a convex hull, extract normal equations for each unique face
	# We used this object to see what subsequent questions needed to be asked after each survey
	def __init__(self):
		self.value_range = value_range = [1, 9, 17, 25, 33]

	def plotPoints(self, survey_data): # function that takes in survey data and plots points for each shape
		cube_color = [25,25,112] # Midnight Blue
		cylinder_color = [255,255,0] # Yellow
		cone_color = [255,0,0] # Red

		colors = {
		'cube': cube_color,
		'cylinder': cylinder_color,
		'cone': cone_color
		}

		for resp in survey_data:
			c = colors[resp['shape']] #get shape color


	def createPoints(self, n=100): # creates a set of points for testing functions
		points = list()
		for __ in range(n):
			w = np.random.choice(self.value_range)
			h = np.random.choice(self.value_range)
			e = np.random.choice(self.value_range)
			points.append([w, h, e])
		points = np.array(points)
		return points

	def plotPoints(self, points, show = True): # creates a 3d plot of points
		fig = plt.figure()
		ax = fig.add_subplot(111, projection='3d')
		ax.scatter(points[:,0], points[:,1], points[:,2])
		ax.set_xlim3d([0,33])
		ax.set_ylim3d([0,33])
		ax.set_zlim3d([0,33])
		ax.set_xticks(self.value_range)
		ax.set_yticks(self.value_range)
		ax.set_zticks(self.value_range)
		ax.set_xlabel('w')
		ax.set_ylabel('h')
		ax.set_zlabel('e')
		if show:
			plt.show()
		return ax

	def fitConvexHull(self, points): #creates a convext hull from provided points in 3d
		hull = ConvexHull(points, incremental = True)
		return hull

	def plotHull(self, points, hull, ax): #plots convex hull
		eqs, inv_ind = self.uniqueHullEquations(hull)
		unique_pts = []
		plt.ion()
		pdb.set_trace()
		for eq_ind in range(len(eqs)): #look thorough all equations
			pts = []
			# store simplex and then sort, maybe it won't cross then?
			for bound_pt_ind in range(len(hull.simplices)): # look through all points on boundary of surfaces
				if inv_ind[bound_pt_ind] == eq_ind: # get simplices that correspond to an equation
					p = np.array(points[hull.simplices[bound_pt_ind]]) # extract points simplex points to
					pts.append(p)
			unique_pts.append(np.unique(np.array(pts).reshape(-1,3), axis = 0))
		for plane_pts in unique_pts:
			self.drawPlane(plane_pts, ax)
			plt.draw()
			plt.pause(1)
		plt.show()
		pdb.set_trace()
		
	def uniqueHullEquations(self, hull): #returns the unique equations defining a convex hull
		uniq_eqs, inv_ind = np.unique(hull.equations, axis = 0, return_inverse=True)
		uniq_simp = self.combineSimplices(hull, uniq_eqs, inv_ind)
		return uniq_eqs, uniq_simp

	def combineSimplices(self, hull, uniq_eqs, inv_ind): #returns correspong simplexes for unique hull
		uniq_simp = []
		for eq_ind in range(len(uniq_eqs)): #search over e
			simp = []
			for bound_pt_ind in range(len(hull.simplices)):
				if inv_ind[bound_pt_ind] == eq_ind:
					simp.append(hull.simplices[bound_pt_ind])
			uniq_simp.append(np.unique(np.array(simp).flatten()))
		return uniq_simp

	def normalVectors(self, eqs): # returns the normal vector for a set of equations
		if eqs.ndim == 1:
			nm = eqs[0:3]
		elif eqs.ndim == 2:
			nm = eqs[0:3, :]
		return nm

	def drawPlanesFromHull(self, hull, ax, show = False): #draws planes for each set of hull points
		for simplex in hull.simplices:
			# pt = np.array([points[simplex[0]], points[simplex[1]], points[simplex[2]]])
			pt = np.array(points[simplex])
			self.drawPlane(pt, ax)
		if show:
			plt.show()

	def drawNormalsFromHull(self, hull, ax, show = False, hull_original = None): # draw normals for each set of hulls
		for eqs, simplex in zip(hull.equations, hull.simplices):
			nm = self.normalVectors(eqs)
			bound_pts = points[simplex]
			avg_pt = np.mean(bound_pts, axis = 0).reshape(-1,3)
			t = 5
			off_plane1 = avg_pt + nm * t
			off_plane2 = avg_pt - nm * t
			# see if adding point changes hull
			if not self.inHull(hull_original, off_plane1):
				off_plane = off_plane1
			else:
				off_plane = off_plane2
			line = np.vstack((avg_pt, off_plane))
			# ax.scatter(line[:, 0], line[:, 1], line[:, 2], 'k', linewidth = 5)
			ax.plot(line[:, 0], line[:, 1], line[:, 2], 'k-', linewidth = 5)
		if show:
			plt.show()

	def inHull(self, hull_orig, point): #checks if a point is in the hull
		hull_test = self.fitConvexHull(np.vstack((hull_orig.points,  point)))
		if hull_test == hull_orig:
				return True
		else:
			return False

	def paramsForNewQuestions(self, hull): # from the normal equations, list parameters for new questions
		question_counter = 0
		q_range = 10
		half_range = 6
		for eqs, simplex in zip(hull.equations, hull.simplices):
			nm = self.normalVectors(eqs)
			bound_pts = points[simplex]
			avg_pt = np.mean(bound_pts, axis = 0)
			print("Question %s, Boundary Parameters -- w:%s, h:%s, e:%s" %(question_counter, avg_pt[0].round(2), avg_pt[1].round(2), avg_pt[2].round(2)))
			question_counter += 1
			max_pt = avg_pt - q_range * nm
			range_pt = np.ones((6,3)) * (avg_pt - half_range * nm)
			for span  in range(5): # 5 images in question
				range_pt[span] += (2 * half_range) / 5 * span * nm
			if (range_pt<1).any():
				print('\t Invalid Range')
			else:
				for span in range(5):
					print('\t Image %s -- w:%0.2f, h:%0.2f, e:%0.2f' %(span, range_pt[span][0], range_pt[span][1], range_pt[span][2]))

	def drawPlane(self, pts, ax): #draws plane for a set of points
		color = (np.random.rand(3)).reshape(1,3)
		poly3d = Poly3DCollection([pts], facecolors = color)
		ax.add_collection3d(poly3d)

	def calculatePlane(self, plane_points): #gets parameters for plane from three points
		# http://kitchingroup.cheme.cmu.edu/blog/2015/01/18/Equation-of-a-plane-through-three-points/
		pdb.set_trace()
		v1 = plane_points[1] - plane_points[0]
		v2 = plane_points[2] - plane_points[0]
		cp = np.cross(v1, v2)
		a, b, c = cp
		d = np.dot(cp, plane_points[0])
		print('The equation is {0}x + {1}y + {2}z = {3}'.format(a, b, c, d))
		return a, b, c, d


if __name__ == '__main__':
	BP = BuildPolytope()
	points = BP.createPoints(20) # get data
	ax = BP.plotPoints(points, show = False) # plot data
	hull = BP.fitConvexHull(points) # fit a hull to the data
	# get unique planes
	eqs, simps = BP.uniqueHullEquations(hull)
	hull_simp = copy.deepcopy(hull)
	hull_simp.equations = eqs
	hull_simp.simplices = simps
	BP.paramsForNewQuestions(hull_simp)
	BP.drawPlanesFromHull(hull_simp, ax, show = False)
	BP.drawNormalsFromHull(hull_simp, ax, show = True, hull_original = hull)
	# BP.plotHull(points, hull, ax)
	plt.show()
	pdb.set_trace()