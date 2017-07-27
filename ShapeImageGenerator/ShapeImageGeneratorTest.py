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

	def loadSTLFileList(self): # get all STL files in directory
		self.STLFileList = list()
		directory = curdir + '/../ShapeGenerator/Shapes'
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
					params_list[ip][k] = np.array(params_list[ip][k].split(',')).astype('float')#convert to numpy array
				elif 'Image Size' == k:
					i = 1 # should do soemthing here
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
			if ((shapes == None) or (params['Model'].split('_')[0] in shapes)): # allows only a single set of shapes to be made from list. Mostly during development
				imageSuccess = self.createImageFromParameters(params)
				# if not imageSuccess:
				# 	pdb.set_trace()
				print("Current: %s" %counter)

	def createImageFromParameters(self, params): # creates image from a single set of parameters
		objLoadSuccess = self.loadObjectFromParameters(params)
		if objLoadSuccess:
			self.groundPlane.createGroundPlane(y_height = self.Obj.h/2.0/100)
			# self.vis.changeBackgroundColor(self.groundPlane.groundPlane.GetLinks()[0].GetGeometries()[0].GetAmbientColor())
			self.Obj.changeColor('purpleI')
			self.Hand.changeColor('yellowI')
			cam_params = params['Camera Transform']
			self.vis.setCamera(cam_params[0], cam_params[1], cam_params[2])
			if params['Joint Angles'] is not '' and params['Hand Matrix'] is not '':
				self.Hand.show()
				self.Hand.setJointAngles(params['Joint Angles'])
				self.Hand.obj.SetTransform(params['Hand Matrix'])
			else: #for images where no hand is shown
				self.Hand.hide()
			self.Obj.obj.SetTransform(params['Model Matrix'])
			if np.sum(self.Obj.obj.GetTransform() - matrixFromAxisAngle([0,0,np.pi/2])) < 1e-4: #if object is rotated 90, use different dimension
				self.groundPlane.createGroundPlane(y_height = self.Obj.w/2.0/100)
			else: #offset by height if no rotation -- this is not a great solution when object starts to rotate!
				self.groundPlane.createGroundPlane(y_height = self.Obj.h/2.0/100)
			# this should definitely be taken care of when making the spreadsheet
			pts = self.Hand.getContactPoints()
			while len(pts) > 0:
				self.Hand.moveY(-0.001)
				pts = self.Hand.getContactPoints()
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

	def loadSceneFromParameters(self, params):
		self.loadObjectFromParameters(params)
		self.loadHandFromParameters(params)

	def getParameterFromList(self, list_indx): return self.params_list[list_indx] #get parameters from a location in the list



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

	def Test5(self): # Description: Read parameter file and create multiple images
		fn = curdir + '/ImageGeneratorParameters.csv'
		self.SIG.readParameterFile(fn)
		# self.SIG.createImagesFromParametersList(shapes = ['cube'])
		# self.SIG.createImagesFromParametersList(shapes = ['ellipse'])
		# self.SIG.createImagesFromParametersList(shapes = ['cylinder'])
		# self.SIG.createImagesFromParametersList(shapes = ['cone'])
		# self.SIG.createImagesFromParametersList(shapes = ['handle'])
		# self.SIG.createImagesFromParametersList(shapes = ['vase'])
		self.SIG.createImagesFromParametersList()
		print("Image Generation Complete!")

	def Test6(self): # Description: Create CSV file for making images
		fn = curdir + '/ImageGeneratorParameters.csv'
		self.SIG.loadSTLFileList()
		# create list of dictionaries
		L = list()
		headers = ['Joint Angles', 'Hand Matrix', 'Model', 'Model Matrix', 'Camera Transform','Image Save Name', 'Image Size']
		CameraTransform = ['%s, %s, %s' %(60, -2.355, -.449), '%s, %s, %s' %(60, -2.355, -np.pi/2.2)]
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
		ModelMatrix.append(np.array([[ 0, -1,  0,  0], [ 1,  0,  0,  0], [ 0,  0,  1,  0], [ 0,  0,  0,  1]])) # rotated 90 degrees around e

		
		for model in self.SIG.STLFileList:
			for ip, preshape in enumerate(preshapes):
				for it, handT in enumerate(handTs):
					for ic, cameraT in enumerate(CameraTransform):
						for im, modelT in enumerate(ModelMatrix):
							model_type = model.split('/')[-1].strip('.stl')
							if im == 1 and 'cylinder' not in model_type: # skip second model matrix orientation for all objects except cylinder
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
								# i think the limit should be applied for each grasp?
								h_limit = np.array([-0.08, -0.04, 0.06, -0.025]) # this is specific for each grasp!
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

								D['Hand Matrix'] = copy.deepcopy(handT[ip])
								D['Model Matrix'] = ModelMatrix[im]
								D['Camera Transform'] = cameraT
								if im == 0: #normal save name
									ImageSaveName = '%s/%s_%s_%s_cam%s' %('GeneratedImages/Grasps', D['Model'], preshape_names[ip], handT_names[it], ic)
								elif im == 1: #sidways cylinder save name
									ImageSaveName = '%s/%s_%s_%s_cam%s' %('GeneratedImages/Grasps', D['Model'].replace('cylinder', 'cylinderRot'), preshape_names[ip], handT_names[it], ic)
								D['Image Save Name'] = ImageSaveName
								D['Image Size'] = '' # need to do something for this step -- image size

								if h == 17/100.0 and w == 17/100.0 and e == 17/100.0: #only capturing the "medium" object with grasps
									if a is None or a == 30 or a == 8.5/100:
										L.append(D)


		# for model in self.SIG.STLFileList: #capturing images of all objects
		# 	D = dict.fromkeys(headers)
		# 	D['Camera Transform'] = CameraTransform[0]
		# 	D['Model'] = model.split('/')[-1].strip('.stl')
		# 	D['Model Matrix'] = np.eye(4)
		# 	D['Image Save Name'] = '%s/%s_nohand' %('GeneratedImages/ObjectsOnly', D['Model'])
		# 	L.append(D)


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
		self.SIG.createImageFromParameters(self.SIG.params_list[81])
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

if __name__ == '__main__':
	T = Tester()
	T.Test6()
	T.Test5()
	# T.Test7()
	# T.Test10()
	# T.Test8()
	



