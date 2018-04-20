
import numpy as np
import sys, os, pdb, copy, subprocess, time
from openravepy import *
from Colors import ColorsDict, bcolors
from Utils import UtilTransforms
from stlwriter import Binary_STL_Writer
base_path = os.path.dirname(os.path.realpath(__file__))
# from NearContactStudy import JOINT_ANGLES_NAMES

'''
Classes in this document are for working in OpenRave specific to the Barrett Hand and generated STL objects
The objects are meant to make it easier to work in OpenRave by dealing with quirks

General overview:
initialize a Vis class object
Then initialize other objects (hands, boxes, cones, etc.) with the Vis class

Significantly more commenting is necessary to make this usable

'''

class Vis(object): #General Class for visualization
	def __init__(self, viewer = True):
		self.env = Environment()
		self.colors = dict()
		self.colors = ColorsDict.colors
		self.points = list()
		# an arbitrary camera Angle that I picked
		self.cameraTransform = np.array([[-0.46492937, -0.50410198,  0.72781995, -0.32667211],
   										[-0.10644389, -0.78428209, -0.6112048 ,  0.29396212],
       									[ 0.8789257 , -0.36163905,  0.3109772 , -0.17278717],
       									[ 0.        ,  0.        ,  0.        ,  1.        ]])
		if viewer:
			self.env.SetViewer('qtcoin')
			# self.env.SetViewer('qtosg')
			self.viewer = self.env.GetViewer()
			self.viewer.SetCamera(self.cameraTransform)
			self.cameraFocusPoint = [0,0,0]
			self.viewer.SetSize(1215,960)
		# pdb.set_trace()
		# sensor = RaveCreateSensor(self.env, 'offscreen_render_camera')
		# sensor.SendCommand('setintrinsic 529 525 328 267 0.01 10')
		# sensor.SendCommand('setdims 640 480')
		# sensor.Configure(Sensor.ConfigureCommand.PowerOn)

		# sensor.SetTransform([])
		# data = sensor.GetSensorData();
		# matplotlib.pyplot.imshow(img)


	def changeBackgroundColor(self, color):
		#values should be between 0 and 1.  values are scaled up to a point, and then outside of that I don't know what happens
		if len(color) != 3:
			print('Invalid Color Array.  Must have only 3 elements')
			return
		self.viewer.SetBkgndColor(color)

	def close(self): # Close Env
		self.env.Destroy()
		self.viewer.quitmainloop()

	def reset(self): # Reset Env
		self.env.Reset()

	def drawPoints(self, points, c = 'pink'): # Draw points
		points = np.array(points).astype('float')
		if c in self.colors.keys():
			color_vals = self.colors[c]
		else:
			color_vals = c
		self.points.append(self.env.plot3(points = points, pointsize=.005,colors = color_vals, drawstyle = 2))

	def clearPoints(self): # Clear all Points
		self.points = list()

	def DrawGlobalAxes(self): # Draw axes at origin
		self.axes = misc.DrawAxes(self.env, [1,0,0,0,0,0,0])

	def takeImage(self, fname, delay = True): # Take an image of the OpenRave window
		try:
			if not os.path.isdir(os.path.split(fname)[0]): #make a directory if it doesn't exist
				os.makedirs(os.path.split(fname)[0])
		except:
			pass
		self.env.UpdatePublishedBodies()
		try: #there is a bug in my version of Linux.  This should work with the proper drivers setup
			Im = self.viewer.GetCameraImage(640,480,  self.viewer.GetCameraTransform(),[640,640,320,240])
			plt.imshow(Im)
		except: #this is more robust, but requires that particular window to be selected
			if not delay:
				subprocess.call(["gnome-screenshot", "-w", "-B", "--file="+fname])
			else:
				subprocess.call(["gnome-screenshot", "-w", "-B", "--file="+fname, '--delay=1'])
				time.sleep(1)

	def setCameraFocusPoint(self, pt): # sent the center point that the camera rotates around with setCamera
		if len(pt) == 3:
			self.cameraFocusPoint = np.array(pt)
		else:
			print('Invalid Input')

	def setCamera(self, dist, az, el): # Description: Sets camera location pointed at center at a distance, azimuth, and elevation
		#This can be re-written to be more efficient (unneeded operations)
		cam_T_zero = np.eye(4)
		cam_p_zero = poseFromMatrix(np.eye(4))
		cam_p_dist = cam_p_zero;
		cam_p_dist[4:] = np.array([0, 0, -1*dist]).astype('float')/100 #Distance should be in cms. Negative so that it faces center
		cam_T_dist = matrixFromPose(cam_p_dist)
		rot_AA_el = [el, 0, 0]
		rot_mat_el = matrixFromAxisAngle(rot_AA_el)
		rot_el = np.dot(rot_mat_el, cam_T_dist)
		rot_AA_az = [0, az, 0]
		rot_mat_az = matrixFromAxisAngle(rot_AA_az)
		rot_new = np.dot(rot_mat_az, rot_el)
		# pdb.set_trace()
		# rot_new[0:3, 3] = trasnformPoints(rot_new, self.cameraFocusPoint)
		self.viewer.SetCamera(rot_new)
		# pdb.set_trace()

		return rot_new

	#TODO!!!!
	def getCamera(self): # Get distance, azimuth, and elevation of camera in current scene
		# this is an inverse kinematics problem.  it will take a little bit of effort
		# force camera to look at point (0,0,0)
		cur_T = self.viewer.GetCameraTransform()
		lookat = [0,0,0] # origin
		# up_vec = cur_T[0:3,1] # up vector
		rot_az_el = np.hstack((cur_T[0:3,1:], np.array([0,0,0]).reshape(3,1)))
		up_vec = np.dot(np.array([0,0,1]), rot_az_el)
		cam_pos = cur_T[0:3,3] # camera position
		new_T1 = transformLookat(lookat, cam_pos, up_vec)
		pdb.set_trace()
		self.viewer.SetCamera(new_T1)
		camAA = axisAngleFromRotationMatrix(new_T1)
		el, az, __ = camAA
		dist = np.linalg.norm(cam_pos) * 100 # convert to cm
		new_T2 = self.setCamera(dist, az, el)

