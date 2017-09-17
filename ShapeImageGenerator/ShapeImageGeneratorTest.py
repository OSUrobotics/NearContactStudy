import sys, os, copy, csv, re
from openravepy import *
import pdb
from NearContactStudy import Vis, GenVis, HandVis, ObjectGenericVis, AddGroundPlane
from NearContactStudy import BASE_PATH
import numpy as np 
import time
import matplotlib.pyplot as plt
import subprocess
from PIL import Image



class ShapeImageGenerator(object):
	def __init__(self, viewer = True):
		self.model_path = ''
		self.vis = Vis(viewer)
		self.Hand = HandVis(self.vis)
		self.Hand.loadHand()
		self.Hand.localTranslation(np.array([0,0,-0.075])) #offset so palm is at 0,0,0
		self.Obj = ObjectGenericVis(self.vis)
		self.groundPlane = AddGroundPlane(self.vis)
		self.loadSTLFileList()

	def loadSTLFileList(self, directory = BASE_PATH + '/ShapeGenerator/Shapes'): # get all STL files in directory
		self.STLFileList = list()
		for root, dirs, filenames in os.walk(directory):
			if filenames != []:
				for fname in filenames:
					if os.path.splitext(fname)[1] == '.stl': #only want stl files
						self.STLFileList.append(root + '/' + fname)

	def valuesFromFileName(self, fn_abs): # gets features of object from file name
		fn = fn_abs.split('/')[-1]
		fn_parts = fn.strip('.stl').split('_')
		shape = fn_parts[0]
		h = int(fn_parts[1].strip('h'))
		w = int(fn_parts[2].strip('w'))
		e = int(fn_parts[3].strip('e'))
		a = None
		if len(fn_parts) == 5: # extra feature when there is alpha
			a = int(fn_parts[4].strip('a'))
		return shape, h, w, e, a
		
	def loadObject(self, objtype, h, w, e, a = None): # loads stl object into scene
		# only centroid that hasn't been dealt with is the handle.
		# all centroids shoudl be in the center of the object
		self.Obj.features['type'] = objtype
		self.Obj.features['h'] = h
		self.Obj.features['w'] = w
		self.Obj.features['e'] = e
		self.Obj.features['a'] = a

		result = self.Obj.loadObject(objtype, h, w, e, a)
		return result

	def setObjTransparent(self, alpha = 0.5): # change transparency of object
		self.Obj.changeColor(alpha = alpha)   # this can be changed to changeColor

	def readParameterFile(self, fn): # reads in parameters for creating images from a CSV file
		params_list = list()
		with open(fn, 'rb') as file:
			csvreader = csv.reader(file, delimiter = ',')
			headers = csvreader.next()
			for row in csvreader:
				D = dict()
				for header,val in zip(headers,row):
					D[header] = val
				params_list.append(D)
		for ip in range(len(params_list)):
			for k in params_list[ip].keys():
				if 'Joint Angles' == k:
					try:
						params_list[ip][k] = np.array(params_list[ip][k].split(',')).astype('float')#convert to numpy array
					except Exception: # for when that entry is blank like when no hand in image
						# params_list[ip][k] = np.zeros(10) # set to some position so error is not thrown
						pass
				elif 'Hand Matrix' == k: # extract array
					try:
						params_list[ip][k] = self.stringToArray(params_list[ip][k])
					except Exception: # for when that entry is blank like when no hand in image
						# params_list[ip][k] = np.eye(4) # set to some position so error is not thrown
						pass
				elif 'Image Save Name' == k:
					params_list[ip][k] += '.png' # add extension
				elif 'Model' == k:
					params_list[ip][k] += '.stl' # add extension
				elif 'Model Matrix' == k: # extract array
					mat_str = params_list[ip][k]
					mat_num = self.stringToArray(mat_str)
					params_list[ip][k] = mat_num
				elif 'Camera Transform' == k:
					try: # in case camera transform is in three value format
						params_list[ip][k] = np.array(params_list[ip][k].split(',')).astype('float')#convert to numpy array
					except: # for when transform is in Transformation matrix format
						params_list[ip][k] = self.stringToArray(params_list[ip][k])
				elif 'Image Size' == k:
					i = 1 # should do soemthing here
				elif 'Ground Plane Height' == k:
					params_list[ip][k] = float(params_list[ip][k])
				else:
					print('Unexpected Key: %s' %(k))
		self.params_list = params_list
		return self.params_list

	def stringToArray(self, mat_str): # Description: convert string to array
		# had to do this because it is really easy to just copy and paste a matrix into spreadsheet (or save through DictWriter)
		# The matrix is also much easier to read in the csv file in this form
		# downside is that when you read it out, the brackets are part of the string.
		# this can be done in fewer, more efficient steps with regex, but i couldn't figure it out
		mat_re = re.findall(r'\[.*?\]', mat_str)
		mat_strip = [t.strip('[]') for t in mat_re]
		mat_num = np.array([t.split() for t in mat_strip]).astype('float')
		return mat_num

	def createImagesFromParametersList(self, shapes = None, obj_path = None): # creates images from a list of parameters
		print("Total: %s" %(len(self.params_list)))
		counter = 0
		for params in self.params_list:
			counter += 1
			if ((shapes == None) or (params['Image Save Name'].split('/')[-1].split('_')[0] in shapes)): # allows only a single set of shapes to be made from list. Mostly during development
				imageSuccess = self.createImageFromParameters(params, obj_path = obj_path)
				# if not imageSuccess:
				# 	pdb.set_trace()
				print("Current: %s" %counter)

	def createImageFromParameters(self, params, obj_path = None): # creates image from a single set of parameters
		
		objLoadSuccess = self.loadObjectFromParameters(params, obj_path = obj_path)
		if objLoadSuccess:
			try: # if ground plane is in params
				self.groundPlane.createGroundPlane(y_height = params['Ground Plane Height'])
			except:
				self.groundPlane.createGroundPlane(y_height = self.Obj.h/2.0/100)
			# self.vis.changeBackgroundColor(self.groundPlane.groundPlane.GetLinks()[0].GetGeometries()[0].GetAmbientColor())
			self.Obj.changeColor('purpleI')
			self.Hand.changeColor('yellowI')
			cam_params = params['Camera Transform']
			if len(cam_params) == 3: # 3 value camera location
				self.vis.setCamera(cam_params[0], cam_params[1], cam_params[2])
			else: # full camera transform given
				self.vis.viewer.SetCamera(cam_params)
			if params['Joint Angles'] is not '' and params['Hand Matrix'] is not '':
				self.Hand.show()
				self.Hand.setJointAngles(params['Joint Angles'])
				self.Hand.obj.SetTransform(params['Hand Matrix'])
			else: #for images where no hand is shown
				self.Hand.hide()
			self.Obj.obj.SetTransform(params['Model Matrix'])
			pts = self.Hand.getContactPoints(self.Obj.obj)
			while len(pts) > 0:
				self.Hand.moveY(-0.001)
				pts = self.Hand.getContactPoints(self.Obj.obj)
				
			self.vis.takeImage(params['Image Save Name'], delay = True)

			print("Image Recorded: %s" %params['Image Save Name'])
			return True
		else:
			print("Model Not Found: %s" %params['Model'])
			return False

	def loadObjectFromParameters(self, params, obj_path = None): # loads objects from a single set of parameters
		if obj_path is None:
			objLoadSuccess = self.Obj.loadObjectFN(self.Obj.stl_path + params['Model'])
		else:
			objLoadSuccess = self.Obj.loadObjectFN(obj_path + params['Model'])
		return objLoadSuccess

	def loadHandFromParameters(self, params): # sets hand features from a single set of parameters
		self.Hand.show()
		self.Hand.setJointAngles(params['Joint Angles'])
		self.Hand.obj.SetTransform(params['Hand Matrix'])

	def loadSceneFromParameters(self, params, collisionAvoid = True):
		self.groundPlane.createGroundPlane(y_height = params['Ground Plane Height'])

		self.loadObjectFromParameters(params)
		self.Obj.changeColor('purpleI')
		self.Obj.obj.SetTransform(params['Model Matrix'])
		if collisionAvoid:
			pts = self.Hand.getContactPoints(self.Obj.obj)
			while len(pts) > 0:
				self.Hand.moveY(-0.001)
				pts = self.Hand.getContactPoints(self.Obj.obj)

		self.Hand.show()
		self.loadHandFromParameters(params)
		self.Hand.changeColor('yellowI')
		self.Hand.setJointAngles(params['Joint Angles'])
		self.Hand.obj.SetTransform(params['Hand Matrix'])

		self.vis.viewer.SetCamera(params['Camera Transform'])

	def getParameterFromIndex(self, list_indx):
		if isinstance(list_indx, int):
			return self.params_list[list_indx] #get parameters from a location in the list

	def getParameterFromFeatures(self, shape, h, w, e, obj_or, grasp_type, grasp_approach, grasp_rot, cam_view, a = None):
		if a is not None:
			save_name = "%s_h%s_w%s_e%s_a%s_%s_%s_%s_%s_cam%s" %(shape, h, w, e, a, obj_or, grasp_type, grasp_approach, grasp_rot, cam_view)
		else: 
			save_name = "%s_h%s_w%s_e%s_%s_%s_%s_%s_cam%s" %(shape, h, w, e, obj_or, grasp_type, grasp_approach, grasp_rot, cam_view)
		# pdb.set_trace()
		for param in self.params_list:
			if save_name in param['Image Save Name']:
				return param
		print("No Match Found")
		return False




