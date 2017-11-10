from openravepy import *
from Colors import ColorsDict, bcolors
import numpy as np
import sys, os, pdb, copy, subprocess, time
from Colors import ColorsDict, bcolors
from stlwriter import Binary_STL_Writer
import platform
print "\n\n" + platform.node() + "\n\n"
if platform.node()[0:3] == 'reu': #lab computer
	base_path = os.path.dirname(os.path.realpath(__file__))
elif platform.node() == 'Sonny': #lab computer
	base_path = rospkg.RosPack().get_path('valid_grasp_generator')
	import retract_finger
elif platform.node() == 'Desktop': #personal desktop Linux
	base_path = os.path.dirname(os.path.realpath(__file__))
	retract_fingers_path = os.path.expanduser('~/catkin_ws/src/valid_grasp_generator/src')
	sys.path.append(retract_fingers_path)
	import retract_finger
else:
	base_path = os.path.dirname(os.path.realpath(__file__))

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

	def globalMove(self,T): # apply global Translation to object
		T_new = self.TClass.TL2T(T)
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
		T = self.TClass.CombineRotationTranslation(RotationMatrix, Translation)
		pdb.set_trace()
		T = self.TClass.AddTranslation(self.objCentroid, T) #what is this doing?
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
		self.TClass = Transforms(self.obj)
	
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
		self.TClass = Transforms(self.obj)

	def setJointAngles(self, JA): # set hand joint angles
		#adjust fingertip values so we get behavior more similar to the actual hand
		# JA[4] += -0.7853981
		# JA[7] += -0.7853981
		# JA[9] += -0.7853981
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

	def addNoiseToGrasp(self, Obj, T_zero = None, Contact_JA = None, TL_n = 0.01, R_n = 0.1, JA_n = 0.1): # adds white noise to position, rotation, and location of grasp
		# searches for grasp that has all three fingers in contact with object, otherwise grasp can be odd
		in_contact = [False, False]
		if Contact_JA is None:
			Contact_JA = self.obj.GetDOFValues()
		if T_zero is None:
			T_zero = self.obj.GetTransform()
		while not all(in_contact):
			self.setJointAngles(Contact_JA)
			# some type of noise operation.  probably more noise in orientation, ane less in position
			noise_T = np.eye(4)
			noise_T[:3,:3] = np.random.normal(loc = 0, scale = R_n, size = (3,3))
			noise_T[:3,3] = np.random.normal(loc = 0, scale = TL_n, size = (3))
			T_noise = T_zero + noise_T
			noise_JA = np.random.normal(loc = 0, scale = JA_n, size = Contact_JA.shape)
			JA_noise = Contact_JA + noise_JA
			# move fingers into noise position and adjust fingers for valid grasp
			self.setJointAngles(JA_noise)
			self.obj.SetTransform(T_noise)
			contact_points2, contact_links2 = self.retractFingers(Obj)
			# check to make sure all fingers are in contact. not perfect, but makes certain a good grasp
			in_contact = [any([True if link in x else False for x in contact_links2]) for link in ['finger_1', 'finger_2', 'finger_3']]
			# in_contact = [any([True if link in x else False for x in contact_links2]) for link in contact_links1]
		return T_noise, JA_noise

	def makeEqual(self, HandObj): # make this object have same shape and transform as another hand object
		self.obj.SetTransform(HandObj.obj.GetTransform())
		self.obj.SetDOFValues(HandObj.obj.GetDOFValues())
	
	def getContact(self, body=None):
		self.env.GetCollisionChecker().SetCollisionOptions(CollisionOptions.Contacts)
		report = CollisionReport()
		contact = {}
		for link in self.obj.GetLinks():
			if body == None:
				collision = self.env.CheckCollision(link, report=report)
			else:
				collision = self.env.CheckCollision(link, body, report=report)
			if len(report.contacts) > 0:
				print 'link %s %d contacts'%(link.GetName(),len(report.contacts))
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

		def createGroundPlane(self, y_height, x = 0.5, y = 0, z = 0.5): #Removes any existing ground plane (if any), then creates a ground plane.
			with self.vis.env:
				self.removeGroundPlane()
				self.groundPlane = RaveCreateKinBody(self.vis.env, '')
				self.groundPlane.SetName('groundPlane')
				self.groundPlane.InitFromBoxes(np.array([[0,y_height,0, x, y, z]]),True) # set geometry as one box
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

	def loadArm(self): # load arm from file
		self.robotFN = self.stl_path + 'barrett_wam.dae'
		self.obj = self.env.ReadRobotXMLFile(self.robotFN)
		# self.robotFN = '/home/ammar/Documents/SourceSoftware/openrave/src/robots/barrettwam.robot.xml'
		self.obj = self.vis.env.ReadRobotXMLFile(self.robotFN)
		self.env.Add(self.obj, True)
		self.obj.SetVisible(1)
		self.TClass = Transforms(self.obj)

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
		self.obj.SetDOFValues(jointAngles)

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

	def generateSTL(self, save_filename):
		self.getSTLFeatures()
		self.writeSTL(save_filename)



class Transforms(object): #class for holding all transform operations -- this may be useless!
	def __init__(self, link):
		self.i = 1
		self.link = link

	# Description: Translation to Transformation
	def TL2T(self, Tl):
		Tl = np.array(Tl)
		T_pose = np.hstack((np.array([1,0,0,0]), Tl)) # zero rotation quaternion
		T_new = matrixFromPose(T_pose)
		return T_new

	def R2T(self, R):
		T = np.eye(4)
		T[:3,:3] = R
		return T

	def AddTranslation(self,Tl, T):
		if len(Tl) == 3:
			T[:3,3] += Tl[:]
		else: # if it is a transformation matrix
			T[:3,3] += Tl[:3,3]
		return T


	def CombineRotationTranslation(self, R, Tl):
		T = np.eye(4)
		T = self.R2T(R)
		T = self.AddTranslation(Tl, T)
		return T

		
		
if __name__ == '__main__': #For testing classes (put code below and run in terminal)
	V = Vis()
	H = HandVis(V)
	O = ObjectGenericVis(V)
	H.loadHand()
	O.loadObject('cube', 3, 3, 3)
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