class GenVis(object): # General class for objects in visualization
	def __init__(self, V):
		self.vis = V
		self.env = V.env
		self.obj = None
		self.TClass = None
		self.bcolors = bcolors
		self.axes = list()
		self.colors = dict()
		self.colors = ColorsDict.colors

	def hide(self): self.obj.SetVisible(0) # hide obj

	def show(self): self.obj.SetVisible(1) # show obj

	def objExists(self): #check if an object is in scene
		if self.obj is None:
			self.bcolors.printFail("Load object first!")

	def QCheck(self, Q): # check if array is a quaternion
		if len(Q) != 4:
			self.bcolors.printFail("Vector is not a Quaternion")

	def TLCheck(self, TL): # check if an array is a translation vector
		if len(TL) != 3:
			self.bcolors.printFail("Vector is not Translation")

	def objCheck(self): # check if object exists
		if self.obj is not None:
			self.vis.env.Remove(self.obj) #remove object before adding a new one otherwise it gets abandoned in space!

	def globalTransformation(self, T): # apply global Transformation to object
		if T.shape == (4,4):
			self.obj.SetTransform(T)
		elif T.shape == (7,):
			self.obj.SetTransform(matrixFromPose(T))
		else:
			print("Did not recognize Transform Type")

	def getGlobalTransformation(self):
		return self.obj.GetTransform()

	def globalMove(self,T): # apply global Translation to object
		T_new = UtilTransforms.TL2T(T)
		self.obj.SetTransform(T_new)

	def globalQuatMove(self, Q): # apply global Rotation from Quaternion
		self.objExists(), self.QCheck(Q)
		T = matrixFromQuat(Q)
		self.globalTransformation(T)

	def globalQuatTranslationMove(self, Q, Translation): # apply global Transformation from Quaternion and Translation
		print("This needs to be checked!!")
		pdb.set_trace()
		self.QCheck(Q), Self.TLCheck(Translation)
		RotationMatrix = matrixFromQuat(Q)
		self.vis.drawPoints(Translation)
		T = UtilTransforms.RTL2T(RotationMatrix, Translation)
		pdb.set_trace()
		T = UtilTransforms.AddTranslation(self.objCentroid, T) #what is this doing?
		self.globalTransformation(T)

	def addObjectAxes(self): # Add local axes to object (will not move with object!)
		# a minor bug in openrave that doesn't allow using the name to set axes
		self.axes.append(misc.DrawAxes(self.env, self.obj.GetTransform(), dist = 1))

	def clearAxes(self): self.axes = None # clear all axes created relative to this object

	def changeColor(self, color = None, alpha = None): # change color of object.  Sets all sub features to same color
		if color is None and alpha is None: # random color
			color = np.random.rand(3)
			alpha = self.obj.GetLinks()[0].GetGeometries()[0].GetTransparency()
		elif color is not None and alpha is None: # keep transparency the same
			alpha = self.obj.GetLinks()[0].GetGeometries()[0].GetTransparency()
		elif color is None and alpha is not None: #only want to change transparency but keep color the same
			color = self.obj.GetLinks()[0].GetGeometries()[0].GetDiffuseColor()
		if type(color) is str: #loads from dictionary
			color = self.colors[color]
		#TODO: add a check to cycle through and verify colors are correct.  sometimes color change doesn't seem to work
		for link in self.obj.GetLinks():
			for geos in link.GetGeometries():
				geos.SetAmbientColor([0.9, 0.9, 0.9]) # Ambient color set to the same as the robot hand in bhand.dae file
				geos.SetDiffuseColor(color)
				geos.SetTransparency(alpha)

	def localRotation(self, R): # apply a local rotation. translate to origin, rotate, translate back
		T = self.obj.GetTransform()
		T_pose = poseFromMatrix(T)
		# undo position change
		T_zero = poseFromMatrix(T)
		T_zero[4:] = 0
		T_zero = matrixFromPose(T_zero)
		self.globalTransformation(T_zero)
		# rotate in new frame
		rot = matrixFromQuat(quatFromRotationMatrix(R)) #change from 3x3 to 4x4
		T_rot = np.dot(T_zero, rot)
		self.globalTransformation(T_rot)
		# move back to position
		self.localTranslation(T_pose[4:])
		return T_rot

	def localTranslation(self, TL): # apply local translation
		T = self.obj.GetTransform()
		T_pose = poseFromMatrix(T)
		TL = np.array(TL).reshape(3,) #force into correct format
		T_pose_new = copy.deepcopy(T_pose)
		T_pose_new[4:] += TL
		self.globalTransformation(matrixFromPose(T_pose_new))
		return T_pose_new

	def linearInterp(self, array1, array2, alpha): # linear interpolation between two arrays
		array_interp = array1 * (1 - alpha) + array2 * (alpha)
		return array_interp

	def moveX(self, x_dist): self.localTranslation([x_dist, 0, 0]) # move in x direction

	def moveY(self, y_dist): self.localTranslation([0, y_dist, 0]) # move in y direction
        
	def moveZ(self, z_dist): self.localTranslation([0, 0, z_dist]) # move in z direction

	def rotX(self, x_rot): self.localRotation(matrixFromAxisAngle([x_rot, 0, 0])) # rot in x direction

	def rotY(self, y_rot): self.localRotation(matrixFromAxisAngle([0, y_rot, 0])) # rot in y direction

	def rotZ(self, z_rot): self.localRotation(matrixFromAxisAngle([0, 0, z_rot])) # rot in z direction

	def remove(self):
		self.vis.env.Remove(self.obj) # remove object from scene

	#can all STL functions go into GenVis?
	def getSTLFeatures(self):
		links = self.obj.GetLinks()
		all_vertices = []
		all_faces = []
		ind = 0
		# I don't know what is happening here
		for link in links:
			vertices = link.GetCollisionData().vertices
			faces = link.GetCollisionData().indices
			if ind == 0:
				faces = np.add(faces,ind)
			else:
				faces = np.add(faces,ind+1)
			try:
				ind = faces[-1][-1]
			except:
				pass
		
			#print "link: ", link, "\nStarting index for this link: ", len(all_vertices)
			link_pose = poseFromMatrix(link.GetTransform())
			transform_vertices = poseTransformPoints(link_pose, vertices)
			all_vertices.extend(transform_vertices.tolist())
			all_faces.extend(faces.tolist())
		return all_faces, all_vertices

	def writeSTL(self, save_filename, faces, vertices):
		faces_points = []
		for vec in faces:
			faces_points.append([vertices[vec[0]],vertices[vec[1]],vertices[vec[2]]])

		with open(save_filename,'wb') as fp:
			writer = Binary_STL_Writer(fp)
			writer.add_faces(faces_points)
			writer.close()

	def writeVerticestoFile(self, filename):
		self.getSTLFeatures()
		np.savetxt(filename, np.array(self.all_vertices))
		print('List of Vertices saved to %s' %filename)

	def generateSTL(self, save_filename):
		f, v = self.getSTLFeatures()
		self.writeSTL(save_filename, f, v)

	def multiGenerateSTL(self, save_filename, add_objs):
		# takes multiple objects and generates a single STL
		# one of the objects is the object that it is being called from
		add_objs.extend([self])
		faces = []
		vertices = []
		for o in add_objs:
			f, v = o.getSTLFeatures()
			if len(faces) > 1:
				# if there is nothing in it, just add
				# else need to continue vertice counter from last value
				max_ind = np.max(faces) + 1
				f = f + max_ind
			faces.extend(f)
			vertices.extend(v)
		self.writeSTL(save_filename, faces, vertices)

