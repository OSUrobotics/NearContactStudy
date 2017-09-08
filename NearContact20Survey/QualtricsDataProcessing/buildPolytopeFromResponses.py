#! /usr/bin/env python
import pdb
import numpy as np
import copy
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from scipy.spatial import ConvexHull
import Image, ImageOps
import os
import seaborn as sns
sns.set()
import csv

from KeyMapper import KeyMapper

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

	def formatPlot(self, ax): #adds some standard formatting for plots
		ax.set_xlim3d([0,33])
		ax.set_ylim3d([0,33])
		ax.set_zlim3d([0,33])
		ax.set_xticks(self.value_range)
		ax.set_yticks(self.value_range)
		ax.set_zticks(self.value_range)

	def plotPoints(self, points, ax, errors = None, show = True): # creates a 3d plot of points
		# assume errors are already scaled (not applying 2 stdev here)
		ax.scatter(points[:,0], points[:,1], points[:,2])
		self.formatPlot(ax)
		if errors is not None and len(errors) == len(points):
			for i,pe in enumerate(zip(points,errors)):
				p, e = pe
				upper = p + e
				lower = p - e
				x = [lower[0], upper[0]]
				y = [lower[1], upper[1]]
				z = [lower[2], upper[2]]
				ax.plot(x, y, z, marker="_", ms=10)
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

	def drawPlanesFromHull(self, points, hull, ax, show = False, color = None): #draws planes for each set of hull points
		if color is None: color = (np.random.rand(3)).reshape(1,3)
		for simplex in hull.simplices:
			# pt = np.array([points[simplex[0]], points[simplex[1]], points[simplex[2]]])
			pt = np.array(points[simplex])
			self.drawPlane(pt, ax, color)
		if show:
			plt.show()
		return color.flatten()

	def drawNormalsFromHull(self, points, hull, ax, show = False, hull_original = None): # draw normals for each set of hulls
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

	def drawAvgPointOnHull(self, points, hull, ax, show = False, hull_original = None): #draws points at the center of each plane
		for eqs, simplex in zip(hull.equations, hull.simplices):
			nm = self.normalVectors(eqs)
			bound_pts = points[simplex]
			avg_pt = np.mean(bound_pts, axis = 0).reshape(-1,3)
			# print("Average Point: %s" %avg_pt)
			ax.scatter(avg_pt[0,0], avg_pt[0,1], avg_pt[0,2], c = 'r', marker = 'o', s = 50)
			# ax.plot(avg_pt[:], 'ro', markersize = 10)
		if show:
			plt.show()

	def inHull(self, hull_orig, point): #checks if a point is in the hull
		hull_test = self.fitConvexHull(np.vstack((hull_orig.points,  point)))
		if hull_test == hull_orig:
				return True
		else:
			return False

	def drawPlane(self, pts, ax, color = None): #draws plane for a set of points
		#have to do something to order the points!
		if color is None:
			color = (np.random.rand(3)).reshape(1,3)
		poly3d = Poly3DCollection([pts], alpha=0.5) #alpha doesn't work
		poly3d.set_facecolor(color)
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

	def addGraspImage(self, image_fn, ax, show = False, loc = 0, color = None): #adds an image of the grasp to the existing plot
		im = Image.open(image_fn)
		if color is not None:
			color = color * 255 #convert from 0-1 to 0-255
			color = color.astype('int')
		else:
			color = np.random.randint(0,255,size=(3))
		pad = 5
		im = ImageOps.expand(im, border=pad, fill=tuple(color))
		scaling = 0.8
		size = (scaling*im.size[0], scaling*im.size[1])
		im.thumbnail(size, Image.ANTIALIAS)
		width = im.size[0]
		height = im.size[1]
		im = np.array(im).astype(np.float) / 255 #convert to array with values between 0 and 1
		fig = ax.figure

		# With newer (1.0) versions of matplotlib, you can 
		# use the "zorder" kwarg to make the image overlay
		# the plot, rather than hide behind it... (e.g. zorder=10)
		if loc == 0: x_loc = pad; 					y_loc = fig.bbox.ymax - height
		if loc == 1: x_loc = pad; 					y_loc = pad
		if loc == 2: x_loc = fig.bbox.xmax - width; y_loc = fig.bbox.ymax - height
		if loc == 3: x_loc = fig.bbox.xmax - width; y_loc = pad
		fig.figimage(im, x_loc, y_loc, zorder = 10)
		if show: plt.show()




