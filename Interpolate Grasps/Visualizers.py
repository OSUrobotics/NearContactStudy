from openravepy import *
from Colors import ColorsDict, bcolors
import numpy as np
import sys, os, pdb, copy, subprocess


import platform
if platform.node() == 'Sonny': #lab computer
	base_path = rospkg.RosPack().get_path('valid_grasp_generator')
	import retract_finger
elif platform.node() == 'Desktop': #personal desktop Linux
	base_path = os.path.dirname(os.path.realpath(__file__))
	retract_fingers_path = os.path.expanduser('~/catkin_ws/src/valid_grasp_generator/src')
	sys.path.append(retract_fingers_path)
	import retract_finger

else: # personal desktop Windows
	base_path = 'C:\Users\KothariAmmar\Documents\Grasping Lab\Interpolate Grasps\\'


class Vis(object): #General Class for visualization
	def __init__(self):
		self.env = Environment()
		self.env.SetViewer('qtcoin')
		self.viewer = self.env.GetViewer()
		self.colors = dict()
		self.colors = ColorsDict.colors
		self.points = list()
		# an arbitrary camera Angle that I picked
		self.cameraTransform = np.array([[-0.46492937, -0.50410198,  0.72781995, -0.32667211],
   										[-0.10644389, -0.78428209, -0.6112048 ,  0.29396212],
       									[ 0.8789257 , -0.36163905,  0.3109772 , -0.17278717],
       									[ 0.        ,  0.        ,  0.        ,  1.        ]])
		self.viewer.SetCamera(self.cameraTransform)

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

	def takeImage(self, fname): # Take an image of the OpenRave window
		Viewer = self.env.GetViewer()
		try: #there is a bug in my version of Linux.  This should work with the proper drivers setup
			Im = Viewer.GetCameraImage(640,480,  Viewer.GetCameraTransform(),[640,640,320,240])
			plt.imshow(Im)
		except: #this is more robust, but requires that particular window to be selected
			subprocess.call(["gnome-screenshot", "-w", "-B", "--file="+fname, '--delay=1'])

	def setCamera(self, dist, az, el): # Description: Sets camera location pointed at center at a distance, azimuth, and elevation
		#Thsi can be re-written to be more efficient (unneeded operations)
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
		rot_az = np.dot(rot_mat_az, rot_el)
		rot_new = rot_az
		self.viewer.SetCamera(rot_new)
		# pdb.set_trace()

		return rot_new

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
		self.objExists(), self.QCheck()
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
		if color is None: # random color
			color = np.random.rand(3)
		if alpha is None: # keep transparency the same
			alpha = self.obj.GetLinks()[0].GetGeometries()[0].GetTransparency()
		elif alpha is not None and color is None: #only want to change transparency but keep color the same
			color = self.obj.GetLinks()[0].GetGeometries()[0].GetDiffuseColor()
		if type(color) is str: #loads from dictionary
			color = self.colors[color]
		for link in self.obj.GetLinks():
			for geos in link.GetGeometries():
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
        


class ObjectVis(GenVis):
	def __init__(self, V):
		super(ObjectVis, self).__init__(V)
		self.loadObjectList()
		self.stl_path = base_path + "/models/stl_files/"
		
	def loadObjectList(self):
		import obj_dict
		self.objectGraspDict = obj_dict.grasp_obj_dict # (name, stl file name, y_rotate??)
		self.objectCentroidDict = obj_dict.obj_centroid_dict

	def loadObject(self, obj_num):
		self.objCheck()
		self.obj_num = obj_num
		self.addObject()
		self.moveCentroid_to_Origin()
	
	def addObject(self):
		# self.objFN = self.stl_path + self.objectGraspDict[self.obj_num][1].replace('STL','dae')
		self.objFN = self.stl_path + self.objectGraspDict[self.obj_num][1]
		self.obj = self.env.ReadKinBodyXMLFile(self.objFN, {'scalegeometry':'0.001 0.001 0.001'})
		self.env.Add(self.obj, True)
		self.TClass = Transforms(self.obj)
	
	def moveCentroid_to_Origin(self):
		self.objCentroid = np.array(self.objectCentroidDict[self.obj_num]) / 1000  # some weird scaling factor
		self.obj.SetVisible(0) #hide object
		self.vis.drawPoints(([0,0,0])) #draw point at origin
		self.vis.drawPoints((self.objCentroid))
		self.obj.SetVisible(1) #show object
		self.adjustByCentroid()

	def adjustByCentroid(self):
		pose_new = self.GetCentroidTransform()
		self.globalTransformation(pose_new)

	def GetCentroidTransform(self):
		pose = poseFromMatrix(self.obj.GetTransform())
		centroid_transform = poseTransformPoints(pose, -1*self.objCentroid.reshape(1,3)) #effectively a local translation by centroid!
		pose_new = np.hstack((pose[:4], centroid_transform.reshape(3,)))
		return pose_new