class ObjectVis(GenVis): # intended for use with more complex shapes and with additional feature information -- for previous study
	def __init__(self, V):
		super(ObjectVis, self).__init__(V)
		self.loadObjectList()
		self.stl_path = base_path + "/models/stl_files/"
		
	def loadObjectList(self): # loads a list of objects from a document -- for a previous study
		import obj_dict
		self.objectGraspDict = obj_dict.grasp_obj_dict # (name, stl file name, y_rotate??)
		self.objectCentroidDict = obj_dict.obj_centroid_dict

	def loadObject(self, obj_num): # loads object that is in the list and moves centroid to origin -- for a previous study
		self.objCheck()
		self.obj_num = obj_num
		self.addObject()
		self.moveCentroid_to_Origin()
	
	def addObject(self): # adds an object that is in the list -- for previous study
		# self.objFN = self.stl_path + self.objectGraspDict[self.obj_num][1].replace('STL','dae')
		self.objFN = self.stl_path + self.objectGraspDict[self.obj_num][1]
		self.obj = self.env.ReadKinBodyXMLFile(self.objFN, {'scalegeometry':'0.001 0.001 0.001'})
		self.env.Add(self.obj, True)
		self.TClass = UtilTransforms
	
	def moveCentroid_to_Origin(self): # gets centroid from list and moves object to that location
		self.objCentroid = np.array(self.objectCentroidDict[self.obj_num]) / 1000  # some weird scaling factor
		self.obj.SetVisible(0) #hide object
		self.vis.drawPoints(([0,0,0])) #draw point at origin
		self.vis.drawPoints((self.objCentroid))
		self.obj.SetVisible(1) #show object
		self.adjustByCentroid()

	def adjustByCentroid(self): #moves object locally by centroid
		pose_new = self.GetCentroidTransform()
		self.globalTransformation(pose_new)

	def GetCentroidTransform(self): # create transform to locally move object by centroid
		pose = poseFromMatrix(self.obj.GetTransform())
		centroid_transform = poseTransformPoints(pose, -1*self.objCentroid.reshape(1,3)) #effectively a local translation by centroid!
		pose_new = np.hstack((pose[:4], centroid_transform.reshape(3,)))
		return pose_new

	def GetCurrentCentroid(self):
		pose = poseFromMatrix(self.obj.GetTransform())
		return self.vis.drawPoints(poseTransformPoints(pose, self.objCentroid.reshape(1,3))[-3:])

class ObjectGenericVis(ObjectVis):  # this object is for basic shapes -- near contact study
	def __init__(self, V):
		super(ObjectVis, self).__init__(V)
		curdir = os.path.dirname(os.path.realpath(__file__))
		self.stl_path = curdir +'/../ShapeGenerator/Shapes/'
		self.features = dict()

	def loadObject(self, objtype, h, w, e, a = None): # load object based on features -- for near contact study
		self.objCheck()
		self.h = int(h)
		self.w = int(w)
		self.e = int(w)

		if a is not None:
			self.a = int(a)
			self.objFN = self.stl_path + '%s_h%s_w%s_e%s_a%s.stl' %(objtype, int(h), int(w), int(e), int(a))
			if objtype == 'handle': #dimensions are much smaller on handle so had to add a 0 in front of dims
				self.objFN = self.stl_path + '%s_h%s_w0%s_e0%s_a0%s.stl' %(objtype, int(h), int(w), int(e), int(a))
				if int(w) > 9: #weirdness with filename -- need to find a better solution
					self.objFN = self.objFN.replace('w0','w')
				if int(a) > 9:
					self.objFN = self.objFN.replace('a0','a')
				if int(e) > 9:
					self.objFN = self.objFN.replace('e0','e')

		else:
			self.objFN = self.stl_path + '%s_h%s_w%s_e%s.stl' %(objtype, int(h), int(w), int(e))
		self.loadObjectFN(self.objFN)
		self.objType = objtype
		self.h = int(h)
		self.w = int(w)
		self.e = int(e)

	def loadObjectFN(self, FN): # load an object from file name
		self.objCheck()
		self.objFN = FN
		self.h, self.w, self.e, self.a = self.getFeaturesFromFN(FN)
		if os.path.isfile(self.objFN):
			self.obj = self.env.ReadKinBodyXMLFile(self.objFN)
			self.env.Add(self.obj,True)
			return True
		else:
			print("STL File Does not Exist! Parameters may be wrong.")
			print('Filename: %s' %self.objFN)
			return False

	def getFeaturesFromFN(self, FN):
		FN_processed = FN.split('/')[-1].strip('.stl') #removing path and extension
		h = FN_processed.split('_')[1].strip('h')
		h = self.decimalCheck(h)
		w = FN_processed.split('_')[2].strip('w')
		w = self.decimalCheck(w)
		e = FN_processed.split('_')[3].strip('e')
		e = self.decimalCheck(e)
		if 'a' in FN_processed:
			a = FN_processed.split('_')[4].strip('a')
			a = self.decimalCheck(a)
		else:
			a = None

		return h, w, e, a

	def decimalCheck(self, val_str): # check a parameter for D and convert to decimal
		#this is all necessary to try and keep file names readable
		if 'D' in val_str:
			val = float(val_str.replace('D', ''))/10
		else:
			val = float(val_str)
		return val

