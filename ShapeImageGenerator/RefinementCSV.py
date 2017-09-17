from ShapeImageGeneratorTest import ShapeImageGenerator
import os
curdir = os.path.dirname(os.path.realpath(__file__))
import pdb
import csv
import numpy as np
from openravepy import *
import copy


class RefinementCSV(object):
	def __init__(self):
		self.SIG = ShapeImageGenerator(viewer = False)
		i = 1

	def generateImagesFromCSV(self, fn = 'RefinementCSV.csv'):
		self.SIG.readParameterFile(fn)
		self.SIG.createImagesFromParametersList(obj_path = '/home/ammar/Documents/Projects/NearContactStudy/NearContact20Survey/QualtricsDataProcessing/RefinementShapes/')
		print("Image Generation Complete!")
		pdb.set_trace()

	def ImageParamGen(self, file_list = None):
		# input is a csv file with the parameters for the questions
		# yields the next value to take an image of

		if file_list is None:
			root = '/home/ammar/Documents/Projects/NearContactStudy/NearContact20Survey/QualtricsDataProcessing/'
			file_list = ['0.5_NonparametricNextQuestions.csv', '0.0001_NonparametricNextQuestions.csv', '-0.5_NonparametricNextQuestions.csv']
			files = [root + i for i in file_list]

		for FN in files:
			with open(FN, 'rb') as csvfile:
				reader = csv.reader(csvfile)
				for row in reader:
					if len(row) == 1: #its the question description
						try:
							shape,_,_,_,obj_or,grasp,approach,hand_or = row[0].split('_')
						except:
							shape,_,_,_,_,obj_or,grasp,approach,hand_or = row[0].split('_') #for when a cone happens!
						pass
					else:
						row.pop(0) #removes the descriptor (i.e. Question X)
						row = np.array(row).astype(float).reshape(-1,3)
						for r in row:
							yield shape, r, obj_or, grasp, approach, hand_or

	def CSV(self):
		L = list()
		headers = ['Joint Angles', 'Hand Matrix', 'Model', 'Model Matrix', 'Camera Transform', 'Ground Plane Height','Image Save Name', 'Image Size']
		fn = curdir + '/RefinementCSV.csv'
		self.SIG.loadSTLFileList(directory = '/home/ammar/Documents/Projects/NearContactStudy/NearContact20Survey/QualtricsDataProcessing/RefinementShapes')

		######## Features that are independent of any other features of Scene ##################
		 # 3 finger pinch
		 # equidistant
		 # hook
		 # 2 finger pinch
		preshapes = {'3fingerpinch': '0,0,%s,%s,%s,%s,%s,%s,%s,%s' %(0,0.0,0.0,0,0.0,0.0,0.0,0.0),
					 'equidistant':  '0,0,%s,%s,%s,%s,%s,%s,%s,%s' %(np.pi/3,0.0,0.0,np.pi/3,0.0,0.0,0.0,0.0),
					 'hook':		 '0,0,%s,%s,%s,%s,%s,%s,%s,%s' %(np.pi,0.0,0.0,np.pi,0.0,0.0,0.0,0.0),
					 '2fingerpinch': '0,0,%s,%s,%s,%s,%s,%s,%s,%s' %(np.pi/2,0.0,0.0,np.pi/2,0.0,0.0,0.0,0.0)}
		handO_names = ['up', '90', 'down', 'angled']
		 ############# Features that depend on other features in Scene #######
		handT_top = list((np.zeros((4,4)), np.zeros((4,4)), np.zeros((4,4)), np.zeros((4,4))))
		handT_side = list((np.zeros((4,4)), np.zeros((4,4)), np.zeros((4,4)), np.zeros((4,4))))
		handTs = [handT_side, handT_top]
		grasp_height_offset = dict().fromkeys(preshapes.keys())
		for key in grasp_height_offset.keys():
			grasp_height_offset[key] = dict().fromkeys(handO_names)
		# grasp_height_offset['3fingerpinch'] = dict().fromkeys(handO_names)
		grasp_height_offset['3fingerpinch']['up'] = -0.05
		# grasp_height_offset['equidistant'] = dict().fromkeys(handO_names)
		grasp_height_offset['equidistant']['up'] = -0.095
		grasp_height_offset['equidistant']['down'] = -0.17	
		grasp_height_offset['equidistant']['90'] = -0.17
		grasp_height_offset['equidistant']['angled'] = -0.095		
		# grasp_height_offset['hook'] = dict().fromkeys(handO_names)

		grasp_height_offset['hook']['up'] = -0.045
		grasp_height_offset['hook']['90'] = -0.045
		# grasp_height_offset['2fingerpinch'] = dict().fromkeys(handO_names)
		grasp_height_offset['2fingerpinch']['up'] = -0.045

		# handT_initial = {'side':
		# 					{'3fingerpinch': 
		# 						{'up': np.dot(matrixFromAxisAngle([0,0,np.pi/2]), np.eye(4)) # rotate hand around Z
		# 						},
		# 					'equidistant':
		# 						{'up': np.dot(matrixFromAxisAngle([0,0,np.pi]), np.eye(4)), #rotate hand around Z so one finger is up
		# 						 'down': np.dot(matrixFromAxisAngle([0,0,0]), np.eye(4)), # rotate hand around Z so two fingers are up
		# 						 '90': np.dot(matrixFromAxisAngle([0,0,np.pi/2]), np.eye(4)), # rotate hand around Z fingers are on side
		# 						 'angled': np.dot(matrixFromAxisAngle([0,0,3*np.pi/4]), np.eye(4)) # 45 degree rotation from up
		# 						},
		# 					'hook':
		# 						{'up': np.dot(matrixFromAxisAngle([0,0,np.pi]), np.eye(4)), # rotate hand pi around Z
		# 						 '90': np.dot(matrixFromAxisAngle([0,0,-np.pi/2]), np.eye(4)), # rotate hand pi around Z
		# 						},
		# 					'2fingerpinch':
		# 						{'up': np.dot(matrixFromAxisAngle([0,0,np.pi]), np.eye(4)),
		# 						 '90': np.dot(matrixFromAxisAngle([0,0,np.pi]), np.eye(4)),
		# 						 'down': np.dot(matrixFromAxisAngle([0,0,np.pi]), np.eye(4)),
		# 						 'angled': np.dot(matrixFromAxisAngle([0,0,np.pi]), np.eye(4)),
		# 					  	}
		# 					},
		# 				'top': 
		# 					{'3fingerpinch':
		# 						{'up':
		# 						 'angled':
		# 						},
		# 					''
		# 					}

		# 				}

		for cv in (0,1):
			imageGen = self.ImageParamGen()
			for shape, dims, obj_or, grasp, approach, hand_or in imageGen:
				if shape != 'cube': #only doing cubes right now!
					continue
				D = dict.fromkeys(headers)
				h, w, e = dims[:]
				D['Joint Angles'] = preshapes[grasp]
				# pdb.set_trace()
				D['Model'] = '%s_h%.2f_w%.2f_e%.2f' %(shape, h.round(2), w.round(2), e.round(2))
				if shape == 'cone':
					D['Model'] = '%s_h%.2f_w%.2f_e%.2f_a%s' %(shape, h.round(2), w.round(2), e.round(2), 25)
				D['Model'] = D['Model'].replace('.','D')
				h /= 100.0
				w /= 100.0
				e /= 100.0

				clearance = 0.05
				# set Hand Transform
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

				# set Object Transfrom
				ModelT = np.eye(4)
				if obj_or == 'w' and 'cone' in shape: # rotate on its w-side (slanted so needs extra factor)
					ModelT = np.dot(matrixFromAxisAngle([0, 0, np.pi/2 + w_gamma]), ModelT)
				elif obj_or == 'e' and 'cone' in shape: # rotate on its e-side (slanted so needs extra factor)
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
					if cv == 0: #isometric view
						cameraT = np.array([[-0.70626164,  0.30729662, -0.63777996,  1.1007],
								       [ 0.        ,  0.90088162,  0.43406487, -0.7491],
								       [ 0.70795091,  0.30656337, -0.63625813,  1.0981],
								       [ 0.        ,  0.        ,  0.        ,  1.        ]])
					elif cv == 1: #mostly top view
						cameraT = np.array([[-0.70626164,  0.70074499, -0.10075192,  0.1795	],
								       [ 0.        ,  0.14231484,  0.98982144, -1.763 ],
								       [ 0.70795091,  0.69907292, -0.10051151,  0.179 ],
								       [ 0.        ,  0.        ,  0.        ,  1.        ]])

				if approach == 'top': #approach from top, focus on bottom of object
					cam_pt1 = [1.0361, -0.6268, 1.0361]
					cam_pt2 = copy.deepcopy(cam_pt1)
					if cv == 0: # isometric view
						cameraT = transformLookat([0,-0.25, 0], cam_pt1, [0, 1, 0])
					if cv == 1: #mostly top view
						r = np.linalg.norm(cam_pt1)
						cam_pt2[1] = -1 * np.sqrt(r * 0.95)
						cam_pt2[0] = np.sqrt((r - cam_pt2[1]**2)/2)
						cam_pt2[2] = cam_pt2[0]
						cameraT = transformLookat([0,-0.25, 0], cam_pt2, [0, 1, 0])

				D['Camera Transform'] = copy.deepcopy(cameraT)

				# set ground plane
				D['Ground Plane Height'] = 0

				#set image save name
				base_dir = '/home/ammar/Documents/Projects/NearContactStudy/NearContact20Survey/QualtricsDataProcessing/RefinementImages'
				ImageSaveName = '%s/%s_%s_%s_%s_%s_cam%s' %(base_dir, D['Model'], obj_or, grasp, approach, hand_or, cv)
				
				D['Image Save Name'] = ImageSaveName

				L.append(D)


		self.writeDictToCSV(L, fn, headers)
		

	def writeDictToCSV(self, D, file_name, headers):
		with open(file_name, 'wb') as file:
			writer = csv.DictWriter(file, headers)
			writer.writeheader()
			for l in D:
				writer.writerow(l)
		print("Successfully wrote to CSV file")


if __name__ == '__main__':
	R = RefinementCSV()
	R.CSV()
	# R.generateImagesFromCSV()