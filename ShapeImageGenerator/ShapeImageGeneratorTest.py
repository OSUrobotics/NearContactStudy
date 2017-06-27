import sys, os, copy, csv, re
from openravepy import *
import pdb
curdir = os.path.dirname(os.path.realpath(__file__))
classdir = curdir +'/../Interpolate Grasps/'
sys.path.insert(0, classdir) # path to helper classes
from Visualizers import Vis, GenVis, HandVis, ObjectGenericVis
import numpy as np 
import time
import matplotlib.pyplot as plt
import subprocess



class ShapeImageGenerator(object):
	def __init__(self):
		self.model_path = 'blah'
		self.vis = Vis()
		self.Hand = HandVis(self.vis)
		self.Hand.loadHand()
		self.Hand.localTranslation(np.array([0,0,-0.075])) #offset so palm is at 0,0,0
		self.Obj = ObjectGenericVis(self.vis)
		self.loadSTLFileList()

	def loadSTLFileList(self): # get all STL files in directory
		self.STLFileList = list()
		directory = curdir + '/../ShapeGenerator/Shapes/'
		for root, dirs, filenames in os.walk(directory):
			if filenames != []:
				for fname in filenames:
					if os.path.splitext(fname)[1] == '.stl': #only want text files
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
		

	def loadObject(self, objtype, h, w, e, a): # loads stl object into scene
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
		self.Obj.changeColor(alpha = alpha) # this can be changed to changeColor

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
					params_list[ip][k] = np.array(params_list[ip][k].split(',')).astype('float')#convert to numpy array
				elif 'Image Save Name' == k:
					params_list[ip][k] += '.png' # add extension
				elif 'Model' == k:
					params_list[ip][k] += '.stl' # add extension
				elif 'Model Matrix' == k: #array had brackets so had to do this!
					mat_str = params_list[ip][k]
					mat_re = re.findall(r'\[.*?\]', mat_str)
					mat_strip = [t.strip('[]') for t in mat_re]
					# pdb.set_trace()
					mat_num = np.array([t.split() for t in mat_strip]).astype('float')
					params_list[ip][k] = mat_num
				elif 'Camera Transform' == k:
					params_list[ip][k] = np.array(params_list[ip][k].split(',')).astype('float')#convert to numpy array
				elif 'Image Size' == k:
					i = 1 # should do soemthing here
				else:
					print('Unexpeted Key: %s' %(k))
		self.params_list = params_list
		return self.params_list

	def createImagesFromParametersList(self): # creates images from a list of parameters
		for params in self.params_list:
			self.createImagesFromParameters(params)

	def createImagesFromParameters(self, params): # creates image from a single set of parameters
		shape, h, w, e, a = self.valuesFromFileName(params['Model'])
		objLoadSuccess = self.loadObject(shape, h, w, e, a)
		if objLoadSuccess:
			self.Obj.changeColor('greenI')
			self.Hand.changeColor('blueI')
			cam_params = params['Camera Transform']
			self.vis.setCamera(cam_params[0], cam_params[1], cam_params[2])
			self.Hand.setJointAngles(params['Joint Angles'])
			self.Obj.obj.SetTransform(params['Model Matrix'])
			self.vis.takeImage(params['Image Save Name'])

			print("Image Recorded: %s" %params['Image Save Name'])
		else:
			print("Model Not Found: %s" %params['Model'])




class Tester(object): # this is just meant to test different parts of the class
	def __init__(self):
		## TODO: make gui sliders for moving hand into position to make creating input sheet easier
		self.SIG = ShapeImageGenerator()

	def Test1(self): # Description: load file and move camera around
		SIG = self.SIG
		cube_list = [f for f in SIG.STLFileList if 'cube' in f]
		for f in cube_list[0:10]:
		# for f in SIG.STLFileList:
			shape, h, w, e = SIG.valuesFromFileName(f)
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
			SIG.vis.setCamera(50, -3*np.pi/4, -np.pi/7)
			f_dict = SIG.Obj.features
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

	def Test5(self): # Description: Read parameter file and create image
		fn = curdir + '/ImageGeneratorParameters.csv'
		self.SIG.readParameterFile(fn)
		self.SIG.createImagesFromParametersList()

	def Test6(self): # Description: Create CSV file for making images
		fn = curdir + '/ImageGeneratorParameters.csv'
		self.SIG.loadSTLFileList()
		# create list of dictionaries
		L = list()
		headers = ['Joint Angles', 'Model', 'Model Matrix', 'Camera Transform', 'Image Save Name', 'Image Size']
		CameraTransform = '%s, %s, %s' %(50, -2.355, -.449)
		preshapes = ['0,0,%s,%s,%s,%s,%s,%s,%s,%s' %(0,0.1,0.1,0,0.1,0.1,0.1,0.1),
					 '0,0,%s,%s,%s,%s,%s,%s,%s,%s' %(1,0.1,0.4,1,0.1,0.4,0.1,0.4)]
		for model in self.SIG.STLFileList:
			for ip, preshape in enumerate(preshapes):
				D = dict()
				D[headers[0]] = preshape
				D[headers[1]] = model.split('/')[-1].strip('.stl')
				e =  float(D[headers[1]].split('_')[3].strip('e'))/100/2 + 0.01 #position object extent + buffer away from origin (palm)
				ModelMatrix = np.array([[ 1.,  0.,  0.,  0.],  [ 0.,  1.,  0.,  0.],  [ 0.,  0.,  1.,  e],  [ 0.,  0.,  0.,  1.]] )
				D[headers[2]] = ModelMatrix
				D[headers[3]] = CameraTransform
				ImageSaveName = '%s_grasp%s' %(D[headers[1]], ip)
				D[headers[4]] = ImageSaveName
				D[headers[5]] = '' # need to do something for this step
				L.append(D)


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
		pdb.set_trace()
		self.SIG.createImagesFromParameters(self.SIG.params_list[323])
		pdb.set_trace()


if __name__ == '__main__':
	T = Tester()
	T.Test5()
	