class HandVis(GenVis):
	def __init__(self, V):
		super(HandVis, self).__init__(V)
		self.stl_path = base_path + "/models/robots/"

	def loadHand(self): # load hand from file
		self.robotFN = self.stl_path + 'bhand.dae'
		self.obj = self.env.ReadRobotXMLFile(self.robotFN)
		self.env.Add(self.obj, True)
		self.changeColor(color = self.colors['grey'])
		self.obj.SetVisible(1)

	def setJointAngles(self, JA): # set hand joint angles
		#adjust fingertip values so we get behavior more similar to the actual hand
		JA[4] += -0.7853981
		JA[7] += -0.7853981
		JA[9] += -0.7853981
		self.obj.SetDOFValues(JA)
		''' Index in Joint Angle array: joint that it affects  |   value limit
		0: unknown
		1: unknown
		2: Finger1-Rotation		|	0 < l < pi
		3: Finger1-Base			|	0 < l < 2.44
		4: Finger1-Tip			|	0 < l < 0.837
		5: Finger2-Rotation		|	0 < l < pi
		6: Finger2-Base			|	0 < l < 2.44
		7: Finger2-Tip			|	0 < l < 0.837
		8: Finger3-Base			|	0 < l < 2.44
		9: Finger3-Tip			|	0 < l < 0.837
		'''

	def getJointAngles(self):
		# get the current joint angles
		return self.obj.GetDOFValues()

	def getPalmPoint(self, draw = False): # get the point that is in the center of the palm
		palm_pose = poseFromMatrix(self.obj.GetTransform())
		base_pt = numpy.array(palm_pose[4:])
		palm_pt = base_pt + self.getPalmOffset()
		if draw:
			self.vis.drawPoints(base_pt)
			self.vis.drawPoints(palm_pt)

		return palm_pt

	def getPalmOffset(self): # vector from base of hand to palm in global frame
		# Finds a vector from the base of the wrist to the middle of he palm by following
		# the apporach vector for the depth of the palm (7.5cm)
		palm_approach_rel = [0,0,1]
		palm_approach_global = poseTransformPoints(poseFromMatrix(self.obj.GetTransform()), [palm_approach_rel])[0]
		palm_approach_global = np.array(palm_approach_global)
		palm_approach_norm = palm_approach_global / np.linalg.norm(palm_approach_global)
		palm_approach_scaled = palm_approach_norm * 0.075
		return palm_approach_scaled

	def getPalmTransform(self): # I don't know what this is for?
		T = self.obj.getTransform()
		palm_approach_rel = [0,0,1]
		palm_approach_global = poseTransformPoints(poseFromMatrix(self.obj.GetTransform()), [palm_approach_rel])[0]

	def orientHandtoObj(self, T_H, T_O, Obj): # based on hand transform and object transform, can orient hand to object -- for previous study
		HandtoObject = np.dot(np.linalg.inv(T_O), T_H)
		self.obj.SetTransform(HandtoObject)
		self.localTranslation(-1 * Obj.objCentroid)
		return HandtoObject

	def localRotation(self, R): # apply a local rotation. translate to origin, rotate, translate back
		# pdb.set_trace()
		T = self.obj.GetTransform() # current transform
		palm_point = self.getPalmPoint() # get palm point in global frame
		P_origin = self.localTranslation(-palm_point) # move palm to origin
		T_origin = matrixFromPose(P_origin) # palm at origin without rotation
		T_origin_rot = np.dot(R, T_origin) # palm at origin with rotation
		self.obj.SetTransform(T_origin_rot) # apply rotation at origin
		T_rot = self.localTranslation(palm_point) # move back to original location
		return T_rot

	def ZSLERP(self, AA1, AA2, alpha, T_zero = None, move = True): #this is actually just a rotation that is meant to fake SLERP.
		# TODO: make this a real ZSLERP instead of this approximation
		# from AA1 to AA2
		AA_interp = AA1 * (1 - alpha) + AA2 * (alpha) #natural to think 10% interp is 10% away from start angle
		rot = matrixFromAxisAngle(AA_interp)
		if T_zero is None:
			T_zero = self.obj.GetTransform()
		T_new = np.dot(rot, T_zero)
		if move == True:
			self.obj.SetTransform(T_new)

		return T_new

	def retractFingers(self, Obj): # Uses a previous script to move the fingers into contact with object.  
		# Deals with small errors in recorded data to ensure no weiredness
		# like fingers going through objects
		# the script that does this shoudl be examined because it does not seem very effective
		contact_points, contact_links = retract_finger.retract_fingers(self.env, self.obj, Obj.obj)
		return contact_points, contact_links

	def addNoiseToGrasp(self, noise, percent=False):
		# add noise to the joint angles of the grasp
		# get random length array
		# ensure it is within bounds -- clamp if it is not
		# percent True means to add noise that is a percentage of the total travel range
		if percent:
			(lower, upper) = self.obj.GetDOFLimits()
			noise_JA = noise/100.0*(upper-lower)*np.random.randn(len(self.getJointAngles()))
		else:
			noise_JA = noise*np.random.randn(len(self.getJointAngles()))
		noisy_grasp = self.getJointAngles() + noise_JA
		noisy_grasp = self.limitJAToLimits(noisy_grasp)
		return noisy_grasp

	def limitJAToLimits(self, JA):
		(lower, upper) = self.obj.GetDOFLimits()
		JA_clamp = np.clip(JA, lower, upper)
		return JA_clamp

	def makeEqual(self, HandObj): # make this object have same shape and transform as another hand object
		self.obj.SetTransform(HandObj.obj.GetTransform())
		self.obj.SetDOFValues(HandObj.obj.GetDOFValues())

	def closeFingersToContact(self):
		# TODO: add a check for when the joint limits have been reached
		# keep closing the fingers until contact occurs with the object
		# NO dynamic simulation of object (caused by contact or gravity)
		# i have not tried it with a small object that is only touched by medial objects
		JA_d = 1e-3
		start_JA = self.getJointAngles()
		current_JA = copy.deepcopy(start_JA)
		contact_flag = False
		finger_count = 3
		med_JA_idx = [3, 6, 8]
		dist_JA_idx = [4, 7, 9]
		iter_count = 0
		while not contact_flag:
			JA_add = np.zeros(10)
			contacts = self.getContact(verbose=False)
			contact_medial_flag = [False] * finger_count
			contact_distal_flag = [False] * finger_count
			if len(contacts) > 0:
				# something in contact
				# check for medial and distal for each finger
				# set parts that are in contact to True
				for k,v in contacts.iteritems():
					for l,d in (('dist',contact_distal_flag), ('med',contact_medial_flag)):
						if l in k:
							for i in range(finger_count):
								if str(i+1) in k:
									d[i] = True

			for fing in range(finger_count):
				# if the distal link is in contact
				# then stop moving the medial
				if contact_distal_flag[fing]:
					contact_medial_flag[fing] = contact_distal_flag[fing]

				# if medial link is not in contact and distal link is not in contact
				# then move medial only
				elif not contact_medial_flag[fing] and not contact_distal_flag[fing]:
					contact_medial_flag[fing] = False
					contact_distal_flag[fing] = True

				# if poximal link is in contact and distal link is not in contact
				# then move distal only
				# -- this should already be taken care of by contact
				elif contact_medial_flag[fing] and not contact_distal_flag[fing]:
					contact_distal_flag[fing] = False

			# add to medial joints based on which ones are not in contact
			for cf, idx in zip(contact_medial_flag, med_JA_idx):
				if not cf:
					JA_add[idx] = 1
			for cf, idx in zip(contact_distal_flag, dist_JA_idx):
				if not cf:
					JA_add[idx] = 1
			JA_add *= JA_d

			if all(JA_add == 0):
				# stop closing fingers if nothing is moving
				contact_flag = True
				continue
			current_JA = current_JA + JA_add
			self.setJointAngles(self.limitJAToLimits(current_JA))
			iter_count += 1
			if iter_count > 2e3: # crude solution to understanding when JA limits exceeded
				print('No Solution found')
				break
		return self.getJointAngles()

	def moveInPalmNormalDirection(self, vec):
		# given a movement vector, it will return a transformation matrix to move it in that direction
		T = self.getGlobalTransformation()
		T[:3, 3] += vec
		return T

	def moveToMakeValidGrasp(self, body=None):
		# from the current configuration
		# 1) move the palm out of contact with the object by moving along palm normal
		# 2) move the fingers out of contact by opening medial and distal links
		
		step_d = -0.01 # I don't know how to determine if it is in the correct direction
		finger_count = 3
		med_JA_idx = [3, 6, 8]
		dist_JA_idx = [4, 7, 9]
		start_JA = self.getJointAngles()
		current_JA = copy.deepcopy(start_JA)
		palm_normal_dir = self.getPalmOffset()
		# palm in contact
		contacts = self.getContact(verbose=False, body=body)
		palm_contact = any(['palm' in k for k in contacts.keys()])
		while palm_contact: #may want to add distal links to this set? or create a seperate section for distal
			# move in normal direction by step_d
			handT_new = self.moveInPalmNormalDirection(palm_normal_dir * step_d)
			self.globalTransformation(handT_new)
			contacts = self.getContact(verbose=False, body=body)
			palm_contact = any(['palm' in k for k in contacts.keys()])
				
		# open fingers until medial not in contact		
		contacts = self.getContact(verbose=False, body=body)
		medial_contact = any(['med' in k for k in contacts.keys()])
		while medial_contact:
			JA_add = np.zeros(10)
			contact_medial_flag = [False] * finger_count # assume they are not in contact
			# check if the medial sections are in contact
			for i in range(finger_count):
				for k,v in contacts.iteritems():
					for l,d in [('med',contact_medial_flag)]:
						if l in k:
							for i in range(finger_count):
								if str(i+1) in k:
									d[i] = True
			
			# move medial sections based on contact -- could move distal sections are ratio here
			for i in range(finger_count):
				if contact_medial_flag[i]:
					JA_add[med_JA_idx[i]] += step_d
			current_JA = current_JA + JA_add
			# check JA to make sure limit is not reached
			if any(self.limitJAToLimits(current_JA)[med_JA_idx] != current_JA[med_JA_idx]):
				print('Cannot move medial joints to non contact location')
				break
			self.setJointAngles(self.limitJAToLimits(current_JA))

			# check contact status
			contacts = self.getContact(verbose=False, body=body)
			medial_contact = any(['med' in k for k in contacts.keys()])

		# open fingers until distal not in contact		
		contacts = self.getContact(verbose=False, body=body)
		distal_contact = any(['dist' in k for k in contacts.keys()])
		while distal_contact:
			JA_add = np.zeros(10)
			contact_distal_flag = [False] * finger_count
			# check if the distal sections are in contact
			for i in range(finger_count):
				for k,v in contacts.iteritems():
					for l,d in [('dist',contact_distal_flag)]:
						if l in k:
							for i in range(finger_count):
								if str(i+1) in k:
									d[i] = True
			# move distal sections based on contact
			for i in range(finger_count):
				if contact_distal_flag[i]:
					JA_add[dist_JA_idx[i]] += step_d
			current_JA = current_JA + JA_add
			# check JA to make sure limit is not reached
			## the much more complicated version ##
			# dist_move_idx = JA_add[dist_JA_idx] != 0
			# if any((self.limitJAToLimits(current_JA)[dist_JA_idx] != current_JA[dist_JA_idx]) + dist_move_idx):
			## 
			if any(self.limitJAToLimits(current_JA)[dist_JA_idx] != current_JA[dist_JA_idx]):
				print('Cannot move distal joints to non contact location')
				break
			self.setJointAngles(self.limitJAToLimits(current_JA))

			# check contact status
			contacts = self.getContact(verbose=False)
			distal_contact = any(['dist' in k for k in contacts.keys()])


		# last step is to close the fingers to contact
		self.closeFingersToContact()
	
	def getContact(self, body=None, verbose=True):
		self.env.GetCollisionChecker().SetCollisionOptions(CollisionOptions.Contacts)
		report = CollisionReport()
		contact = {}
		for link in self.obj.GetLinks():
			if body == None:
				collision = self.env.CheckCollision(link, report=report)
			else:
				collision = self.env.CheckCollision(link, body, report=report)
			if len(report.contacts) > 0:
				if verbose: print 'link %s %d contacts'%(link.GetName(),len(report.contacts))
				contact[link.GetName()] = report.contacts
		return contact

	# Kadon Engle - last edited 07/14/17
	def getContactPoints(self, body=None): # Gets the contact points for the links of the fingers if they are in contact with something in the environment
		self.env.GetCollisionChecker().SetCollisionOptions(CollisionOptions.Contacts)
		report = CollisionReport()
		positions = []
		for link in self.obj.GetLinks():
			if body == None:
				collision = self.env.CheckCollision(link.GetName(), len(report.contacts))
			else:
				collision = self.env.CheckCollision(link, body,report=report)
			if len(report.contacts) > 0:
				print 'link %s %d contacts'%(link.GetName(),len(report.contacts))
				positions += [c.pos for c in report.contacts]
		return positions