class PolytopeParametric(object):
	# class for making a polytope from parametric stats
	def __init__(self):
		self.mapper = None

	def setDicts(self, small_stats, large_stats):
		#sets dictionaries that will be used for plotting purposes
		self.small_shapedata_stats = small_stats
		self.large_shapedata_stats = large_stats


	def FNFromKey(self, key_orig): #returns a filename to an image
		if self.mapper is None:
			self.mapper = KeyMapper()
		key = self.mapper.map(key_orig)
		image_dir = os.path.dirname(os.path.realpath(__file__)) + '/../../ShapeImageGenerator/GeneratedImagesReduced/Grasps/'
		file_parts = ['', '_h', '_w', '_e', '_', '_', '_', '_']
		if len(key) > len(file_parts):
			file_parts.insert(4, '_a')
		out_FN = ''
		for val,part in zip(key, file_parts):
			out_FN += part + str(val)
		out_FN += '.png'
		# print("Image FN: %s" %out_FN)
		return image_dir + out_FN

	def responsesAsPoints(self, key):
		# returns the responses for a given key as a set of points
		# instead of an individual value for that dimension
		dim_mapper = {' H': 0, ' W': 1, ' E': 2}
		responses = []
		errors = []
		for d in (self.small_shapedata_stats[key], self.large_shapedata_stats[key]):
			for k1, v1 in d.iteritems():
				moderate_array = [17, 17, 17]
				error_array = [0, 0, 0]
				moderate_array[dim_mapper[k1]] = v1[0] #average value
				error_array[dim_mapper[k1]] = v1[1] #std deviation
				responses.append(moderate_array)
				errors.append(error_array)
		responses = np.array(responses)
		errors = np.array(errors)
		return responses, errors

	def createPolytopeStats(self, key, Save = False, ax = None, multi = False, loc = 0, color = None): #plots values from survey for a single scenario using averaged values
		P = BuildPolytope()
		image_fn = self.FNFromKey(key) #key should already be converted
		responses, errors = self.responsesAsPoints(key)

		# plot it on an array
		if ax is None:
			fig = plt.figure(figsize = (15, 10))
			ax = fig.add_subplot(111, projection='3d')
		ax = P.plotPoints(responses, errors = errors, show = False, ax = ax)
		if not multi: ax.set_title(key.split('_')[0])
		hull = P.fitConvexHull(responses)
		eqs, simps = P.uniqueHullEquations(hull)
		hull_simp = copy.deepcopy(hull)
		hull_simp.equations = eqs
		hull_simp.simplices = simps
		# P.paramsForNewQuestionsGrid(responses, errors, hull_simp, ax, Plot = False)
		P.drawPlanesFromHull(responses, hull_simp, ax, show = False, color = color)
		P.drawAvgPointOnHull(responses, hull_simp, ax, show = False, hull_original = hull)
		P.addGraspImage(image_fn, ax, show = False, loc = loc, color = color)
		if not multi:
			if Save:
				ax.figure.savefig('SinglePolytope/ParametricContinuous/' + key + '.png')
				plt.close(ax.figure)
			else:
				plt.show()
		return ax

	def createPolytopeStatsAll(self): #plots for all scenarios in survey
		for key in self.small_shapedata_stats.keys():
			self.createPolytopeStats(key, Save = True)

	def createMultiplePolytopeStats(self, key_list, Save = False):
		#plots multiple polytopes on the same plot
		if len(key_list) < 2:
			print('Insufficient Entries')
			return
		ax = None
		color_list = (np.random.rand(len(key_list * 3))).reshape(-1,3)
		for ik,key in enumerate(key_list):
			ax = self.createPolytopeStats(key = key, Save = False, ax = ax, multi = True, loc = ik, color = color_list[ik])
		if Save:
			ax.figure.savefig('TwoPolytopes/ParametricContinuous/' + '_'.join(key_list) + '.png')
			plt.close(ax.figure)
		else:
			plt.show()

	def createMultiplePolytopeStatsAll(self, Save = True): #plots all combinations
		for key1 in self.small_shapedata_stats.keys():
			for key2 in self.small_shapedata_stats.keys():
				self.createMultiplePolytopeStats((key1, key2), Save = Save)

	def paramsForNewQuestionsLinear(self, key): # from the normal equations, list parameters for new questions
		points, errors = self.responsesAsPoints(key)
		P = BuildPolytope()
		hull_orig = P.fitConvexHull(points)
		eqs, simps = P.uniqueHullEquations(hull_orig)
		hull = copy.deepcopy(hull_orig)
		hull.equations = eqs
		hull.simplices = simps

		question_counter = 0
		q_range = 10
		half_range = 6
		normal_pts = []
		print('*'*5 + key + '*'*5)
		for eqs, simplex in zip(hull.equations, hull.simplices):
			nm = P.normalVectors(eqs)
			bound_pts = points[simplex]
			avg_pt = np.mean(bound_pts, axis = 0)
			print("Question %s, Boundary Parameters -- w:%s, h:%s, e:%s" %(question_counter, avg_pt[0].round(2), avg_pt[1].round(2), avg_pt[2].round(2)))
			question_counter += 1
			range_pt = np.ones((5,3)) * (avg_pt - half_range * nm)
			for span  in range(5): # 5 images in question
				range_pt[span] += (2 * half_range) / 5 * span * nm
			normal_pts.append(range_pt)
			if (range_pt<1).any():
				print('\t Invalid Range')
				pdb.set_trace()
			else:
				for span in range(5):
					print('\t Image %s -- w:%0.2f, h:%0.2f, e:%0.2f' %(span, range_pt[span][0], range_pt[span][1], range_pt[span][2]))
		# normal_pts = np.array(normal_pts).reshape(-1,3)
		return normal_pts

	def plotQuestionPoints(self, qpoints, ax = None): #scatter plots points from question
		if ax is None:
			fig = plt.figure(figsize = (15, 10))
			ax = fig.add_subplot(111, projection='3d')
		for qp in qpoints:
			ax.scatter(qp[:,0], qp[:,1], qp[:,2], c = 'k', marker = '*', s =10)
		BuildPolytope().formatPlot(ax)

	def paramsForNewQuestionsGrid(self, key): # from the normal equation, list parameters for next survey questions
		points, errors = self.responsesAsPoints(key)
		P = BuildPolytope()
		hull_orig = P.fitConvexHull(points)
		eqs, simps = P.uniqueHullEquations(hull_orig)
		hull = copy.deepcopy(hull_orig)
		hull.equations = eqs
		hull.simplices = simps
		# pdb.set_trace()

		question_counter = 0
		exploration_range = 1
		grid_points_all = []
		for eqs, simplex in zip(hull.equations, hull.simplices):
			nm = P.normalVectors(eqs)
			bound_pts = points[simplex]
			avg_pt = np.mean(bound_pts, axis = 0)
			stdev = np.sqrt(np.sum(errors[simplex]**2, axis = 0)) #sqrt of the sum of the variances along each dimension
			print("Question %s, Boundary Parameters -- w:%s, h:%s, e:%s" %(question_counter, avg_pt[0].round(2), avg_pt[1].round(2), avg_pt[2].round(2)))
			print("Standard Deviations -- w:%s, h:%s, e:%s" %(stdev[0].round(2), stdev[1].round(2), stdev[2].round(2)))
			# if Plot: ax.scatter(avg_pt[0], avg_pt[1], avg_pt[2], c='r', marker='o', s=50)
			# if Plot: ax.scatter(bound_pts[:,0], bound_pts[:,1], bound_pts[:,2], c='k', marker='2',s=50)
			delta1 = nm*exploration_range
			delta2 = bound_pts[0] - avg_pt
			delta2 /= np.linalg.norm(delta2) #normalize
			delta2 *= exploration_range
			image_count = 0
			single_grid = []
			for i1 in range(3): #normal direction and picking a direction from the mean towards a boundary point
				mid_point = avg_pt - delta1 + i1*delta1
				grid_ps = np.array([mid_point - delta2 + i2*delta2 for i2 in range(3)])
				single_grid.append(grid_ps)
				for p in grid_ps:
					print('\t Image %s -- w:%0.2f, h:%0.2f, e:%0.2f' %(image_count, p[0], p[1], p[2]))
					image_count += 1
			single_grid = np.array(single_grid).reshape(-1,3)
			grid_points_all.append(single_grid)
	
		return grid_points_all

	def writePointsToCSV(self, csvfn, key, points): #writes points for a question to csv
		with open(csvfn, 'ab') as csvfile:
			writer = csv.writer(csvfile)
			writer.writerow([key])
			for i,point_set in enumerate(points):
				row = ['Question %s' %i]
				for p in point_set:
					row.extend(p)
				writer.writerow(row)