class ObjectGenericVis(ObjectVis):
	def __init__(self, V):
		super(ObjectVis, self).__init__(V)
		curdir = os.path.dirname(os.path.realpath(__file__))
		self.stl_path = curdir +'/../ShapeGenerator/Shapes/'
		self.features = dict()

	def loadObject(self, objtype, h, w, e, a = None):
		self.objCheck()
		if a is not None:
			self.objFN = self.stl_path + '%s_h%s_w%s_e%s_a%s.stl' %(objtype, int(h), int(w), int(e), int(a))
		else:
			self.objFN = self.stl_path + '%s_h%s_w%s_e%s.stl' %(objtype, int(h), int(w), int(e))
		if os.path.isfile(self.objFN):
			self.obj = self.env.ReadKinBodyXMLFile(self.objFN)
			self.env.Add(self.obj,True)
			return True
		else:
			print("STL File Does not Exist! Parameters may be wrong.")
			return False





class HandVis(GenVis):
	def __init__(self, V):
		super(HandVis, self).__init__(V)
		self.stl_path = base_path + "/models/robots/"

	def loadHand(self):
		self.robotFN = self.stl_path + 'bhand.dae'
		self.obj = self.env.ReadRobotXMLFile(self.robotFN)
		self.env.Add(self.obj, True)
		self.changeColor(color = self.colors['grey'])
		self.obj.SetVisible(1)
		self.TClass = Transforms(self.obj)

	def setJointAngles(self, JA):
		self.obj.SetDOFValues(JA)

	def getPalmPoint(self):
		palm_pose = poseFromMatrix(self.obj.GetTransform())
		base_pt = numpy.array(palm_pose[4:])
		palm_pt = base_pt + self.getPalmOffset()
		self.vis.drawPoints(base_pt)
		self.vis.drawPoints(palm_pt)

		return palm_pt

		# Finds a vector from the base of the wrist to the middle of he palm by following
		#	the apporach vector for the depth of the palm (7.5cm)
	def getPalmOffset(self):
		palm_approach_rel = [0,0,1]
		palm_approach_global = poseTransformPoints(poseFromMatrix(self.obj.GetTransform()), [palm_approach_rel])[0]
		palm_approach_global = np.array(palm_approach_global)
		palm_approach_norm = palm_approach_global / np.linalg.norm(palm_approach_global)
		palm_approach_scaled = palm_approach_norm * 0.075
		return palm_approach_scaled

	def getPalmTransform(self):
		T = self.obj.getTransform()
		palm_approach_rel = [0,0,1]
		palm_approach_global = poseTransformPoints(poseFromMatrix(self.obj.GetTransform()), [palm_approach_rel])[0]


	def orientHandtoObj(self, T_H, T_O, Obj):
		HandtoObject = np.dot(np.linalg.inv(T_O), T_H)
		self.obj.SetTransform(HandtoObject)
		self.localTranslation(-1 * Obj.objCentroid)
		return HandtoObject

	def ZSLERP(self, AA1, AA2, alpha, T_zero = None, move = True):
		# from AA1 to AA2
		AA_interp = AA1 * (1 - alpha) + AA2 * (alpha) #natural to think 10% interp is 10% away from start angle
		rot = matrixFromAxisAngle(AA_interp)
		if T_zero is None:
			T_zero = self.obj.GetTransform()
		T_new = np.dot(rot, T_zero)
		if move == True:
			self.obj.SetTransform(T_new)

		return T_new

	def retractFingers(self, Obj):
		contact_points, contact_links = retract_finger.retract_fingers(self.env, self.obj, Obj.obj)
		return contact_points, contact_links

	def addNoiseToGrasp(self, Obj, T_zero = None, Contact_JA = None, TL_n = 0.01, R_n = 0.1, JA_n = 0.1):
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

	def makeEqual(self, HandObj):
		self.obj.SetTransform(HandObj.obj.GetTransform())
		self.obj.SetDOFValues(HandObj.obj.GetDOFValues())

class Transforms(object): #class for holding all transform operations
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