# Kadon Engle - last edited 07/06/17
class AddGroundPlane(object): #General class for adding a ground plane into the environment.
		def __init__(self, V):
			self.vis = V
			self.groundPlane = None
			self.colors = dict()
			self.colors = ColorsDict.colors

		def changeColor(self, color = None, alpha = None): # change color of object.  Sets all sub features to same color
			# pdb.set_trace()
			if type(color) is str: #loads from dictionary
				color = self.colors[color]
			for link in self.groundPlane.GetLinks():
				for geos in link.GetGeometries():
					geos.SetDiffuseColor(color)

		def createGroundPlane(self, y_height, x = 0.5, y = 0, z = 0.5, x_pos = 0, z_pos = 0): #Removes any existing ground plane (if any), then creates a ground plane.
			with self.vis.env:
				self.removeGroundPlane()
				self.groundPlane = RaveCreateKinBody(self.vis.env, '')
				self.groundPlane.SetName('groundPlane')
				self.groundPlane.InitFromBoxes(np.array([[x_pos,y_height,z_pos, x, y, z]]),True) # set geometry as one box
				T = np.eye(4)
				T[:3,3] = [x_pos, y_height, z_pos]
				self.groundPlane.SetTransform(T)
				self.vis.env.AddKinBody(self.groundPlane)
				self.groundPlane.GetLinks()[0].GetGeometries()[0].SetDiffuseColor([0,0,0])
				self.groundPlane.GetLinks()[0].GetGeometries()[0].SetAmbientColor([3,3,3])

		def removeGroundPlane(self): #Cycles through Bodies in the environment. If 'groundPlane' exists, remove it.
			for i in self.vis.env.GetBodies():
				if i.GetName() == 'groundPlane':
					self.vis.env.Remove(i)