class PolytopeNonparametric(PolytopeParametric):
	# class for making a polytop from nonparametric stats
	def __init__(self):
		super(PolytopeNonparametric, self).__init__()

	def setDicts(self, small_stats, large_stats):
		super(PolytopeNonparametric, self).setDicts(small_stats, large_stats)

	def FNFFromKey(self, key_orig):
		return super(FNFromKey, self).FNFromKey(key_orig)

	def responsesAsPoints(self, key, CI_amount):
		# returns the responses for a given key as a set of points
		# instead of an individual value for that dimension
		dim_mapper = {' H': 0, ' W': 1, ' E': 2}
		responses = []
		try:
			for i,d in enumerate((self.small_shapedata_stats[key], self.large_shapedata_stats[key])):
				for k1, v1 in d.iteritems():
					moderate_array = [17, 17, 17]
					#median value -- correct value changes depding on if its the large side or the small side
					if CI_amount >= 0.5:
						if i == 0: moderate_array[dim_mapper[k1]] = v1[2] # upper value in interval
						if i == 1: moderate_array[dim_mapper[k1]] = v1[1] # lower value in interval
					elif CI_amount < 0.5:
						if i == 0: moderate_array[dim_mapper[k1]] = v1[1] # lower value in interval
						if i == 1: moderate_array[dim_mapper[k1]] = v1[2] # upper value in interval
					responses.append(moderate_array)
			responses = np.array(responses)
			return responses
		except:
			pdb.set_trace()

	def pointsCreatePolytopeCheck(self, responses):
		# assumes an ordered list of values (1st and 4th correspond to min and max of H dimension)
		for i in range(3): #i don't know how generalizable this check is!
			if all(responses[i] >= responses[i+3]):
				return False
		else:
			return True

	def createPolytopeStats(self, CI_amount, key, Save = False, ax = None, multi = False, loc = 0, color = None): #plots values from survey for a single scenario using averaged values
		P = BuildPolytope()
		image_fn = self.FNFromKey(key) #key should already be converted
		responses = self.responsesAsPoints(key = key, CI_amount = CI_amount)
		check = self.pointsCreatePolytopeCheck(responses)
		if not check:
			print('Polytope does not exist: %s' %key)
			return False

		# plot it on an array
		if ax is None:
			fig = plt.figure(figsize = (15, 10))
			ax = fig.add_subplot(111, projection='3d')
		ax = P.plotPoints(responses, show = False, ax = ax)
		if not multi: ax.set_title('%s %s' %(round(CI_amount,2), key.split('_')[0]))
		hull = P.fitConvexHull(responses)
		eqs, simps = P.uniqueHullEquations(hull)
		hull_simp = copy.deepcopy(hull)
		hull_simp.equations = eqs
		hull_simp.simplices = simps
		# P.paramsForNewQuestionsGrid(responses, errors, hull_simp, ax, Plot = False)
		color = P.drawPlanesFromHull(responses, hull_simp, ax, show = False, color = color)
		P.drawAvgPointOnHull(responses, hull_simp, ax, show = False, hull_original = hull)
		P.addGraspImage(image_fn, ax = ax, show = False, loc = loc, color = color)
		if not multi:
			if Save:
				ax.figure.savefig('SinglePolytope/NonparametricContinuous/' + key + '%s' %(round(CI_amount,2)) + '.png')
				plt.close(ax.figure)
		return ax

	def createPolytopeStatsAll(self, CI_amount): #plots for all scenarios in survey
		for key in self.small_shapedata_stats.keys():
			self.createPolytopeStats(CI_amount, key = key, Save = True)

	def createMultiplePolytopeStats(self, CI_amount, key_list = None, Save = False):
		#plots multiple polytopes on the same plot
		if not key_list: key_list = [self.small_shapedata_stats.keys()[i] for i in [18, 30]]
		if len(key_list) < 2:
			print('Insufficient Entries')
			return
		ax = None
		color_list = (np.random.rand(len(key_list * 3))).reshape(-1,3)
		for ik,key in enumerate(key_list):
			ax = self.createPolytopeStats(CI_amount, key = key, Save = False, ax = ax, multi = True, loc = ik, color = color_list[ik])

		ax.set_title('CI: %s' %(round(CI_amount*100,0)))
		if Save:
			ax.figure.savefig('TwoPolytopes/NonparametricContinuous/' + '_'.join(key_list) + '%s' %(round(CI_amount*100,0)) + '.png')
			plt.close(ax.figure)
		else:
			plt.show()

	def createMultiplePolytopeStatsAll(self, CI_amount, Save = True): #plots all combinations
		for key1 in self.small_shapedata_stats.keys():
			for key2 in self.small_shapedata_stats.keys():
				self.createMultiplePolytopeStats(CI_amount, (key1, key2), Save = Save)

	def paramsForNewQuestionsLinear(self, CI_amount, key): # from the normal equations, list parameters for new questions
		points= self.responsesAsPoints(key, CI_amount)
		P = BuildPolytope()
		hull_orig = P.fitConvexHull(points)
		eqs, simps = P.uniqueHullEquations(hull_orig)
		hull = copy.deepcopy(hull_orig)
		hull.equations = eqs
		hull.simplices = simps

		question_counter = 0
		q_range = 10
		half_range = 6
		normal_pts = []
		print('*'*5 + key + '*'*5)
		for eqs, simplex in zip(hull.equations, hull.simplices):
			nm = P.normalVectors(eqs)
			bound_pts = points[simplex]
			avg_pt = np.mean(bound_pts, axis = 0)
			print("Question %s, Boundary Parameters -- w:%s, h:%s, e:%s" %(question_counter, avg_pt[0].round(2), avg_pt[1].round(2), avg_pt[2].round(2)))
			question_counter += 1
			range_pt = np.ones((5,3)) * (avg_pt - half_range * nm)
			for span  in range(5): # 5 images in question
				range_pt[span] += (2 * half_range) / 5 * span * nm
			normal_pts.append(range_pt)
			if (range_pt<1).any():
				print('\t Invalid Range')
				pdb.set_trace()
			else:
				for span in range(5):
					print('\t Image %s -- w:%0.2f, h:%0.2f, e:%0.2f' %(span, range_pt[span][0], range_pt[span][1], range_pt[span][2]))
		return normal_pts

	def paramsForNewQuestionsGrid(self, CI_amount, key): # from the normal equation, list parameters for next survey questions
		points = self.responsesAsPoints(key, CI_amount)
		P = BuildPolytope()
		hull_orig = P.fitConvexHull(points)
		eqs, simps = P.uniqueHullEquations(hull_orig)
		hull = copy.deepcopy(hull_orig)
		hull.equations = eqs
		hull.simplices = simps

		question_counter = 0
		exploration_range = 1
		grid_points_all = []
		# print('Key: %s' %key)
		for eqs, simplex in zip(hull.equations, hull.simplices):
			nm = P.normalVectors(eqs)
			bound_pts = points[simplex]
			avg_pt = np.mean(bound_pts, axis = 0)
			# print("Question %s, Boundary Parameters -- w:%s, h:%s, e:%s" %(question_counter, avg_pt[0].round(2), avg_pt[1].round(2), avg_pt[2].round(2)))
			question_counter += 1
			# if Plot: ax.scatter(avg_pt[0], avg_pt[1], avg_pt[2], c='r', marker='o', s=50)
			# if Plot: ax.scatter(bound_pts[:,0], bound_pts[:,1], bound_pts[:,2], c='k', marker='2',s=50)
			delta1 = nm*exploration_range
			delta2 = bound_pts[0] - avg_pt
			delta2 /= np.linalg.norm(delta2) #normalize
			delta2 *= exploration_range
			image_count = 0
			single_grid = []
			for i1 in range(3): #normal direction and picking a direction from the mean towards a boundary point
				mid_point = avg_pt - delta1 + i1*delta1
				grid_ps = np.array([mid_point - delta2 + i2*delta2 for i2 in range(3)])
				single_grid.append(grid_ps)
				for p in grid_ps:
					# print('\t Image %s -- w:%0.2f, h:%0.2f, e:%0.2f' %(image_count, p[0], p[1], p[2]))
					image_count += 1
			single_grid = np.array(single_grid).reshape(-1,3)
			grid_points_all.append(single_grid)
	
		return grid_points_all

	def writeAllQuestions(self, csvfn, CI_amount, shape = None): # generats new questions for all objects (with filter) and saves to file
		try:
			os.remove(csvfn)
		except:
			pass
		for key in self.small_shapedata_stats.keys():
			try:
				qps = self.paramsForNewQuestionsGrid(CI_amount, key)
				self.writePointsToCSV(csvfn, qps, CI_amount, key)
			except:
				print('Failed to write Questions to File: %s%s' %(key, CI_amount))

	def writePointsToCSV(self, csvfn, points, CI_amount, key): #writes points for a question to csv
		try:
			key += '%s' %CI_amount
		except:
			pdb.set_trace()
		super(PolytopeNonparametric, self).writePointsToCSV(csvfn, key, points)


if __name__ == '__main__':
	eng = matlab.engine.start_matlab()
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