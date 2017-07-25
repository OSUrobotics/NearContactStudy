import cv2
import os, pdb, copy, time, sys, csv, shutil
import numpy as np
curdir = os.path.dirname(os.path.realpath(__file__))
classdir = curdir +'/../InterpolateGrasps/'
sys.path.insert(0, classdir) # path to helper classes
from Visualizers import Vis, GenVis, HandVis, ObjectGenericVis
from ShapeImageGeneratorTest import ShapeImageGenerator
from openravepy import matrixFromPose, poseTransformPoints, poseMult, transformLookat




# Author: Ammar Kothari - Editted 7/18/17
# class to create the images that are used in the study table
class TableImageGenerator(object):
	def __init__(self):
		self.SIG = ShapeImageGenerator()
		self.SIG.Hand.changeColor('blueI')
		self.ImageFolder = 'GraspTypesImages'
		self.HandList = list()
		self.HandList.append(self.SIG.Hand)
		self.threeFingerPinch = np.array([0,0,0,0.1,0.1,0,0.1,0.1,0.1,0.1])
		self.equidistant = np.array([0,0,np.pi/3,0.1,0.1,np.pi/3,0.1,0.1,0.1,0.1])
		self.hook = np.array([0,0,np.pi,0.1,0.1,np.pi,0.1,0.1,0.1,0.1])
		self.twoFingerPinch = np.array([0,0,np.pi/2,0.1,0.1,np.pi/2,0.1,0.1,0.1,0.1])


	def loadAdditionalHand(self):
		self.HandList.append(HandVis(self.SIG.vis))
		self.HandList[-1].loadHand()
		self.HandList[-1].show()
		self.HandList[-1].changeColor('blueI')

	def removeHand(self, ind = -1): # remove last hand in list
		self.SIG.vis.env.Remove(self.HandList[ind].obj)
		self.HandList.pop(ind)

	def positionVariation(self, handvis_obj1, handvis_obj2, T_start, d, dim, transparency = False): #shows hand change position
		for h in [handvis_obj1, handvis_obj2]:
			h.setJointAngles(self.threeFingerPinch)
			h.obj.SetTransform(T_start)
			if transparency:
				h.changeColor(alpha = 0.1)
		if dim == 'x':
			handvis_obj2.moveX(d)
		elif dim == 'y':
			handvis_obj2.moveY(d)
		elif dim == 'z':
			handvis_obj2.moveZ(d)
		else:
			print('Not a valid dimension')
			return False

	def rotationVariation(self, handvis_obj1, handvis_obj2, T_start, r, dim, transparency = False): #shows hand change position
		for h in [handvis_obj1, handvis_obj2]:
			h.setJointAngles(self.threeFingerPinch)
			h.obj.SetTransform(T_start)
			if transparency:
				h.changeColor(alpha = 0.25)
		if dim == 'x':
			handvis_obj2.rotX(r)
		elif dim == 'y':
			handvis_obj2.rotY(r)
		elif dim == 'z':
			handvis_obj2.rotZ(r)
		else:
			print('Not a valid dimension')
			return False

	def showExtentDisplacement(self):
		self.loadAdditionalHand()
		self.SIG.loadObject('cube', 9, 6, 3)
		HandT_close = np.array([[-0.04130666,  0.00697219, -0.99912219,  0.12647927],
						       [ 0.99623446,  0.0765784 , -0.04065289,  0.00315787],
						       [ 0.07622774, -0.99703919, -0.01010914,  0.00844372],
						       [ 0.        ,  0.        ,  0.        ,  1.        ]])

		cameraT = np.array([[-0.90334304, -0.28681269,  0.31891979, -0.09966846],
					       [ 0.03851306,  0.68630138,  0.72629688, -0.33613098],
					       [-0.42718625,  0.66837781, -0.60891954,  0.30641025],
					       [ 0.        ,  0.        ,  0.        ,  1.        ]])

		variationDist = 0.1
		filename = os.path.join(self.ImageFolder,'ExtentDisplacement')
		self.SIG.Obj.changeColor('greenI')
		self.SIG.groundPlane.createGroundPlane(self.SIG.Obj.h/2/100.0)
		self.positionVariation(self.HandList[0], self.HandList[1], HandT_close, variationDist, 'x', transparency = True)
		self.SIG.vis.viewer.SetCamera(cameraT)
		self.SIG.vis.takeImage(filename)

	def showExtentRotation(self):
		self.loadAdditionalHand()
		self.SIG.loadObject('cube', 9, 6, 3)
		HandT_close = np.array([[-0.28685032, -0.01221862, -0.95789749,  0.12337235],
						       [ 0.95493781,  0.07591818, -0.28693241, -0.01489359],
						       [ 0.07622775, -0.99703918, -0.01010913,  0.00944319],
						       [ 0.        ,  0.        ,  0.        ,  1.        ]])

		cameraT = np.array([[-0.90334304, -0.28681269,  0.31891979, -0.09966846],
					       [ 0.03851306,  0.68630138,  0.72629688, -0.33613098],
					       [-0.42718625,  0.66837781, -0.60891954,  0.30641025],
					       [ 0.        ,  0.        ,  0.        ,  1.        ]])

		self.SIG.vis.viewer.SetCamera(cameraT)
		variationDist = np.pi/6
		filename = os.path.join(self.ImageFolder,'ExtentRotation')
		self.SIG.Obj.changeColor('greenI')
		self.SIG.groundPlane.createGroundPlane(self.SIG.Obj.h/2/100.0)
		self.rotationVariation(self.HandList[0], self.HandList[1], HandT_close, variationDist, 'z', transparency = False)
		self.HandList[0].changeColor('pinkI')
		self.SIG.vis.takeImage(filename)
		self.removeHand()

	def showWidthDisplacement(self):
		self.loadAdditionalHand()
		self.SIG.loadObject('cube', 9, 6, 3)
		HandT_close = np.array([[-0.04130666,  0.00697219, -0.99912219,  0.12647927],
						       [ 0.99623446,  0.0765784 , -0.04065289,  0.00315787],
						       [ 0.07622774, -0.99703919, -0.01010914,  0.00844372],
						       [ 0.        ,  0.        ,  0.        ,  1.        ]])

		cameraT = np.array([[-0.90334304, -0.28681269,  0.31891979, -0.09966846],
					       [ 0.03851306,  0.68630138,  0.72629688, -0.33613098],
					       [-0.42718625,  0.66837781, -0.60891954,  0.30641025],
					       [ 0.        ,  0.        ,  0.        ,  1.        ]])

		variationDist = -0.1
		filename = os.path.join(self.ImageFolder,'WidthDisplacement')
		self.SIG.Obj.changeColor('greenI')
		self.SIG.groundPlane.createGroundPlane(self.SIG.Obj.h/2/100.0)
		self.positionVariation(self.HandList[0], self.HandList[1], HandT_close, variationDist, 'z', transparency = True)
		self.HandList[0].changeColor('pinkI')
		self.SIG.vis.viewer.SetCamera(cameraT)
		self.SIG.vis.takeImage(filename)

	def showWidthRotation(self):
		self.loadAdditionalHand()
		self.SIG.loadObject('cube', 9, 6, 3)
		HandT_close = np.array([[-0.28685032, -0.01221862, -0.95789749,  0.12337235],
						       [ 0.95493781,  0.07591818, -0.28693241, -0.01489359],
						       [ 0.07622775, -0.99703918, -0.01010913,  0.00944319],
						       [ 0.        ,  0.        ,  0.        ,  1.        ]])

		cameraT = np.array([[-0.90334304, -0.28681269,  0.31891979, -0.09966846],
					       [ 0.03851306,  0.68630138,  0.72629688, -0.33613098],
					       [-0.42718625,  0.66837781, -0.60891954,  0.30641025],
					       [ 0.        ,  0.        ,  0.        ,  1.        ]])

		variationDist = np.pi/6
		filename = os.path.join(self.ImageFolder,'WidthRotation')
		self.SIG.Obj.changeColor('greenI')
		self.SIG.groundPlane.createGroundPlane(self.SIG.Obj.h/2/100.0)
		self.rotationVariation(self.HandList[0], self.HandList[1], HandT_close, variationDist, 'y', transparency = False)
		self.HandList[0].changeColor('pinkI')
		self.SIG.vis.viewer.SetCamera(cameraT)
		self.SIG.vis.takeImage(filename)
		self.removeHand()


	def showHeightDisplacement(self):
		self.loadAdditionalHand()
		self.SIG.loadObject('cube', 12, 6, 3)
		HandT_close = np.array([[-0.04130666,  0.00697219, -0.99912219,  0.12647927],
						       [ 0.99623446,  0.0765784 , -0.04065289,  0.00315787],
						       [ 0.07622774, -0.99703919, -0.01010914,  0.00844372],
						       [ 0.        ,  0.        ,  0.        ,  1.        ]])

		cameraT = np.array([[-0.90334304, -0.28681269,  0.31891979, -0.09966846],
					       [ 0.03851306,  0.68630138,  0.72629688, -0.33613098],
					       [-0.42718625,  0.66837781, -0.60891954,  0.30641025],
					       [ 0.        ,  0.        ,  0.        ,  1.        ]])

		variationDist = -0.1
		filename = os.path.join(self.ImageFolder,'HeightVariation')
		self.SIG.Obj.changeColor('greenI')
		self.SIG.groundPlane.createGroundPlane(self.SIG.Obj.h/2/100.0)
		self.positionVariation(self.HandList[0], self.HandList[1], HandT_close, variationDist, 'y', transparency = True)
		self.HandList[0].changeColor('pinkI')
		self.SIG.vis.viewer.SetCamera(cameraT)
		self.SIG.vis.takeImage(filename)

	def showHeightRotation(self):
		self.loadAdditionalHand()
		self.SIG.loadObject('cube', 9, 6, 3)
		HandT_close = np.array([[-0.08030137,  0.63819909, -0.765672  ,  0.1095985 ],
						       [ 0.99623446,  0.07657835, -0.04065286,  0.00315787],
						       [ 0.03268928, -0.76605331, -0.64194527,  0.05413172],
						       [ 0.        ,  0.        ,  0.        ,  1.        ]])

		cameraT = np.array([[-0.90334304, -0.28681269,  0.31891979, -0.09966846],
					       [ 0.03851306,  0.68630138,  0.72629688, -0.33613098],
					       [-0.42718625,  0.66837781, -0.60891954,  0.30641025],
					       [ 0.        ,  0.        ,  0.        ,  1.        ]])

		rotationDist = np.pi/6
		filename = os.path.join(self.ImageFolder,'HeightRotation')
		self.SIG.Obj.changeColor('greenI')
		self.SIG.groundPlane.createGroundPlane(self.SIG.Obj.h/2/100.0)
		self.rotationVariation(self.HandList[0], self.HandList[1], HandT_close, rotationDist, 'x', transparency = True)
		self.HandList[0].changeColor('pinkI')
		self.SIG.vis.viewer.SetCamera(cameraT)
		self.SIG.vis.takeImage(filename)
		self.removeHand()

	def equidistantPregrasp(self):
		self.HandList[0].setJointAngles(self.equidistant)
		self.HandList[0].obj.SetTransform(np.eye(4))
		self.SIG.groundPlane.createGroundPlane(-0.1)
		cameraT = np.array([[ 0.65212081, -0.43412208,  0.62151144, -0.38697323],
					       [-0.02831762, -0.83318784, -0.55226455,  0.37152871],
					       [ 0.75758601,  0.34254348, -0.55563244,  0.34353289],
					       [ 0.        ,  0.        ,  0.        ,  1.        ]])
		filename = os.path.join(self.ImageFolder,'equidistantPregrasp')
		self.SIG.vis.viewer.SetCamera(cameraT)
		self.HandList[0].changeColor(color = 'blueI')
		self.SIG.vis.takeImage(filename)

	def threeFingerPinchPregrasp(self):
		self.HandList[0].setJointAngles(self.threeFingerPinch)
		self.HandList[0].obj.SetTransform(np.eye(4))
		self.HandList[0].rotZ(np.pi/2)
		self.SIG.groundPlane.createGroundPlane(-0.1)
		cameraT = np.array([[ 0.65212081, -0.43412208,  0.62151144, -0.38697323],
					       [-0.02831762, -0.83318784, -0.55226455,  0.37152871],
					       [ 0.75758601,  0.34254348, -0.55563244,  0.34353289],
					       [ 0.        ,  0.        ,  0.        ,  1.        ]])
		filename = os.path.join(self.ImageFolder,'ThreeFingerPinchPregrasp')
		self.SIG.vis.viewer.SetCamera(cameraT)
		self.HandList[0].changeColor(color = 'blueI')
		self.SIG.vis.takeImage(filename)

	def hookPregrasp(self):
		self.HandList[0].setJointAngles(self.hook)
		self.HandList[0].obj.SetTransform(np.eye(4))
		self.HandList[0].rotZ(-np.pi/2)
		self.SIG.groundPlane.createGroundPlane(-0.1)
		cameraT = np.array([[ 0.65212081, -0.43412208,  0.62151144, -0.38697323],
					       [-0.02831762, -0.83318784, -0.55226455,  0.37152871],
					       [ 0.75758601,  0.34254348, -0.55563244,  0.34353289],
					       [ 0.        ,  0.        ,  0.        ,  1.        ]])
		filename = os.path.join(self.ImageFolder,'HookPregrasp')
		self.SIG.vis.viewer.SetCamera(cameraT)
		self.HandList[0].changeColor(color = 'blueI')
		self.SIG.vis.takeImage(filename)

	def twoFingerPinchPregrasp(self):
		self.HandList[0].setJointAngles(self.twoFingerPinch)
		self.HandList[0].obj.SetTransform(np.eye(4))
		self.SIG.groundPlane.createGroundPlane(-0.1)
		cameraT = np.array([[ 0.65212081, -0.43412208,  0.62151144, -0.38697323],
					       [-0.02831762, -0.83318784, -0.55226455,  0.37152871],
					       [ 0.75758601,  0.34254348, -0.55563244,  0.34353289],
					       [ 0.        ,  0.        ,  0.        ,  1.        ]])
		filename = os.path.join(self.ImageFolder,'TwoFingerPinchPregrasp')
		self.SIG.vis.viewer.SetCamera(cameraT)
		self.HandList[0].changeColor(color = 'blueI')
		unused_finger_alpha = 0.5
		# set unused finger to more transparent
		t_line_draw = list()
		n_points = 750
		verts_imp = list()
		link_gen = (link for link in self.HandList[0].obj.GetLinks() if 'finger_3' in link.GetName())
		for link in link_gen:
			for geos in link.GetGeometries():
				geos.SetTransparency(unused_finger_alpha)
				# P_total = poseMult(link.GetTransformPose(), geos.GetTransformPose())
				# tmesh = geos.GetCollisionMesh()
				# verts_transformed = poseTransformPoints(P_total, tmesh.vertices)
				# t_line_draw.append(self.SIG.vis.env.plot3(verts_transformed[::50], pointsize = 5))
				# dist = np.zeros(len(tmesh.vertices) -1)
				# verts_group = list()
				# for idx,v in enumerate(tmesh.vertices[:-2]):
				# 	dist[idx] = np.linalg.norm(tmesh.vertices[idx] - tmesh.vertices[idx+1])
				# 	if dist[idx] > 5e-2: # if large distance than add to next line set
				# 		verts_imp.append(verts_group)
				# 		# pdb.set_trace()
				# 		verts_group = np.array(verts_group)
				# 		verts_transformed = poseTransformPoints(P_total, verts_group)
				# 		pdb.set_trace()
				# 		t_line_draw.append(self.SIG.vis.env.drawlinelist(verts_transformed, linewidth = 3))
						
				# 		verts_group = list()
				# 	verts_group.append(tmesh.vertices[idx])
				# pdb.set_trace()
				
					
					
					# 	verts_imp.append(tmesh.vertices[idx])
					# if i == 1:
					# 	i = 2
				# verts_transformed = poseTransformPoints(P_total, tmesh.vertices)
				# t_line_draw.append(self.SIG.vis.env.drawlinestrip(verts_transformed[0::n_points], linewidth = 3))
				
		# pdb.set_trace()
		self.SIG.vis.takeImage(filename)

		# to make a wireframe
		#tmesh = geos.GetCollisionMesh()
		#env.drawtrimesh(verts[:,:])
		#env.drawlinestrip(verts[0:100,:], linewidth = 3)

	def palmDistanceMetric(self):
		self.SIG.loadObject('cube', 9, 6, 3)
		self.SIG.Obj.changeColor('greenI')
		HandT = np.array([[ 0.08,  1.  , -0.03,  0.  ],
					       [ 1.  , -0.08, -0.  , -0.  ],
					       [-0.  , -0.03, -1.  ,  0.21],
					       [ 0.  ,  0.  ,  0.  ,  1.  ]])

		cameraT = np.array([[ 0.02598803,  0.99090335,  0.13204235, -0.08580729],
					       [ 0.09352606,  0.12909753, -0.98721158,  0.6148898 ],
					       [-0.9952776 ,  0.03800508, -0.0893203 ,  0.09105067],
					       [ 0.        ,  0.        ,  0.        ,  1.        ]])
		filename = os.path.join(self.ImageFolder,'PalmDistanceMetric')

		self.HandList[0].obj.SetTransform(HandT)
		self.SIG.groundPlane.createGroundPlane(self.SIG.Obj.h/2/100.0)
		self.SIG.vis.viewer.SetCamera(transformLookat([0,0,0],[0, -.6,0], [1,0,0]) ) # move point to between palm and face of object
		self.HandList[0].changeColor(color = 'blueI')
		# self.SIG.vis.viewer.SetCamera(np.round(cameraT,4))

		self.SIG.vis.takeImage(filename)
		pdb.set_trace()

	def TestRotation(self):
		# self.SIG.loadObject('cube', 9, 6, 3)
		HandT_close = np.array([[-0.28685032, -0.01221862, -0.95789749,  0.12337235],
						       [ 0.95493781,  0.07591818, -0.28693241, -0.01489359],
						       [ 0.07622775, -0.99703918, -0.01010913,  0.00944319],
						       [ 0.        ,  0.        ,  0.        ,  1.        ]])
		self.HandList[0].obj.SetTransform(HandT_close)
		self.SIG.vis.DrawGlobalAxes()
		self.SIG.vis.drawPoints(self.HandList[0].getPalmPoint())
		self.HandList[0].rotZ(np.pi)





if __name__ == '__main__':
	TIG = TableImageGenerator()
	# TIG.showExtentDisplacement()
	# TIG.showWidthDisplacement()
	# TIG.showHeightDisplacement()
	TIG.showExtentRotation()
	TIG.showWidthRotation()
	TIG.showHeightRotation()

	# TIG.equidistantPregrasp()
	# TIG.threeFingerPinchPregrasp()
	# TIG.hookPregrasp()
	# TIG.twoFingerPinchPregrasp()
	# TIG.palmDistanceMetric()

	# TIG.TestRotation()
	pdb.set_trace()