# Ammar Kothari - last edited 07/10/17
class ArmVis(GenVis): # general class for importing arm into an openrave scene
	# it would be nice to reuse the functions from Hand here

	# can't use changeColor -- links do not have geometries
	def __init__(self, V):
		super(ArmVis, self).__init__(V)
		self.stl_path = base_path + "/models/robots/"
		self.base_offset = np.array([[-0.06,  1.  ,  0.  ,  0.  ],
									[-1.  , -0.06, -0.  , -0.  ],
									[-0.  , -0.  ,  1.  , -1.  ],
									[ 0.  ,  0.  ,  0.  ,  1.  ]])

	def loadArm(self): # load arm from file
		self.robotFN = self.stl_path + 'barrett_wam.dae'
		self.obj = self.env.ReadRobotXMLFile(self.robotFN)
		self.obj = self.vis.env.ReadRobotXMLFile(self.robotFN)
		self.env.Add(self.obj, True)
		self.obj.SetVisible(1)
		self.globalTransformation(self.base_offset)

	def getJointAngles(self):
		return self.obj.GetDOFValues()

	def setJointAngles(self, jointAngles):
		if len(jointAngles) != 17:
			print('Input array should be 1x17')
			return
		'''
		Index in Joint Angle array: joint that it affects  |   value limit
		0 : J1						|-2.6 < l < 2.6
		1 : J2						|-1.98< l < 1.98
		2 : J3						|-2.8 < l < 2.8
		3 : J4						|-0.9 < l < 3.14
		4 : J5						|-4.55< l < 1.25
		5 : J6						|-1.57< l < 1.57
		6 : J7						|  -3 < l < 3
		7 : Unknown
		8 : Unknown
		10: Finger1-Rotation		|	0 < l < pi
		11: Finger1-Base			|	0 < l < 2.44
		12: Finger1-Tip				|	0 < l < 0.837
		13: Finger2-Rotation		|	0 < l < pi
		14: Finger2-Base			|	0 < l < 2.44
		15: Finger2-Tip				|	0 < l < 0.837
		16: Finger3-Base			|	0 < l < 2.44
		17: Finger3-Tip				|	0 < l < 0.837
		'''
		# adjusting the joint angles due to an issue with the model mapping
		jointAngles[11] += -0.7853981
		jointAngles[14] += -0.7853981
		jointAngles[16] += -0.7853981
		self.obj.SetActiveDOFValues(jointAngles)

	def testJointIndicies(self):
		#cycles through joint indices to help identify which numbers correspond to which joint
		pdb.set_trace()
		JA_start = self.getJointAngles()
		JA = np.zeros(self.obj.GetActiveDOF())
		minval, maxval = self.obj.GetDOFLimits()
		for i in range(self.obj.GetActiveDOF()):
			print("Changing Joint %s -- %s" %(i, JOINT_ANGLES_NAMES[i]))
			for theta in np.linspace(minval[i], maxval[i], 10):
				JA[i] = theta
				self.setJointAngles(JA)
				time.sleep(0.2)
			JA[i] = 0
		self.setJointAngles(JA_start)

	def markZeroForAllLinks(self):
		# plots a point at the "zero" for each link
		all_transforms = self.obj.GetLinkTransformations()
		for link in self.obj.GetLinks():
			link_pt = link.GetTransform()[:3,3]
			self.vis.drawPoints(link_pt)

	def convertRobot2OpenRAVE(self, JA_robot):
		# converts the angles output by the robot to the right length for OpenRAVE
		# rearrange and insert some zeros so that it aligns with openrave system
		# idx 7,8 are unknown and 9,12 should be the same because they are rotation of the fingers around base
		# for the hand, robot outputs all the proximal links, spread, all distal links
		JA_openrave = np.concatenate((JA_robot[0:7], [0,0], JA_robot[[10, 7, 11, 10, 8, 12, 9, 13]]), 0)
		return JA_openrave

	def getEETransform(self):
		# get transformation of hand (so that I can align just a hand with it)
		return self.obj.GetLinks()[9].GetTransform()

	#can all STL functions go into GenVis?
	def getSTLFeatures(self):
		links = self.obj.GetLinks()
		all_vertices = []
		all_faces = []
		ind = 0
		# I don't know what is happening here
		for link in links:
			vertices = link.GetCollisionData().vertices
			faces = link.GetCollisionData().indices
			if ind == 0:
				faces = np.add(faces,ind)
			else:
				faces = np.add(faces,ind+1)
			try:
				ind = faces[-1][-1]
			except:
				pass
		
			#print "link: ", link, "\nStarting index for this link: ", len(all_vertices)
			link_pose = poseFromMatrix(link.GetTransform())
			transform_vertices = poseTransformPoints(link_pose, vertices)
			all_vertices.extend(transform_vertices.tolist())
			all_faces.extend(faces.tolist())
		self.all_faces = all_faces
		self.all_vertices = all_vertices

	def writeSTL(self, save_filename):
		faces_points = []
		for vec in self.all_faces:
			faces_points.append([self.all_vertices[vec[0]],self.all_vertices[vec[1]],self.all_vertices[vec[2]]])

		with open(save_filename,'wb') as fp:
			writer = Binary_STL_Writer(fp)
			writer.add_faces(faces_points)
			writer.close()

	def writeVerticestoFile(self, filename):
		self.getSTLFeatures()
		np.savetxt(filename, np.array(self.all_vertices))
		print('List of Vertices saved to %s' %filename)

	def generateSTL(self, save_filename):
		self.getSTLFeatures()
		self.writeSTL(save_filename)

