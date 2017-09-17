from ShapeImageGeneratorTest import ShapeImageGenerator
import os
curdir = os.path.dirname(os.path.realpath(__file__))
from openravepy import *
import copy
import numpy as np
import pdb



class HandCenteredCSV(object):
	def __init__(self, viewer = False):
		self.SIG = ShapeImageGenerator(viewer = viewer)

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




	def HandT(self, grasp, shape, h, w, e, obj_or, approach, hand_or, cv): #given a set of featuers, outputs the params to make an image
		D = dict()
		
		preshape_names = ['3fingerpinch', 'equidistant', 'hook', '2fingerpinch']
		model_orientations = ['h', 'w', 'e']
		handT_names = ['side', 'top']
		handO_names = ['up', '90', 'down', 'angled']
		cam_view_names = ['0', '1']
		 # 3 finger pinch
		 # equidistant
		 # hook
		 # 2 finger pinch
		preshapes = {'3 finger pinch': '0,0,%s,%s,%s,%s,%s,%s,%s,%s' %(0,0.0,0.0,0,0.0,0.0,0.0,0.0),
					 'equidistant': '0,0,%s,%s,%s,%s,%s,%s,%s,%s' %(np.pi/3,0.0,0.0,np.pi/3,0.0,0.0,0.0,0.0),
					 'hook': '0,0,%s,%s,%s,%s,%s,%s,%s,%s' %(np.pi,0.0,0.0,np.pi,0.0,0.0,0.0,0.0),
					 '2 finger pinch': '0,0,%s,%s,%s,%s,%s,%s,%s,%s' %(np.pi/2,0.0,0.0,np.pi/2,0.0,0.0,0.0,0.0)}

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
		clearance = 0.05

		D['Joint Angles'] = preshapes[grasp]
		D['Model'] = shape
		####################### set Hand Transform #######################
		handT = np.zeros((4,4))
		height_in_world = 0; extent_in_world = 0;
		if obj_or == 'w' and 'cone' in shape: # adjust height offset for rotated cone, width side down
			height_complete = h / (1 - a/100.0);
			w_gamma = np.arctan2(w/2, height_complete)
			height_in_world = 1.0 * (w * np.cos(w_gamma) - h * np.sin(w_gamma))
			extent_in_world = e
		elif obj_or == 'e' and 'cone' in shape: # adjust height offset for rotated cone, extent side down
			height_complete = h / (1 - a/100.0);
			e_gamma = np.arctan2(e/2, height_complete)
			height_in_world = 1.0 * (e * np.cos(e_gamma) - h * np.sin(e_gamma))
			extent_in_world = h / np.cos(e_gamma)
		elif obj_or == 'h': # no rotation to object
			height_in_world = h
			extent_in_world = e
		elif obj_or == 'w': # adjust height offset for rotated object, width side down
			height_in_world = w
			extent_in_world = e
		elif obj_or == 'e': #adjust height offset for rotated object, extent side down
			height_in_world = e
			extent_in_world = h

		if approach == 'side': # approach from side
			if grasp == '3fingerpinch': # 3 finger pinch
				if hand_or == 'up':
					handT = np.dot(matrixFromAxisAngle([0,0,np.pi/2]), np.eye(4)) # rotate hand around Z
			elif grasp == 'equidistant': #equidistant
				if hand_or == 'up': # claw, 180 degree rotation
					handT = np.dot(matrixFromAxisAngle([0,0,np.pi]), np.eye(4)) #rotate hand around Z so one finger is up
				elif hand_or == 'down':
					handT = np.dot(matrixFromAxisAngle([0,0,0]), np.eye(4)) # rotate hand around Z so two fingers are up
				elif hand_or == '90':
					handT = np.dot(matrixFromAxisAngle([0,0,np.pi/2]), np.eye(4)) # rotate hand around Z fingers are on side
				elif hand_or == 'angled': #45 degree rotation from up
					handT = np.dot(matrixFromAxisAngle([0,0,3*np.pi/4]), np.eye(4))
			elif grasp == 'hook': #hook
				if hand_or == 'up':
					handT = np.dot(matrixFromAxisAngle([0,0,np.pi]), np.eye(4)) # rotate hand pi around Z
				elif hand_or == '90':
					handT = np.dot(matrixFromAxisAngle([0,0,-np.pi/2]), np.eye(4)) # rotate hand pi around Z
			elif grasp == '2fingerpinch': #2 finger pinch
				handT = np.dot(matrixFromAxisAngle([0,0,np.pi]), np.eye(4)) # rotate hand pi around Z
			try:
				if height_in_world/2.0 < abs(grasp_height_offset[grasp][hand_or]): #need to clear ground plane
					# pdb.set_trace()
					handT[1,3] = grasp_height_offset[grasp][hand_or] #height offset, grasp specific
				else:
					handT[1,3] = -height_in_world/2.0
			except:
				pdb.set_trace()
			handT[2, 3] = -0.075 # offset for palm
		if approach == 'top': # approach from top
			if grasp == '3fingerpinch': #3 finger pinch
				if hand_or == 'up':
					handT = np.dot(matrixFromAxisAngle([0,0,np.pi/2]), np.eye(4)) # rotate hand pi/2 around Z
					handT = np.dot(matrixFromAxisAngle([-np.pi/2,0,0]), handT) # rotate hand pi/2 around X
				elif hand_or == 'angled':
					handT = np.dot(matrixFromAxisAngle([0,0,np.pi/2]), np.eye(4)) # rotate hand pi/2 around Z
					handT = np.dot(matrixFromAxisAngle([-np.pi/2,0,0]), handT) # rotate hand pi/2 around X
					handT = np.dot(matrixFromAxisAngle([0,np.pi/4,0]), handT) # rotate around y for fingers to corner
			elif grasp == 'equidistant': #equidistant
				if hand_or == 'up':
					handT = np.dot(matrixFromAxisAngle([0,0,np.pi]), np.eye(4)) # rotate hand pi around Z
					handT = np.dot(matrixFromAxisAngle([-np.pi/2,0,0]), handT) # rotate hand pi/2 around X
				if hand_or == 'angled':
					handT = np.dot(matrixFromAxisAngle([0,0,np.pi]), np.eye(4)) # rotate hand pi around Z
					handT = np.dot(matrixFromAxisAngle([-np.pi/2,0,0]), handT) # rotate hand pi/2 around X
					handT = np.dot(matrixFromAxisAngle([0,-np.pi/4,0]), handT) # rotate around y for fingers to corner
				if hand_or == '90':
					handT = np.dot(matrixFromAxisAngle([-np.pi/2,0,0]), np.eye(4)) # rotate hand pi/2 around X
					handT = np.dot(matrixFromAxisAngle([0,np.pi/2,0]), handT) # rotate hand pi/2 around Y
			elif grasp == 'hook': #hook
				if hand_or == 'up':
					handT = np.dot(matrixFromAxisAngle([0,0,-np.pi/2]), np.eye(4)) # rotate hand pi around Z
					handT = np.dot(matrixFromAxisAngle([-np.pi/2,0,0]), handT) # rotate hand pi/2 around X
				if hand_or == 'angled':
					handT = np.dot(matrixFromAxisAngle([0,0,-np.pi/2]), np.eye(4)) # rotate hand pi around Z
					handT = np.dot(matrixFromAxisAngle([-np.pi/2,0,0]), handT) # rotate hand pi/2 around X
					handT = np.dot(matrixFromAxisAngle([0,np.pi/4,0]), handT) # rotate around y for fingers to corner
			elif grasp == '2fingerpinch': #2 finger pinch
				if hand_or == 'up':
					handT = np.dot(matrixFromAxisAngle([-np.pi/2,0,0]), np.eye(4)) # rotate hand pi/2 around X
					handT = np.dot(matrixFromAxisAngle([0, np.pi, 0]), handT) # rotate hand pi around Y
				if hand_or == 'angled':
					handT = np.dot(matrixFromAxisAngle([-np.pi/2,0,0]), np.eye(4)) # rotate hand pi/2 around X
					handT = np.dot(matrixFromAxisAngle([0, np.pi, 0]), handT) # rotate hand pi around Y
					# block view of skinny objects, but rotating it beyond 45 changes feature of object being examined
					handT = np.dot(matrixFromAxisAngle([0,-np.pi/4,0]), handT) # rotate around y for fingers to corner

			# unlikely for there to be a height collision
			handT[1,3] = -height_in_world + -0.075 + -clearance # offset for palm

		D['Hand Matrix'] = copy.deepcopy(np.round(handT, 4))




		########################   set Object Transfrom    ########################
		ModelT = np.eye(4)
		if obj_or == 'w' and 'cone' in model: # rotate on its w-side (slanted so needs extra factor)
			ModelT = np.dot(matrixFromAxisAngle([0, 0, np.pi/2 + w_gamma]), ModelT)
		elif obj_or == 'e' and 'cone' in model: # rotate on its e-side (slanted so needs extra factor)
			ModelT = np.dot(matrixFromAxisAngle([-np.pi/2 - e_gamma, 0, 0]), ModelT)
		elif obj_or == 'w': # rotate on its w-side
			ModelT = np.dot(matrixFromAxisAngle([0, 0, np.pi/2]), ModelT)
		elif obj_or == 'e': # rotate on its e-side
			ModelT = np.dot(matrixFromAxisAngle([np.pi/2, 0, 0]), ModelT)
		if approach == 'side': # approach from side, hand stays stationary
			ModelT[1,3] = -height_in_world/2.0
			ModelT[2,3] = extent_in_world/2.0 + clearance
		elif approach == 'top': # approach from the top, object bottom stays stationary
			ModelT[1,3] = -height_in_world/2.0

		D['Model Matrix'] = copy.deepcopy(ModelT)


		# Set Camera Transform
		cameraT = np.zeros((4,4))
		if approach == 'side': # approach from side, focus on palm
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

		if approach == 'top': #approach from top, focus on bottom of object
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
		ImageSaveName = '%s_%s_%s_%s_%s_cam%s' %(D['Model'], obj_or, grasp, approach, hand_or, cv)
		D['Image Save Name'] = ImageSaveName

		return D
