import sys, os, copy, csv, re
from openravepy import *
import pdb
curdir = os.path.dirname(os.path.realpath(__file__))
classdir = curdir +'/../InterpolateGrasps/'
sys.path.insert(0, classdir) # path to helper classes
from Visualizers import Vis, GenVis, HandVis, ObjectGenericVis, AddGroundPlane
import numpy as np 
import time
import matplotlib.pyplot as plt
import subprocess
from PIL import Image



class ShapeImageGenerator(object):
	def __init__(self):
		self.model_path = ''
		self.vis = Vis()
		self.Hand = HandVis(self.vis)
		self.Hand.loadHand()
		self.Hand.localTranslation(np.array([0,0,-0.075])) #offset so palm is at 0,0,0
		self.Obj = ObjectGenericVis(self.vis)
		self.groundPlane = AddGroundPlane(self.vis)
		self.loadSTLFileList()

	def loadSTLFileList(self, directory = curdir + '/../ShapeGenerator/Shapes'): # get all STL files in directory
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

	def createImagesFromParametersList(self, shapes = None): # creates images from a list of parameters
		print("Total: %s" %(len(self.params_list)))
		counter = 0
		for params in self.params_list:
			counter += 1
			if ((shapes == None) or (params['Image Save Name'].split('/')[-1].split('_')[0] in shapes)): # allows only a single set of shapes to be made from list. Mostly during development
				imageSuccess = self.createImageFromParameters(params)
				# if not imageSuccess:
				# 	pdb.set_trace()
				print("Current: %s" %counter)

	def createImageFromParameters(self, params): # creates image from a single set of parameters
		objLoadSuccess = self.loadObjectFromParameters(params)
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
				# pdb.set_trace()
			self.vis.takeImage(params['Image Save Name'], delay = True)

			print("Image Recorded: %s" %params['Image Save Name'])
			return True
		else:
			print("Model Not Found: %s" %params['Model'])
			return False

	def loadObjectFromParameters(self, params): # loads objects from a single set of parameters
		objLoadSuccess = self.Obj.loadObjectFN(self.Obj.stl_path + params['Model'])
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

	def ObjectCenteredCSV(self): # Description: Create CSV file for making images
		fn = curdir + '/ImageGeneratorParameters.csv'
		self.SIG.loadSTLFileList()
		# create list of dictionaries
		L = list()
		headers = ['Joint Angles', 'Hand Matrix', 'Model', 'Model Matrix', 'Camera Transform','Image Save Name', 'Image Size']
		CameraTransform = ['%s, %s, %s' %(80, -2.355, -.449), '%s, %s, %s' %(80, -2.355, -np.pi/2.2)]
		preshapes = ['0,0,%s,%s,%s,%s,%s,%s,%s,%s' %(0,0.0,0.0,0,0.0,0.0,0.0,0.0),
					 '0,0,%s,%s,%s,%s,%s,%s,%s,%s' %(np.pi/3,0.0,0.0,np.pi/3,0.0,0.0,0.0,0.0),
					 '0,0,%s,%s,%s,%s,%s,%s,%s,%s' %(np.pi,0.0,0.0,np.pi,0.0,0.0,0.0,0.0),
					 '0,0,%s,%s,%s,%s,%s,%s,%s,%s' %(np.pi/2,0.0,0.0,np.pi/2,0.0,0.0,0.0,0.0)]
					 # 3 finger pinch
					 # equidistant
					 # hook
					 # 2 finger pinch:
		preshape_names =    ['3fingerpinch', 'equidistant', 'hook', '2fingerpinch']
		
		handT_top = list((np.zeros((4,4)), np.zeros((4,4)), np.zeros((4,4)), np.zeros((4,4))))
		handT_side = list((np.zeros((4,4)), np.zeros((4,4)), np.zeros((4,4)), np.zeros((4,4))))
		handTs = [handT_side, handT_top]
		handT_names = ['side', 'top']

		ModelMatrix = list()
		ModelMatrix.append(np.eye(4))
		ModelMatrix.append(np.eye(4))
		

		total_files = len(self.SIG.STLFileList)
		count = 0
		for model in self.SIG.STLFileList:
			# pdb.set_trace()
			print('#' * (np.round(count/total_files, 1)), '\r')
			for ip, preshape in enumerate(preshapes):
				for it, handT in enumerate(handTs):
					for ic, cameraT in enumerate(CameraTransform):
						for im, modelT in enumerate(ModelMatrix):
							model_type = model.split('/')[-1].strip('.stl')
							# if 'cone' in model_type:
							# 	pdb.set_trace()
							if im == 1 and ('cylinder' not in model_type and 'cone' not in model_type): # skip second model matrix orientation for all objects except cylinder
								continue
							else: # only if it is a cylinder, do the second pass
								D = dict.fromkeys(headers)
								D['Joint Angles'] = preshape
								D['Model'] = model_type
								h =  float(D['Model'].split('_')[1].strip('h'))/100.0# position hand above height away from object centroid
								w =  float(D['Model'].split('_')[2].strip('w'))/100.0# position hand width away from object centroid
								e =  float(D['Model'].split('_')[3].strip('e'))/100.0# position hand object extent away from origin (palm)
								if 'a' in D['Model']:
									if 'D' not in D['Model'].split('_')[4].strip('a'):
										a = float(D['Model'].split('_')[4].strip('a'))
									else:
										a = -1
								else:
									a = None
								clearance = 0.01
								
								ModelMatrix[1] = np.array([[ 0, -1,  0,  0], [ 1,  0,  0,  0], [ 0,  0,  1,  0], [ 0,  0,  0,  1]]) # rotated 90 degrees around e
								m = 0
								if im ==1 and 'cylinder' in model_type:
									m = w - h
									ModelMatrix[1] = np.array([[np.cos(np.pi/2), -np.sin(np.pi/2),  0.    , -0.    ],
													       [ np.sin(np.pi/2), np.cos(np.pi/2),  0.    ,  m],
													       [ 0.    ,  0.    ,  1.    ,  0.    ],
													       [ 0.    ,  0.    ,  0.    ,  1.    ]])
									
								if im == 1 and 'cone' in model_type:
									a_rad = np.radians(a)
									# m = h/2 - (-1.0/4.0 * w * np.sin(np.radians(90 - a)))
									m = h/2 - 1.0/2.0 * (w * np.cos(a_rad) - h * np.sin(a_rad))
									ModelMatrix[1] = np.array([[np.cos(np.pi/2 + np.radians(a)), -np.sin(np.pi/2 + np.radians(a)),  0.    , -0.    ],
													       [ np.sin(np.pi/2 + np.radians(a)), np.cos(np.pi/2 + np.radians(a)),  0.    ,  m],
													       [ 0.    ,  0.    ,  1.    ,  0.    ],
													       [ 0.    ,  0.    ,  0.    ,  1.    ]])
								# i think the limit should be applied for each grasp?
								h_limit = np.array([-0.08, -0.04, 0.06, -0.025]) # this is specific for each grasp!
								if im == 1:
									h_offset = -(w/2 + clearance) + m # for objects on their side, needs to account for object center not at origin
								else:
									h_offset = -(h/2 + clearance)
								if h_offset > h_limit[ip]:
									h_offset = h_limit[ip] + h/2

								h_offset -= 0.075 # origin of hand is the base of the hand

								################ SIDE ##########################
								# 3 finger pinch
								handT_side[0] = np.array([[ 0,	-1,	0,	0],
								   						[   1,	0,	0,	-0.02],
								   						[   0,	0,	1,	-.01 + -e/2.0 - clearance - 0.075],
								   						[   0,	0,	0,	1]])
								# equidistant
								handT_side[1] = np.array([[ -1,	0,	0,	0],
								   						[   0,	-1,	0,	-0.056],
								   						[   0,	0,	1,	-.01 + -e/2.0 - clearance - 0.075],
								   						[   0,	0,	0,	1]])
								# hook
								handT_side[2] = np.array([[ 0,	1,	0,	0],
								   						[   -1,	0,	0,	-0.02],
								   						[   0,	0,	1,	-.01 + -e/2.0 - clearance - 0.075],
								   						[   0,	0,	0,	1]])
								# 2 finger pinch
								handT_side[3] = np.array([[ -1,	0,	0,	0],
								   						[   0,	-1,	0,	-.016],
								   						[   0,	0,	1,	-.01 + -e/2.0 - clearance - 0.075],
								   						[   0,	0,	0,	1]])
								
								################ TOP ##########################
								# 3 finger pinch
								handT_top[0] = np.array([[  0,	1,	0,	0],
								   						[   0,	0,	1,	h_offset],
								   						[   1,	0,	0,	0],
								   						[   0,	0,	0,	1]])
								# equidistant
								handT_top[1] = np.array([[ 1.  ,  0.   ,  0.   ,  0   ],
													[ 0.   ,  0.   ,  1.   , h_offset],
													[ 0.   , -1.   ,  0.   ,  0],
													[ 0.   ,  0.   ,  0.   ,  1.   ]])
								# hook
								handT_top[2] = np.array([[ -1.  ,  0.   ,  0.   ,  0   ],
													[ 0.   ,  0.   ,  1.   , h_offset],
													[ 0.   ,  1.   ,  0.   ,  0],
													[ 0.   ,  0.   ,  0.   ,  1.   ]])
								# 2 finger pinch
								handT_top[3] = np.array([[ -1.  ,  0.   ,  0.   ,  0   ],
													[ 0.   ,  0.   ,  1.   , h_offset],
													[ 0.   ,  1.   ,  0.   ,  0],
													[ 0.   ,  0.   ,  0.   ,  1.   ]])
								if im == 1 and ip == 0:
									#need to do something about cone slant
									holder = 1
								D['Hand Matrix'] = copy.deepcopy(handT[ip])
								D['Model Matrix'] = copy.deepcopy(ModelMatrix[im])
								D['Camera Transform'] = cameraT
								if im == 0: #normal save name
									ImageSaveName = '%s/%s_%s_%s_cam%s' %('GeneratedImages/Grasps', D['Model'], preshape_names[ip], handT_names[it], ic)
								elif im == 1 and 'cylinder' in model_type: #sidways cylinder save name
									ImageSaveName = '%s/%s_%s_%s_cam%s' %('GeneratedImages/Grasps', D['Model'].replace('cylinder', 'cylinderRot'), preshape_names[ip], handT_names[it], ic)
								elif im == 1 and 'cone' in model_type: #sideways cone
									ImageSaveName = '%s/%s_%s_%s_cam%s' %('GeneratedImages/Grasps', D['Model'].replace('cone', 'coneRot'), preshape_names[ip], handT_names[it], ic)
								D['Image Save Name'] = ImageSaveName
								D['Image Size'] = '' # need to do something for this step -- image size
								L.append(D)
								count = count + 1


		with open(fn, 'wb') as file:
			writer = csv.DictWriter(file, headers)
			writer.writeheader()
			for l in L:
				writer.writerow(l)
		print("Successfully wrote to CSV file")

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

	def objectsOnlyCSV(self):
		L = list()
		headers = ['Joint Angles', 'Hand Matrix', 'Model', 'Model Matrix', 'Camera Transform','Image Save Name', 'Image Size']
		fn = curdir + '/ImageGeneratorParametersObjectsOnly.csv'
		self.SIG.loadSTLFileList()
		CameraTransform = ['%s, %s, %s' %(80, -2.355, -.449)]

		for model in self.SIG.STLFileList: #capturing images of all objects
			D = dict.fromkeys(headers)
			D['Camera Transform'] = CameraTransform[0]
			D['Model'] = model.split('/')[-1].strip('.stl')
			D['Model Matrix'] = np.eye(4)
			D['Image Save Name'] = '%s/%s_nohand' %('GeneratedImages/ObjectsOnly', D['Model'])
			L.append(D)


		with open(fn, 'wb') as file:
			writer = csv.DictWriter(file, headers)
			writer.writeheader()
			for l in L:
				writer.writerow(l)
		print("Successfully wrote to CSV file")

	def handCenteredPhotos(self): #images with the palm as the focal point, and everything moving around it
		# load stuff
		self.SIG.loadSTLFileList()
		#################### SIDE GRASP #########################
		e_range = [1, 9, 17, 25, 33]
		for e in e_range:
			self.SIG.loadObject('cube', 9, 9, e)
			self.SIG.Obj.changeColor('purpleI')
			self.SIG.Hand.changeColor('yellowI')
			self.SIG.groundPlane.createGroundPlane(y_height = 0)

			# define transforms
			ObjT = np.eye(4)
			ObjT[1,3] = -self.SIG.Obj.h/2.0/100
			ObjT[2,3] = self.SIG.Obj.e/2.0/100 + 0.1
			HandT = np.array([ [ 0	  ,  1.   ,  0.   ,  0.   ],
						       [-1.   , -0	  , -0.   , -0.047],
						       [-0.   , -0.   ,  1.   , -0.075],
						       [ 0.   ,  0.   ,  0.   ,  1.   ]])
			# CameraT = transformLookat([0,0,0], [0.49111316, -0.42962807, 0.45136327], [-0.33102373, -2.19029834, -0.53001554])
			# CameraT = transformLookat([0,0,0], [0.5, -0.4, 0.45], [0, 1, 0])
			# Cam_dist = np.linalg.norm([0.5, -0.4, 0.45])

			CameraT1 = np.array([[-0.70626164,  0.30729662, -0.63777996,  0.57400196],
						       [ 0.        ,  0.90088162,  0.43406487, -0.39065838],
						       [ 0.70795091,  0.30656337, -0.63625813,  0.57263232],
						       [ 0.        ,  0.        ,  0.        ,  1.        ]])

			CameraT2 = np.array([[-0.70626164,  0.70074499, -0.10075192,  0.09067673],
							       [ 0.        ,  0.14231484,  0.98982144, -0.8908393 ],
							       [ 0.70795091,  0.69907292, -0.10051151,  0.09046036],
							       [ 0.        ,  0.        ,  0.        ,  1.        ]])

			# apply transforms
			self.SIG.Obj.obj.SetTransform(ObjT)
			self.SIG.Hand.obj.SetTransform(HandT)
			# camera angle 1
			self.SIG.vis.viewer.SetCamera(CameraT1)
			# take image
			self.SIG.vis.takeImage('./test_cube_h9_w9_e%s_cam1' %e)
			# camera angle 2
			self.SIG.vis.viewer.SetCamera(CameraT2)
			# take image
			self.SIG.vis.takeImage('./test_cube_h9_w9_e%s_cam2' %e)
			#repeat for other objects

		#################### TOP GRASP #########################
		h_range = [1, 9, 17, 25, 33]
		h_range.sort(reverse = True)
		for h in h_range:
			# pdb.set_trace()
			self.SIG.loadObject('cylinder', h, 9, 9)
			self.SIG.Obj.changeColor('purpleI')
			self.SIG.Hand.changeColor('yellowI')
			self.SIG.groundPlane.createGroundPlane(y_height = 0)

			# define transforms
			ObjT = np.eye(4)
			ObjT[1,3] = -self.SIG.Obj.h/2.0/100
			HandT = np.array([ [-1	  ,  0.   ,  0.   ,  0.   ],
						       [ 0.   , -0	  ,  1.   , -0.075 - self.SIG.Obj.h/100.0 - 0.1],
						       [ 0.   ,  1.   ,  0.   ,  0],
						       [ 0.   ,  0.   ,  0.   ,  1.   ]])
			
			cam_pt1 = [0.5, -0.45, 0.5]
			CameraT1 = np.array([[-0.70626164,  0.30729662, -0.63777996,  0.57400196],
						       [ 0.        ,  0.90088162,  0.43406487, -0.39065838],
						       [ 0.70795091,  0.30656337, -0.63625813,  0.57263232],
						       [ 0.        ,  0.        ,  0.        ,  1.        ]])
			CameraT1 = transformLookat([0,-0.25, 0], cam_pt1, [0, 1, 0])

			CameraT2 = np.array([[-0.70626164,  0.70074499, -0.10075192,  0.09067673],
							       [ 0.        ,  0.14231484,  0.98982144, -0.8908393 ],
							       [ 0.70795091,  0.69907292, -0.10051151,  0.09046036],
							       [ 0.        ,  0.        ,  0.        ,  1.        ]])

			cam_pt2 = copy.deepcopy(cam_pt1)
			r = np.linalg.norm(cam_pt1)
			# pdb.set_trace()
			cam_pt2[1] = -1 * np.sqrt(r * 0.95)
			cam_pt2[0] = np.sqrt((r - cam_pt2[1]**2)/2)
			cam_pt2[2] = cam_pt2[0]
			CameraT2 = transformLookat([0,-0.25, 0], cam_pt2, [0, 1, 0])

			# apply transforms
			self.SIG.Obj.obj.SetTransform(ObjT)
			self.SIG.Hand.obj.SetTransform(HandT)
			# camera angle 1
			self.SIG.vis.viewer.SetCamera(CameraT1)
			# take image
			self.SIG.vis.takeImage('./test_cylinder_h%s_w9_e9_cam0.png' %h)
			# camera angle 2
			self.SIG.vis.viewer.SetCamera(CameraT2)
			# pdb.set_trace()
			# take image
			self.SIG.vis.takeImage('./test_cylinder_h%s_w9_e9_cam1.png' %h)
			#repeat for other objects



		pdb.set_trace()


	def HandCenteredCSV(self): # Description: Create CSV file for making images
		fn = curdir + '/HandCenteredImageGeneratorParameters.csv'
		self.SIG.loadSTLFileList()
		# create list of dictionaries
		L = list()
		headers = ['Joint Angles', 'Hand Matrix', 'Model', 'Model Matrix', 'Camera Transform', 'Ground Plane Height','Image Save Name', 'Image Size']
		# preshape_names = ['3fingerpinch', 'equidistant', 'hook']
		preshape_names = ['3fingerpinch', 'equidistant', 'hook', '2fingerpinch']
		model_orientations = ['h', 'w', 'e']
		handT_names = ['side', 'top']
		handO_names = ['up', '90', 'down', 'angled']
		# handT_names = ['side']
		cam_view_names = ['0', '1']
		# model_orientations = ['upright']

		######## Features that are independent of any other features of Scene ##################
		 # 3 finger pinch
		 # equidistant
		 # hook
		 # 2 finger pinch
		preshapes = ['0,0,%s,%s,%s,%s,%s,%s,%s,%s' %(0,0.0,0.0,0,0.0,0.0,0.0,0.0),
					 '0,0,%s,%s,%s,%s,%s,%s,%s,%s' %(np.pi/3,0.0,0.0,np.pi/3,0.0,0.0,0.0,0.0),
					 '0,0,%s,%s,%s,%s,%s,%s,%s,%s' %(np.pi,0.0,0.0,np.pi,0.0,0.0,0.0,0.0),
					 '0,0,%s,%s,%s,%s,%s,%s,%s,%s' %(np.pi/2,0.0,0.0,np.pi/2,0.0,0.0,0.0,0.0)]

		 ############# Features that depend on other features in Scene #######
		handT_top = list((np.zeros((4,4)), np.zeros((4,4)), np.zeros((4,4)), np.zeros((4,4))))
		handT_side = list((np.zeros((4,4)), np.zeros((4,4)), np.zeros((4,4)), np.zeros((4,4))))
		handTs = [handT_side, handT_top]
		grasp_height_offset = dict().fromkeys(preshape_names)
		grasp_height_offset['3fingerpinch'] = dict().fromkeys(handO_names)
		grasp_height_offset['3fingerpinch']['up'] = -0.05
		grasp_height_offset['equidistant'] = dict().fromkeys(handO_names)
		grasp_height_offset['equidistant']['up'] = -0.095
		grasp_height_offset['equidistant']['down'] = -0.17	
		grasp_height_offset['equidistant']['90'] = -0.17
		grasp_height_offset['equidistant']['angled'] = -0.095		
		grasp_height_offset['hook'] = dict().fromkeys(handO_names)
		grasp_height_offset['hook']['up'] = -0.045
		grasp_height_offset['hook']['90'] = -0.045
		grasp_height_offset['2fingerpinch'] = dict().fromkeys(handO_names)
		grasp_height_offset['2fingerpinch']['up'] = -0.045

		total_files = len(self.SIG.STLFileList)
		count = 0
		for model in self.SIG.STLFileList:
			if 'vase' in model: # not vases for now
				continue
			print('#,' * (np.round(count/total_files, 1)), '\r')
			for im, mo in enumerate(model_orientations):
				for iht, ht in enumerate(handT_names):
					for ipn, pn in enumerate(preshape_names):
						for iho, ho in enumerate(handO_names):
							for icv, cv in enumerate(cam_view_names):
								rot_hand_flag = False
								####### set which configurations should be in CSV #########
								################# CUBE ####################################
									#################### h-up ##############################
										#################### SIDE #############################
								if 'cube' in model and mo == 'h' and ht == 'side' and pn == '3fingerpinch' and ho == 'up':
									pass
								elif 'cube' in model and mo == 'h' and ht == 'side' and pn == 'equidistant' and ho == 'up':
									pass
								elif 'cube' in model and mo == 'h' and ht == 'side' and pn == 'equidistant' and ho == 'down':
									pass
								elif 'cube' in model and mo == 'h' and ht == 'side' and pn == 'hook' and ho == 'up':
									pass
								elif 'cube' in model and mo == 'h' and ht == 'side' and pn == 'hook' and ho == '90':
									pass
								elif 'cube' in model and mo == 'h' and ht == 'side' and pn == '2fingerpinch' and ho == 'up':
									pass
										#################### TOP #############################
								elif 'cube' in model and mo == 'h' and ht == 'top' and pn == '3fingerpinch' and ho == 'up':
									pass
								elif 'cube' in model and mo == 'h' and ht == 'top' and pn == '3fingerpinch' and ho == 'angled':
									pass
								elif 'cube' in model and mo == 'h' and ht == 'top' and pn == 'equidistant' and ho == 'up':
									pass
								elif 'cube' in model and mo == 'h' and ht == 'top' and pn == 'equidistant' and ho == 'angled':
									pass
								elif 'cube' in model and mo == 'h' and ht == 'top' and pn == 'hook' and ho == 'up':
									pass
								elif 'cube' in model and mo == 'h' and ht == 'top' and pn == 'hook' and ho == 'angled':
									pass
								elif 'cube' in model and mo == 'h' and ht == 'top' and pn == '2fingerpinch' and ho == 'up':
									pass
								elif 'cube' in model and mo == 'h' and ht == 'top' and pn == '2fingerpinch' and ho == 'angled':
									pass

								################# ELLIPSE #################################
									#################### h-up ##############################
										#################### SIDE #############################
								elif 'ellipse' in model and mo == 'h' and ht == 'side' and pn == '3fingerpinch' and ho == 'up':
									pass
								elif 'ellipse' in model and mo == 'h' and ht == 'side' and pn == 'equidistant' and ho == 'up':
									pass
								elif 'ellipse' in model and mo == 'h' and ht == 'side' and pn == 'hook' and ho == 'up':
									pass
								elif 'ellipse' in model and mo == 'h' and ht == 'side' and pn == 'hook' and ho == '90':
									pass
								elif 'ellipse' in model and mo == 'h' and ht == 'side' and pn == '2fingerpinch' and ho == 'up':
									pass
										#################### TOP #############################
								elif 'ellipse' in model and mo == 'h' and ht == 'top' and pn == '3fingerpinch' and ho == 'up':
									pass
								elif 'ellipse' in model and mo == 'h' and ht == 'top' and pn == 'equidistant' and ho == 'up':
									pass
								elif 'ellipse' in model and mo == 'h' and ht == 'top' and pn == '2fingerpinch' and ho == 'up':
									pass
								################# CYLINDER #################################
									#################### h-up ##############################
										#################### SIDE ##########################
								elif 'cylinder' in model and mo == 'h' and ht == 'side' and pn == '3fingerpinch' and ho == 'up':
									pass
								elif 'cylinder' in model and mo == 'h' and ht == 'side' and pn == 'equidistant' and ho == 'up':
									pass
								elif 'cylinder' in model and mo == 'h' and ht == 'side' and pn == 'equidistant' and ho == 'down':
									pass
								elif 'cylinder' in model and mo == 'h' and ht == 'side' and pn == 'hook' and ho == 'up':
									pass
								elif 'cylinder' in model and mo == 'h' and ht == 'side' and pn == 'hook' and ho == '90':
									pass
								elif 'cylinder' in model and mo == 'h' and ht == 'side' and pn == '2fingerpinch' and ho == 'up':
									pass
										#################### TOP ###########################
								elif 'cylinder' in model and mo == 'h' and ht == 'top' and pn == '3fingerpinch' and ho == 'up':
									pass
								elif 'cylinder' in model and mo == 'h' and ht == 'top' and pn == 'equidistant' and ho == 'up':
									pass
								elif 'cylinder' in model and mo == 'h' and ht == 'top' and pn == '2fingerpinch' and ho == 'up':
									pass
									################### w-up ##############################
										################### SIDE ##########################
								elif 'cylinder' in model and mo == 'w' and ht == 'side' and pn == '3fingerpinch' and ho == 'up':
									pass
								elif 'cylinder' in model and mo == 'w' and ht == 'side' and pn == 'equidistant' and ho == 'up':
									pass
								elif 'cylinder' in model and mo == 'w' and ht == 'side' and pn == '2fingerpinch' and ho == 'up':
									pass
										################### TOP ###########################
								elif 'cylinder' in model and mo == 'w' and ht == 'top' and pn == '3fingerpinch' and ho == 'up':
									pass
								elif 'cylinder' in model and mo == 'w' and ht == 'top' and pn == '2fingerpinch' and ho == 'up':
									pass
									#################### e-up ##############################
										#################### SIDE ##########################
								elif 'cylinder' in model and mo == 'e' and ht == 'side' and pn == '3fingerpinch' and ho == 'up':
									pass
								elif 'cylinder' in model and mo == 'e' and ht == 'side' and pn == 'equidistant' and ho == 'up':
									pass
								elif 'cylinder' in model and mo == 'e' and ht == 'side' and pn == 'hook' and ho == 'up':
									pass
								elif 'cylinder' in model and mo == 'e' and ht == 'side' and pn == 'hook' and ho == '90':
									pass
								elif 'cylinder' in model and mo == 'e' and ht == 'side' and pn == '2fingerpinch' and ho == 'up':
									pass
										#################### TOP ##########################
								elif 'cylinder' in model and mo == 'e' and ht == 'top' and pn == '3fingerpinch' and ho == 'up':
									pass
								elif 'cylinder' in model and mo == 'e' and ht == 'top' and pn == 'equidistant' and ho == 'up':
									pass
								elif 'cylinder' in model and mo == 'e' and ht == 'top' and pn == 'equidistant' and ho == 'angled':
									pass
								elif 'cylinder' in model and mo == 'e' and ht == 'top' and pn == '2fingerpinch' and ho == 'up':
									pass

								################# CONE #####################################
									#################### h-up ##############################
										#################### SIDE ##########################
								elif 'cone' in model and mo == 'h' and ht == 'side' and pn == '3fingerpinch' and ho == 'up':
									pass
								elif 'cone' in model and mo == 'h' and ht == 'side' and pn == 'equidistant' and ho == 'up':
									pass
								elif 'cone' in model and mo == 'h' and ht == 'side' and pn == 'equidistant' and ho == '90':
									pass
								elif 'cone' in model and mo == 'h' and ht == 'side' and pn == 'hook' and ho == '90':
									pass
								elif 'cone' in model and mo == 'h' and ht == 'side' and pn == '2fingerpinch' and ho == 'up':
									pass
										#################### TOP ##########################
								elif 'cone' in model and mo == 'h' and ht == 'top' and pn == '3fingerpinch' and ho == 'up':
									pass
								elif 'cone' in model and mo == 'h' and ht == 'top' and pn == 'equidistant' and ho == 'up':
									pass
								elif 'cone' in model and mo == 'h' and ht == 'top' and pn == '2fingerpinch' and ho == 'up':
									pass
									#################### e-up ##############################
										#################### SIDE ##########################
								elif 'cone' in model and mo == 'e' and ht == 'side' and pn == '3fingerpinch' and ho == 'up':
									pass
								elif 'cone' in model and mo == 'e' and ht == 'side' and pn == 'equidistant' and ho == 'up':
									pass
								elif 'cone' in model and mo == 'e' and ht == 'side' and pn == '2fingerpinch' and ho == 'up':
									pass
										#################### TOP ##########################
								elif 'cone' in model and mo == 'e' and ht == 'top' and pn == '3fingerpinch' and ho == 'up':
									pass
								elif 'cone' in model and mo == 'e' and ht == 'top' and pn == '2fingerpinch' and ho == 'up':
									pass
								elif 'cone' in model and mo == 'e' and ht == 'top' and pn == 'equidistant' and ho == 'up':
									pass
								elif 'cone' in model and mo == 'e' and ht == 'top' and pn == 'equidistant' and ho == '90':
									pass
								else:
									continue

								#####################################################################################
								model_type = model.split('/')[-1].strip('.stl')
								print("Model: %s" %model_type)
								D = dict.fromkeys(headers)
								# no logic needed, so just set these
								D['Joint Angles'] = preshapes[ipn]
								D['Model'] = model_type

								#extract features of Model
								h =  float(D['Model'].split('_')[1].strip('h'))/100.0# position hand above height away from object centroid
								w =  float(D['Model'].split('_')[2].strip('w'))/100.0# position hand width away from object centroid
								e =  float(D['Model'].split('_')[3].strip('e'))/100.0# position hand object extent away from origin (palm)
								if 'a' in D['Model']:
									if 'D' not in D['Model'].split('_')[4].strip('a'):
										a = float(D['Model'].split('_')[4].strip('a'))
									else:
										a = -1
								else:
									a = None
								clearance = 0.05
								
								# set Hand Transform
								handT = np.zeros((4,4))
								height_in_world = 0; extent_in_world = 0;
								if mo == 'w' and 'cone' in model: # adjust height offset for rotated cone, width side down
									height_complete = h / (1 - a/100.0);
									w_gamma = np.arctan2(w/2, height_complete)
									height_in_world = 1.0 * (w * np.cos(w_gamma) - h * np.sin(w_gamma))
									extent_in_world = e
								elif mo == 'e' and 'cone' in model: # adjust height offset for rotated cone, extent side down
									height_complete = h / (1 - a/100.0);
									e_gamma = np.arctan2(e/2, height_complete)
									height_in_world = 1.0 * (e * np.cos(e_gamma) - h * np.sin(e_gamma))
									extent_in_world = h / np.cos(e_gamma)
								elif mo == 'h': # no rotation to object
									height_in_world = h
									extent_in_world = e
								elif mo == 'w': # adjust height offset for rotated object, width side down
									height_in_world = w
									extent_in_world = e
								elif mo == 'e': #adjust height offset for rotated object, extent side down
									height_in_world = e
									extent_in_world = h

								if ht == 'side': # approach from side
									if pn == '3fingerpinch': # 3 finger pinch
										if ho == 'up':
											handT = np.dot(matrixFromAxisAngle([0,0,np.pi/2]), np.eye(4)) # rotate hand around Z
									elif pn == 'equidistant': #equidistant
										if ho == 'up': # claw, 180 degree rotation
											handT = np.dot(matrixFromAxisAngle([0,0,np.pi]), np.eye(4)) #rotate hand around Z so one finger is up
										elif ho == 'down':
											handT = np.dot(matrixFromAxisAngle([0,0,0]), np.eye(4)) # rotate hand around Z so two fingers are up
										elif ho == '90':
											handT = np.dot(matrixFromAxisAngle([0,0,np.pi/2]), np.eye(4)) # rotate hand around Z fingers are on side
										elif ho == 'angled': #45 degree rotation from up
											handT = np.dot(matrixFromAxisAngle([0,0,3*np.pi/4]), np.eye(4))
									elif pn == 'hook': #hook
										if ho == 'up':
											handT = np.dot(matrixFromAxisAngle([0,0,np.pi]), np.eye(4)) # rotate hand pi around Z
										elif ho == '90':
											handT = np.dot(matrixFromAxisAngle([0,0,-np.pi/2]), np.eye(4)) # rotate hand pi around Z
									elif pn == '2fingerpinch': #2 finger pinch
										handT = np.dot(matrixFromAxisAngle([0,0,np.pi]), np.eye(4)) # rotate hand pi around Z
									try:
										if height_in_world/2.0 < abs(grasp_height_offset[pn][ho]): #need to clear ground plane
											# pdb.set_trace()
											handT[1,3] = grasp_height_offset[pn][ho] #height offset, grasp specific
										else:
											handT[1,3] = -height_in_world/2.0
									except:
										pdb.set_trace()
									handT[2, 3] = -0.075 # offset for palm
								if ht == 'top': # approach from top
									if pn == '3fingerpinch': #3 finger pinch
										if ho == 'up':
											handT = np.dot(matrixFromAxisAngle([0,0,np.pi/2]), np.eye(4)) # rotate hand pi/2 around Z
											handT = np.dot(matrixFromAxisAngle([-np.pi/2,0,0]), handT) # rotate hand pi/2 around X
										elif ho == 'angled':
											handT = np.dot(matrixFromAxisAngle([0,0,np.pi/2]), np.eye(4)) # rotate hand pi/2 around Z
											handT = np.dot(matrixFromAxisAngle([-np.pi/2,0,0]), handT) # rotate hand pi/2 around X
											handT = np.dot(matrixFromAxisAngle([0,np.pi/4,0]), handT) # rotate around y for fingers to corner
									elif pn == 'equidistant': #equidistant
										if ho == 'up':
											handT = np.dot(matrixFromAxisAngle([0,0,np.pi]), np.eye(4)) # rotate hand pi around Z
											handT = np.dot(matrixFromAxisAngle([-np.pi/2,0,0]), handT) # rotate hand pi/2 around X
										if ho == 'angled':
											handT = np.dot(matrixFromAxisAngle([0,0,np.pi]), np.eye(4)) # rotate hand pi around Z
											handT = np.dot(matrixFromAxisAngle([-np.pi/2,0,0]), handT) # rotate hand pi/2 around X
											handT = np.dot(matrixFromAxisAngle([0,-np.pi/4,0]), handT) # rotate around y for fingers to corner
										if ho == '90':
											handT = np.dot(matrixFromAxisAngle([-np.pi/2,0,0]), np.eye(4)) # rotate hand pi/2 around X
											handT = np.dot(matrixFromAxisAngle([0,np.pi/2,0]), handT) # rotate hand pi/2 around Y
									elif pn == 'hook': #hook
										if ho == 'up':
											handT = np.dot(matrixFromAxisAngle([0,0,-np.pi/2]), np.eye(4)) # rotate hand pi around Z
											handT = np.dot(matrixFromAxisAngle([-np.pi/2,0,0]), handT) # rotate hand pi/2 around X
										if ho == 'angled':
											handT = np.dot(matrixFromAxisAngle([0,0,-np.pi/2]), np.eye(4)) # rotate hand pi around Z
											handT = np.dot(matrixFromAxisAngle([-np.pi/2,0,0]), handT) # rotate hand pi/2 around X
											handT = np.dot(matrixFromAxisAngle([0,np.pi/4,0]), handT) # rotate around y for fingers to corner
									elif pn == '2fingerpinch': #2 finger pinch
										if ho == 'up':
											handT = np.dot(matrixFromAxisAngle([-np.pi/2,0,0]), np.eye(4)) # rotate hand pi/2 around X
											handT = np.dot(matrixFromAxisAngle([0, np.pi, 0]), handT) # rotate hand pi around Y
										if ho == 'angled':
											handT = np.dot(matrixFromAxisAngle([-np.pi/2,0,0]), np.eye(4)) # rotate hand pi/2 around X
											handT = np.dot(matrixFromAxisAngle([0, np.pi, 0]), handT) # rotate hand pi around Y
											# block view of skinny objects, but rotating it beyond 45 changes feature of object being examined
											handT = np.dot(matrixFromAxisAngle([0,-np.pi/4,0]), handT) # rotate around y for fingers to corner

									# unlikely for there to be a height collision
									handT[1,3] = -height_in_world + -0.075 + -clearance # offset for palm

								D['Hand Matrix'] = copy.deepcopy(np.round(handT, 4))

								# set Object Transfrom
								ModelT = np.eye(4)
								if mo == 'w' and 'cone' in model: # rotate on its w-side (slanted so needs extra factor)
									ModelT = np.dot(matrixFromAxisAngle([0, 0, np.pi/2 + w_gamma]), ModelT)
								elif mo == 'e' and 'cone' in model: # rotate on its e-side (slanted so needs extra factor)
									ModelT = np.dot(matrixFromAxisAngle([-np.pi/2 - e_gamma, 0, 0]), ModelT)
								elif mo == 'w': # rotate on its w-side
									ModelT = np.dot(matrixFromAxisAngle([0, 0, np.pi/2]), ModelT)
								elif mo == 'e': # rotate on its e-side
									ModelT = np.dot(matrixFromAxisAngle([np.pi/2, 0, 0]), ModelT)
								if ht == 'side': # approach from side, hand stays stationary
									ModelT[1,3] = -height_in_world/2.0
									ModelT[2,3] = extent_in_world/2.0 + clearance
								elif ht == 'top': # approach from the top, object bottom stays stationary
									ModelT[1,3] = -height_in_world/2.0

								D['Model Matrix'] = copy.deepcopy(ModelT)


								# Set Camera Transform
								cameraT = np.zeros((4,4))
								if ht == 'side': # approach from side, focus on palm
									if cv == '0': #isometric view
										cameraT = np.array([[-0.70626164,  0.30729662, -0.63777996,  1.1007],
												       [ 0.        ,  0.90088162,  0.43406487, -0.7491],
												       [ 0.70795091,  0.30656337, -0.63625813,  1.0981],
												       [ 0.        ,  0.        ,  0.        ,  1.        ]])
									elif cv == '1': #mostly top view
										cameraT = np.array([[-0.70626164,  0.70074499, -0.10075192,  0.1795	],
												       [ 0.        ,  0.14231484,  0.98982144, -1.763 ],
												       [ 0.70795091,  0.69907292, -0.10051151,  0.179 ],
												       [ 0.        ,  0.        ,  0.        ,  1.        ]])

								if ht == 'top': #approach from top, focus on bottom of object
									cam_pt1 = [1.0361, -0.6268, 1.0361]
									cam_pt2 = copy.deepcopy(cam_pt1)
									if cv == '0': # isometric view
										cameraT = transformLookat([0,-0.25, 0], cam_pt1, [0, 1, 0])
									if cv == '1': #mostly top view
										r = np.linalg.norm(cam_pt1)
										cam_pt2[1] = -1 * np.sqrt(r * 0.95)
										cam_pt2[0] = np.sqrt((r - cam_pt2[1]**2)/2)
										cam_pt2[2] = cam_pt2[0]
										cameraT = transformLookat([0,-0.25, 0], cam_pt2, [0, 1, 0])


								D['Camera Transform'] = copy.deepcopy(cameraT)


								# set ground plane
								D['Ground Plane Height'] = 0


								# set image save name
								# objname_objorient_preshape_handT_handO_camview
								ImageSaveName = '%s/%s_%s_%s_%s_%s_cam%s' %('GeneratedImages/Grasps', D['Model'], model_orientations[im], preshape_names[ipn], handT_names[iht], handO_names[iho], cam_view_names[icv])
								# if im == 0: #normal save name
								# 	ImageSaveName = '%s/%s_%s_%s_%s_cam%s' %('GeneratedImages/Grasps', D['Model'], preshape_names[ip], handT_names[it], handO_names[io], ic)
								# elif im == 1 and 'cylinder' in model_type: #sidways cylinder save name
								# 	ImageSaveName = '%s/%s_%s_%s_%s_cam%s' %('GeneratedImages/Grasps', D['Model'].replace('cylinder', 'cylinderRot'), preshape_names[ip], handT_names[it], handO_names[io], ic)
								# elif im == 1 and 'cone' in model_type: #sideways cone
								# 	ImageSaveName = '%s/%s_%s_%s_%s_cam%s' %('GeneratedImages/Grasps', D['Model'].replace('cone', 'coneRot'), preshape_names[ip], handT_names[it], handO_names[io], ic)
								D['Image Save Name'] = ImageSaveName

								L.append(D)
								count = count + 1


		with open(fn, 'wb') as file:
			writer = csv.DictWriter(file, headers)
			writer.writeheader()
			for l in L:
				writer.writerow(l)
		print("Successfully wrote to CSV file")

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
	T.testParam(curdir + '/HandCenteredImageGeneratorParameters.csv')
	# T.viewImagesSideBySide('cylinder', h = None, w = 33, e = 33, grasp_type = 'equidistant', grasp_approach = 'side', cam_view = 0)
	# T.viewImagesSideBySide('cylinder', h = None, w = 33, e = 33, grasp_type = 'equidistant', grasp_approach = 'side', cam_view = 1)