class ArmVis_OR(ArmVis): # uses the openrave model of the arm which is more like the real robot
	# it also is set up to work with things like IK
	def __init__(self, V):
		super(ArmVis, self).__init__(V)
		self.stl_path = base_path + "/models/robots/"
		self.other_robots = []
		self.base_offset = np.array([[-0.066,  0.998,  0.   , -0.124],
									[-0.998, -0.066, -0.   ,  0.233],
									[-0.   , -0.   ,  1.   ,  0.009],
									[ 0.   ,  0.   ,  0.   ,  1.   ]])


	def loadArm(self): # load arm from file
		self.robotFN = '/home/ammar/git/openrave/src/robots/barrettwam.robot.xml'
		self.obj = self.env.ReadRobotXMLFile(self.robotFN)
		self.obj = self.vis.env.ReadRobotXMLFile(self.robotFN)
		self.env.Add(self.obj, True)
		self.obj.SetVisible(1)
		self.obj.SetTransform(self.base_offset)

	def loadIK(self):
		#loads the ik plugin
		self.ikmodel = databases.inversekinematics.InverseKinematicsModel(self.obj, iktype=IkParameterization.Type.Transform6D)
		if not self.ikmodel.load():
			self.ikmodel.autogenerate()

	def randomCollisionFreeConfig(self):
		lower,upper = [v[self.ikmodel.manip.GetArmIndices()] for v in self.ikmodel.robot.GetDOFLimits()]
		self.obj.SetDOFValues(np.random.rand()*(upper-lower)+lower,self.ikmodel.manip.GetArmIndices()) # set random values
		if self.obj.CheckSelfCollision():
			print('Collision!')
			time.sleep(1)
			self.randomCollisionFreeConfig()

	def IKSolutions(self):
		#computes all the solutions for the current configuration
		solutions = self.ikmodel.manip.FindIKSolutions(self.ikmodel.manip.GetTransform(),True)
		# openravepy.IkFilterOptions.IgnoreJointLimits +  openravepy.IkFilterOptions.CheckEnvCollisions
		return solutions

	def dispIKSolutions(self, sols):
		# displays them as transparent arms
		transparency = 0.8
		for sol in sols:
			newrobot = RaveCreateRobot(self.vis.env,self.obj.GetXMLId())
			newrobot.Clone(self.obj,0)
			for link in newrobot.GetLinks():
				for geom in link.GetGeometries():
					geom.SetTransparency(transparency)
			self.vis.env.Add(newrobot,True)
			newrobot.SetTransform(self.obj.GetTransform())
			newrobot.SetDOFValues(sol,self.ikmodel.manip.GetArmIndices())
			self.other_robots.append(newrobot)

	def removeAllIKSolutions(self):
		# START HERE: DELETE ROBOTS!
		for robot in self.other_robots:
			pdb.set_trace()

	def setJointAngles(self, jointAngles):
		if len(jointAngles) == 7:
			# only arm joints given
			hand_JA = self.obj.GetDOFValues()[7:]
			JA = np.append(jointAngles, hand_JA)
		elif len(jointAngles) == 11:
			# arm an hand joints given
			JA = jointAngles
		else:
			print('Input array should be 1x7 or 1x11')
			return
		'''
		Index in Joint Angle array: joint that it affects  |   value limit
		0 : J1						|-2.60 < l < 2.6
		1 : J2						|-1.98 < l < 1.97
		2 : J3						|-2.70 < l < 2.74
		3 : J4						|-0.85 < l < 3.14
		4 : J5						|-4.75 < l < 1.30
		5 : J6						|-1.57 < l < 1.57
		6 : J7						|-3.00 < l < 3.00
		7 : ?						| 0.00 < l < 2.44
		8 : ?						| 0.00 < l < 2.44
		9 : ?						| 0.00 < l < 2.44
		10: ?						|-0.01 < l < 3.15
		'''
		self.obj.SetActiveDOFValues(JA)

	def limitArmJAToLimits(self, JA):
		(lower, upper) = self.obj.GetDOFLimits()
		JA_clamp = np.clip(JA, lower[0:7], upper[0:7])
		return JA_clamp

	def limitHandJAToLimits(self, JA):
		(lower, upper) = self.obj.GetDOFLimits()
		JA_clamp = np.clip(JA, lower[7:], upper[7:])
		return JA_clamp

	def IK(self, goalT):
		# RotX = UtilTransforms.RotX(np.pi/2)
		# RotY = UtilTransforms.RotY(np.pi/2)
		RotZ = UtilTransforms.RotZ(-np.pi/2) # cosys misalignment
		T_updated = np.matmul(goalT, np.matmul(self.obj.GetManipulators()[0].GetLocalToolTransform(), RotZ))
		JA, _ = self.IKwithMinJA(T_updated)
		return JA

	def getIK(self, goalT, bitmask=0):
		# returns all IK solutions
		# need to figure out some parameter here to understand how to get certain solutions
		return self.ikmodel.manip.FindIKSolutions(goalT, bitmask)

	def IKwithMinJA(self, goalT):
		# returns the IK solution that is closest to the 0 configuration
		sols = self.getIK(goalT)
		dist_from_zeros = np.linalg.norm(sols, axis = 1)
		idx = np.argmin(dist_from_zeros)
		return sols[idx], dist_from_zeros[idx]

	def thetaTrajectory(self, goalJA, startJA=None, step_size=0.01):
		# trajectory on the robot for using with ros (based on WamPy)
		if startJA == None:
			startJA = np.zeros(len(goalJA))
		DOFs = len(startJA)
		max_dist = np.max(np.abs(goalJA-startJA))
		steps = np.ceil(max_dist/step_size)
		traj = np.array([np.linspace(startJA[i], goalJA[i], steps) for i in range(DOFs)]).T
		if len(traj) == 0:
			traj = np.zeros((1,len(goalJA)))
		else:
			traj_vel = np.gradient(traj, axis=1)
			traj_acc = np.gradient(traj_vel, axis=1)
		return traj

	def sequentialCombineArmandHandTraj(self, armTraj, handTraj):
		# first all the arm movement
		# then all the hand movement
		comb_traj = []
		for a_t in armTraj:
			comb_traj.append(np.hstack((a_t, handTraj[0])))
		for h_t in handTraj:
			comb_traj.append(np.hstack((armTraj[-1], h_t)))
		comb_traj = np.array(comb_traj)
		return comb_traj

	def viewThetaTrajectory(self, traj, dt=0.01):
		for step in traj:
			self.setJointAngles(step)
			time.sleep(dt)

	def generateOperationalSpaceStraightLineTrajectory(self, goalT, startT=poseFromMatrix(np.eye(4))):
		pdb.set_trace()
		self.traj = RaveCreateTrajectory(self.env,'')
		spec = IkParameterization.GetConfigurationSpecificationFromType(IkParameterizationType.Transform6D,'linear')
		self.traj.Init(spec)
		self.traj.Insert(self.traj.GetNumWaypoints(), startT)
		self.traj.Insert(self.traj.GetNumWaypoints(), goalT)

		# set trajectory limits
		planningutils.RetimeAffineTrajectory(self.traj,maxvelocities=np.ones(7),maxaccelerations=5*np.ones(7))

		# creating planner
		planner = RaveCreatePlanner(self.env,'workspacetrajectorytracker')
		params = Planner.PlannerParameters()
		params.SetRobotActiveJoints(self.obj)
		params.SetExtraParameters('<workspacetrajectory>%s</workspacetrajectory>'%self.traj.serialize(0))
		planner.InitPlan(self.obj,params)
		
		outputtraj = RaveCreateTrajectory(self.env,'')

		# execute trajectory
		self.obj.GetController().SetPath(outputtraj)
		# wait for trajectory to finish
		self.obj.WaitForController(0)