class Tester(object): # this is just meant to test different parts of the class
	def __init__(self):
		## TODO: make gui sliders for moving hand into position to make creating input sheet easier
		self.SIG = ShapeImageGenerator()

	def Test1(self): # Description: load file and move camera around
		SIG = self.SIG
		cube_list = [f for f in SIG.STLFileList if 'cube' in f]
		for f in cube_list[0:10]:
		# for f in SIG.STLFileList:
			shape, h, w, e, a = SIG.valuesFromFileName(f)
			SIG.loadObject(shape, h, w, e)
			# SIG.vis.drawPoints([0,0,0])

			# apply a translation
			pose_TL = poseFromMatrix(SIG.Obj.obj.GetTransform())
			pose_TL[4:] = np.array([0, 0, 7.5+w/2+5]).astype('float') / 100 #dimensions are in meters
			#offset from 0 distance to palm, half the width of the object, and some clearance
			# SIG.vis.drawPoints(pose_TL[4:])
			mat_TL = matrixFromPose(pose_TL)
			SIG.Obj.obj.SetTransform(mat_TL)
			SIG.Obj.changeColor('greenI')
			SIG.Hand.changeColor('blueI')

			# apply camera transform
			# based on dist, azimuth, and elevation
			# cam_T_good = np.array([[ 0.0666906 ,  0.18715091, -0.98006474,  0.38671088],
		 #       [-0.04387848,  0.98185137,  0.18450627, -0.07280195],
		 #       [ 0.99680843,  0.03069892,  0.07369215,  0.03687982],
		 #       [ 0.        ,  0.        ,  0.        ,  1.        ]])
			# SIG.vis.viewer.SetCamera(cam_T_good)

			cam_T_cur = SIG.vis.viewer.GetCameraTransform()
			cam_T_zero = np.eye(4)
			cam_p_zero = poseFromMatrix(np.eye(4))
			cam_p_dist = cam_p_zero;
			# for dist in np.linspace(0,100,101):
			# 	# cam_p_dist[4:] = np.array([0, 0, dist]).astype('float')/100 #dist
			# 	# cam_T_dist = matrixFromPose(cam_p_dist)
			# 	# SIG.vis.viewer.SetCamera(cam_T_dist)
			# 	SIG.vis.setCamera(dist, 0, 0)
			# 	time.sleep(0.05)

			# for az in np.linspace(0,np.pi, 101):
			# 	rot_AA_x = [0,az, 0] #azimuth
			# 	rot_mat_x = matrixFromAxisAngle(rot_AA_x)
			# 	rot_new_x = np.dot(rot_mat_x, cam_T_dist)
			# 	SIG.vis.viewer.SetCamera(rot_new_x)
			# 	time.sleep(0.05)

			# for el in np.linspace(0, np.pi, 101):
			# 	rot_AA_y = [el, 0, 0]  #elevation
			# 	rot_mat_y = matrixFromAxisAngle(rot_AA_y)
			# 	rot_new_y = np.dot(rot_mat_y, cam_T_dist)
			# 	SIG.vis.viewer.SetCamera(rot_new_y)
				# time.sleep(0.05)
			# dist = 100
			# for el, az in zip(np.linspace(0,np.pi, 101), np.linspace(0,np.pi, 101)):
			# 	# rot_AA = [el, az, 0]
			# 	# rot_mat = matrixFromAxisAngle(rot_AA)
			# 	# rot_new = np.dot(rot_mat, cam_T_dist)
			# 	# SIG.vis.viewer.SetCamera(rot_new)
			# 	SIG.vis.setCamera(dist, el, az)
			# 	time.sleep(0.05)

			# pdb.set_trace()
			SIG.addGroundPlane(h/100.0/2)
			SIG.vis.setCamera(50, -3*np.pi/4, -np.pi/7)
			f_dict = SIG.Obj.features
			pdb.set_trace()
			image_fn = '%s_%s_h%s_w%s_e%s.png' %(f_dict['type'], int(f_dict['h']), int(f_dict['w']), int(f_dict['e']), 'pregrasp1')
			SIG.vis.takeImage(image_fn)


		pdb.set_trace()


		SIG.vis.close() # Description: Load objects and take a photo

	def Test2(self): # Descrption: Find limits of JA
		DOF = self.SIG.Hand.obj.GetDOFValues() * 0
		self.SIG.Hand.obj.SetDOFValues(DOF)
		for i,x in enumerate(DOF):
			for t in np.linspace(-2*np.pi, 2*np.pi, 21):
				DOF[i] = t
				self.SIG.Hand.obj.SetDOFValues(DOF)
				time.sleep(0.1)
			print("JA: %s" %i)
			pdb.set_trace()
			DOF[i] = 0

	def Test3(self): # Description: Get Object Matrix
		self.SIG.loadObject('cube', 1, 1, 1)
		print(self.SIG.Obj.obj.GetTransform())
		# add something for cropping image to desired size
		pdb.set_trace()

	def Test4(self): # Description: read in file with parameters
		
		fn = curdir + '/ImageGeneratorParameters.csv'
		self.SIG.readParameterFile(fn)
		pdb.set_trace()

	def Test5(self, fn): # Description: Read parameter file and create multiple images
		pdb.set_trace()
		self.SIG.readParameterFile(fn)
		# self.SIG.createImagesFromParametersList(shapes = ['cube'])
		# self.SIG.createImagesFromParametersList(shapes = ['ellipse'])
		# self.SIG.createImagesFromParametersList(shapes = ['cylinder'])
		# self.SIG.createImagesFromParametersList(shapes = ['coneRot'])
		# self.SIG.createImagesFromParametersList(shapes = ['cone'])
		# self.SIG.createImagesFromParametersList(shapes = ['handle'])
		# self.SIG.createImagesFromParametersList(shapes = ['vase'])
		self.SIG.createImagesFromParametersList()
		print("Image Generation Complete!")

	

	def Test7(self): # Description: Read parameter file and create a single image
		#print('\n'.join(['%s:%s' %(it,t['Model']) for it,t in enumerate(self.SIG.params_list)]))
		self.SIG.loadSTLFileList()
		fn = curdir + '/ImageGeneratorParameters.csv'
		self.SIG.readParameterFile(fn)
		self.SIG.createImageFromParameters(self.SIG.params_list[22847])
		#[i for i,param in enumerate(self.SIG.params_list) if 'coneRot' in param['Image Save Name']]
		# self.SIG.loadObject('cylinder', 9, 6, 3)
		pdb.set_trace()

	def Test8(self): # Description: Adding Ground plane with object
		self.SIG.loadSTLFileList()
		fn = curdir + '/ImageGeneratorParameters.csv'
		self.SIG.readParameterFile(fn)
		self.SIG.loadObjectFromParameters(self.SIG.params_list[41])
		self.SIG.loadHandFromParameters(self.SIG.params_list[41])
		self.SIG.addGroundPlane(self.SIG.Obj.h / 100.0 / 2)
		pdb.set_trace()
		# self.SIG.addGroundPlane()

	def Test9(self): # Description: Figure out distance between palm and fingertips
		self.Test7()
		self.SIG.Hand.changeColor(alpha = 0.5)
		links_all = self.SIG.Hand.obj.GetLinks()
		links_tips = [link for link in links_all if 'dist_link' in link.GetName()]
		links_T = [link.GetTransform() for link in links_tips]
		links_point = [T[0:3,3] for T in links_T]
		self.SIG.vis.drawPoints(links_point)
		links_pose = [poseFromMatrix(T) for T in links_T]
		finger_offset = np.array([0, 0.1, 0]).reshape(1,3)
		self.SIG.Hand.show()
		self.SIG.loadObjectFromParameters(self.SIG.params_list[99])
		self.SIG.loadHandFromParameters(self.SIG.params_list[99])
		self.SIG.addGroundPlane(self.SIG.Obj.h / 100.0 / 2)
		pdb.set_trace()
		links_point_global = [poseTransformPoints(l, finger_offset) for l in links_pose]
		links_point_global = np.array(links_point_global).flatten().reshape(-1,3)
		self.SIG.vis.drawPoints(links_point_global, c = 'blueI')

	def Test10(self): #single object test case
		self.SIG.loadSTLFileList()
		fn = curdir + '/ImageGeneratorParameters.csv'
		self.SIG.readParameterFile(fn)
		# self.SIG.loadObject('cylinder', 9, 6, 3)
		params = self.SIG.getParameterFromList(9)
		# pdb.set_trace()
		self.SIG.loadHandFromParameters(params)
		self.SIG.loadObjectFromParameters(params)
		pdb.set_trace()

	

	def testParam(self, fn):
		self.SIG.loadSTLFileList()
		self.SIG.readParameterFile(fn)
		h = lambda: numpy.random.choice([1, 9, 17, 25, 33])
		w = lambda: numpy.random.choice([1, 9, 17, 25, 33])
		e = lambda: numpy.random.choice([1, 9, 17, 25, 33])

		pdb.set_trace()
		param = self.SIG.getParameterFromFeatures('cone', 33, 17, 25, 'w', '3fingerpinch', 'top','up', '1', alpha = 0.25); self.SIG.createImageFromParameters(param)
		# self.graspPlanner()
		# param = self.SIG.getParameterFromFeatures('cube', 33, 1, 1, 'h', '3fingerpinch', 'side', 'up', '0')
		# param = self.SIG.getParameterFromFeatures('cube', 1, 33, 33, 'h', 'equidistant', 'side', 'up', '0')
		# param = self.SIG.getParameterFromFeatures('cube', 1, 33, 33, 'h', 'equidistant', 'side', 'down', '0')
		# param = self.SIG.getParameterFromFeatures('cube', 33, 1, 1, 'h', 'hook', 'side', 'up', '0')
		# param = self.SIG.getParameterFromFeatures('cube', 33, 1, 1, 'h', 'hook', 'side', '90', '0')
		# param = self.SIG.getParameterFromFeatures('cube', 33, 1, 1, 'h', '3fingerpinch', 'top', 'up', '0')
		# param = self.SIG.getParameterFromFeatures('cube', 33, 1, 1, 'h', '3fingerpinch', 'top', 'angled', '0')
		# param = self.SIG.getParameterFromFeatures('cube', 33, 1, 1, 'h', 'equidistant', 'top', 'angled', '0')
		# param = self.SIG.getParameterFromFeatures('cube', 33, 1, 1, 'h', 'hook', 'top', 'angled', '0')
		# param = self.SIG.getParameterFromFeatures('cube', 33, 1, 1, 'h', '2fingerpinch', 'top', 'angled', '0')
		# param = self.SIG.getParameterFromFeatures('ellipse', h(), w(), e(), 'h', '3fingerpinch', 'side', 'up', '0')
		# param = self.SIG.getParameterFromFeatures('ellipse', h(), w(), e(), 'h', 'equidistant', 'side', 'up', '0')
		param = self.SIG.getParameterFromFeatures('ellipse', h(), w(), e(), 'h', 'hook', 'side', 'up', '0')
		self.SIG.createImageFromParameters(param)
		raw_input('Hit Enter to see Top View')
		
		# param = self.SIG.getParameterFromFeatures('cube', 33, 1, 1, 'h', '3fingerpinch', 'side', 'up', '1')
		# param = self.SIG.getParameterFromFeatures('cube', 1, 33, 33, 'h', 'equidistant', 'side', 'up', '1')
		# param = self.SIG.getParameterFromFeatures('cube', 1, 33, 33, 'h', 'equidistant', 'side', 'down', '1')
		# param = self.SIG.getParameterFromFeatures('cube', 33, 1, 1, 'h', 'hook', 'side', 'up', '1')
		# param = self.SIG.getParameterFromFeatures('cube', 33, 1, 1, 'h', 'hook', 'side', '90', '1')
		# param = self.SIG.getParameterFromFeatures('cube', 33, 1, 1, 'h', '3fingerpinch', 'top', 'up', '1')	
		# param = self.SIG.getParameterFromFeatures('cube', 33, 1, 1, 'h', '3fingerpinch', 'top', 'angled', '1')	
		# param = self.SIG.getParameterFromFeatures('cube', 33, 1, 1, 'h', 'equidistant', 'top', 'angled', '1')	
		# param = self.SIG.getParameterFromFeatures('cube', 33, 1, 1, 'h', 'hook', 'top', 'angled', '1')	
		# param = self.SIG.getParameterFromFeatures('cube', 33, 1, 1, 'h', '2fingerpinch', 'top', 'angled', '1')	
		# param = self.SIG.getParameterFromFeatures('ellipse', h(), w(), e(), 'h', '3fingerpinch', 'side', 'up', '1')	
		# param = self.SIG.getParameterFromFeatures('ellipse', h(), w(), e(), 'h', 'equidistant', 'side', 'up', '1')	
		param = self.SIG.getParameterFromFeatures('ellipse', h(), w(), e(), 'h', 'hook', 'side', 'up', '1')	
		self.SIG.createImageFromParameters(param)
		# pdb.set_trace()

		# param = self.SIG.getParameterFromFeatures('cylinder', 33, 1, 1, '3fingerpinch', 'side', 0)
		# param = self.SIG.getParameterFromFeatures('cylinder', 33, 33, 33, 'equidistant', 'side', 0)
		# param = self.SIG.getParameterFromFeatures('cylinder', 33, 33, 33, 'hook', 'side', 1)
		# param = self.SIG.getParameterFromFeatures('cylinder', 33, 33, 33, '2fingerpinch', 'side', 1)
		# param = self.SIG.getParameterFromFeatures('cylinderRot', 33, 33, 33, '3fingerpinch', 'side', 0)
		# param = self.SIG.getParameterFromFeatures('cube', 33, 17, 1, '3fingerpinch', 'side', 0)


		# param = self.SIG.getParameterFromFeatures('cylinder', 1, 1, 1, '3fingerpinch', 'top', 0)
		# param = self.SIG.getParameterFromFeatures('cylinder', 33, 33, 33, 'equidistant', 'top', 0)
		# param = self.SIG.getParameterFromFeatures('cylinder', 33, 33, 33, 'hook', 'top', 0)
		# param = self.SIG.getParameterFromFeatures('cylinder', 33, 33, 33, '2fingerpinch', 'top', 0)
		# param = self.SIG.getParameterFromFeatures('cylinderRot', 33, 33, 33, '3fingerpinch', 'top', 0)
		# param = self.SIG.getParameterFromFeatures('cone', 1, 17, 1, 'hook', 'side', 0, a = 20)
		# param = self.SIG.getParameterFromFeatures('coneRot', 1, 17, 1, 'hook', 'side', 0, a = 20)
		# param = self.SIG.getParameterFromFeatures('cylinderRot', 1, 25, 17, '2fingerpinch', 'top', 0)
		# param = self.SIG.getParameterFromFeatures('cylinder', 1, 25, 17, '2fingerpinch', 'top', 0)
		

		# param = self.SIG.getParameterFromFeatures('cylinder', 33, 33, 33, 'equidistant', 'side', 1)
		# param = self.SIG.getParameterFromFeatures('cylinder', 33, 33, 33, '2fingerpinch', 'top', 1)
		# param = self.SIG.getParameterFromFeatures('cylinderRot', 33, 33, 33, '3fingerpinch', 'side', 1)
		# param = self.SIG.getParameterFromFeatures('cylinderRot', 33, 33, 33, '3fingerpinch', 'top', 1)
		# param = self.SIG.getParameterFromFeatures('cone', 1, 17, 1, 'hook', 'side', 1, a = 20)
		# param = self.SIG.getParameterFromFeatures('coneRot', 1, 17, 1, 'hook', 'side', 1, a = 20)
		# param = self.SIG.getParameterFromFeatures('cylinderRot', 1, 25, 17, '2fingerpinch', 'top', 1)
		# param = self.SIG.getParameterFromFeatures('cylinderRot', 1, 25, 17, '2fingerpinch', 'top', 1)

		# param = self.SIG.getParameterFromFeatures('cube', 33, 17, 1, '3fingerpinch', 'side', 1)

		

	def viewImagesSideBySide(self, shape_type, h = None, w = None, e = None, a = None, grasp_type = None, grasp_approach = None, grasp_rot = None, cam_view = None):
		# view multiple images along one change in dimension side by side
		directory = curdir + '/GeneratedImages'
		param_names = ['%s_', 'h%s', 'w%s', 'e%s', 'a%s', '%s', '%s', '%s', 'cam%s']
		param_values = [shape_type, h, w, e, a, grasp_type, grasp_approach, grasp_rot, cam_view]
		file_parts = []
		for name, val in zip(param_names, param_values):
			if val is not None: #ensure it has a value
				file_parts.append(name %val)
		
		matching_file_names = []
		for root, dirs, filenames in os.walk(directory):
			if filenames != []:
				for fname in filenames:
					if os.path.splitext(fname)[1] == '.png': #only want image files
						status = True
						for part in file_parts: # check each file if it has all the parts
							if part in fname: #keep searching rest of string on success
								continue
							else:
								status = False # break out of search if no success
								break
						if status == True: # if all parts match, add it to the list
							if os.path.join(root, fname) not in matching_file_names:
								matching_file_names.append(os.path.join(root, fname))
		if len(matching_file_names) > 0:
			matching_file_names.sort() #doesn't really help with ordering!
			if len(matching_file_names) == 5:
				matching_file_names = [matching_file_names[i] for i in [1, 4, 0, 2, 3]]
			images = map(Image.open, matching_file_names) #open all images
			widths, heights = zip(*(i.size for i in images))  # extract sizes from images
			total_width = sum(widths) # comparison total width
			max_height = max(heights) # comparison total height
			new_im = Image.new('RGB', (total_width, max_height))
			x_offset = 0
			for im in images:
			  new_im.paste(im, (x_offset,0))
			  x_offset += im.size[0]

			# new_im.save('test.jpg')
			new_im.show()
		pdb.set_trace()

	def graspPlanner(self):
		robot = self.SIG.vis.env.GetRobots()[0] # barrett hand
		target = self.SIG.vis.env.GetBodies()[1] # object in scene
		pdb.set_trace()
		gmodel = databases.grasping.GraspingModel(robot,target)
		if not gmodel.load():
			print 'generating grasping model (one time computation)'
			gmodel.init(friction=0.4,avoidlinks=[])
			gmodel.generate(approachrays=gmodel.computeBoxApproachRays(delta=0.04,normalanglerange=0))
			gmodel.save()


if __name__ == '__main__':
	T = Tester()
	# T.Test6()
	# T.Test5(curdir + '/ImageGeneratorParameters.csv')
	# T.Test7()
	# T.Test10()
	# T.Test8()
	# T.handCenteredPhotos()
	
	if len(sys.argv) > 1 and sys.argv[1] == 'T':
		T.HandCenteredCSV()
	# T.Test5(curdir + '/HandCenteredImageGeneratorParameters.csv')
	# T.testParam(curdir + '/HandCenteredImageGeneratorParameters.csv')
	# T.viewImagesSideBySide('cylinder', h = None, w = 33, e = 33, grasp_type = 'equidistant', grasp_approach = 'side', cam_view = 0)
	# T.viewImagesSideBySide('cylinder', h = None, w = 33, e = 33, grasp_type = 'equidistant', grasp_approach = 'side', cam_view = 1)


