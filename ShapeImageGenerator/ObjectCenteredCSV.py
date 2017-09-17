from ShapeImageGeneratorTest import ShapeImageGenerator




class ObjectCenteredCSV(object):
	def __init__(self):
		self.SIG = ShapeImageGenerator()

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