'''
from NearContactStudy import Vis, ArmVis_OR
V = Vis(); A = ArmVis_OR(V);
A.loadArm()
A.loadIK()
A.randomCollisionFreeConfig()
sols = A.IKSolutions()
A.dispIKSolutions(sols[:10])
'''


		
if __name__ == '__main__': #For testing classes (put code below and run in terminal)
	V = Vis()
	# H = HandVis(V)
	# H.loadHand()
	# O = ObjectGenericVis(V)
	# O.loadObject('cube', 3, 3, 3)
	A = ArmVis(V)
	A.loadArm()
	# O = ObjectVis(V)
	# O.loadObjectList()
	# O.loadObject(2)

	# A.writeVerticestoFile('test_vertices')

	# G = AddGroundPlane(V)
	# G.createGroundPlane(0)
	# Gr = AddGroundPlane(V)
	# Gr.createGroundPlane(0)

	#A = ArmVis(V)
	#A.loadArm()
	#A.generateSTL('test1.stl')
	# for i in range(10):
	# 	JA = np.zeros(17)
	# 	JA[0:7] = np.random.rand(7) * 2 - 1
	# 	A.setJointAngles(JA)
	# 	raw_input('Continue?')
	pdb.set_trace()
	from openravepy import interfaces
	basemanip = interfaces.BaseManipulation(A.obj)

	T = np.array([[np.cos(0.1), np.sin(0.1), 0, 0.1], [np.sin(0.1), np.cos(0.1), 0, 0.1], [0, 0, 0, 0], [0, 0, 0, 1]])
	basemanip.MoveToHandPosition(matrices = [T], execute = False, outputtrajobj = True)



