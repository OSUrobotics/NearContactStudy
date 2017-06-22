import sys, os, copy, subprocess, time, pdb
# import rospkg
# sys.path.insert(0, '~/Desktop/') # path to ParseGraspData
# path = rospkg.RosPack().get_path('valid_grasp_generator')
# sys.path.insert(0, path)
# print(sys.path)
from openravepy import *
from ParseGraspData import ParseGraspData
from Visualizers import Vis, GenVis, ObjectVis, HandVis
import numpy as np
import matplotlib.pyplot as plt 

class DataTester():
	# def __init__(self):


	def Test1(self): #just visualize a grasp
		V = Vis()
		Data = ParseGraspData()
		Data.parseGraspData()
		grasp = Data.val_grasp_data[100]
		Obj = ObjectVis(V)
		Obj.loadObjectList()
		Hand = HandVis(V)
		Hand.loadHand()
		Obj.loadObject(int(grasp['obj'].strip('obj')))
		Hand.globalQuatTranslationMove(grasp['HandRotation'], grasp['HandPosition'])
		Obj.globalQuatTranslationMove(grasp['ObjRotation'], grasp['ObjPosition'])
		V.close()

	def Test2(self): #visualize a specific grasp
		V = Vis()
		Data = ParseGraspData()
		Data.parseGraspData()
		Data.parseAllTransforms()
		grasps = Data.findGrasp(objnum = 4, subnum = 4, graspnum = 11, list2check = Data.all_transforms)
		for grasp in grasps:
			Obj = ObjectVis(V)
			Obj.loadObjectList()
			Hand = HandVis(V)
			Hand.loadHand()
			pdb.set_trace()
			Obj.loadObject(grasp['obj'])
			Hand.globalTransformation(grasp['HandTransformation'])
			Obj.globalTransformation(grasp['ObjTransformation'])
			
		V.close()

	def Test3(self): # Description: figure out how to apply centroid offset in general
		V = Vis()
		Obj1 = ObjectVis(V)
		Obj1.loadObject(4)
		Obj2 = ObjectVis(V)
		Obj2.loadObject(4)
		Obj3 = ObjectVis(V)
		Obj3.loadObject(4)


		Hand1 = HandVis(V)
		Hand1.loadHand()
		Hand2 = HandVis(V)
		Hand2.loadHand()
		# pose = [1, 0, 0, 0, 1, 0, 0]
		pose = np.random.rand(7)
		pose[:4] = pose[:4] / np.linalg.norm(pose[:4])
		rot_noTL = rotationMatrixFromQuat(pose[:4])
		Obj3.localRotation(rot_noTL)
		Obj3.adjustByCentroid()
		Obj1.globalTransformation(matrixFromPose(pose))
		Obj1.addObjectAxes()
		centroid_transform = poseTransformPoints(pose, -1*Obj1.objCentroid.reshape(1,3)) #effectively a local translation by centroid!
		pose_new = np.hstack((pose[:4], centroid_transform.reshape(3,)))
		Obj2.globalTransformation(matrixFromPose(pose_new))
		Obj2.addObjectAxes()
		Obj3.addObjectAxes()

		
		pdb.set_trace()

	def Test4(self): # Description: figure out how to apply local rotation
		V = Vis()
		Obj1 = ObjectVis(V)
		Obj2 = ObjectVis(V)
		Obj1.loadObject(4)
		Obj2.loadObject(4)
		Obj1.changeColor()
		rot = np.array([[0, -1, 0],
						[1, 0, 0],
						[0, 0, -1]])
		for i in range(10):
			rot = np.random.rand(3,3)
			rot = rot/np.linalg.norm(rot)

			Obj1.localRotation(rot)
			Obj1.adjustByCentroid()
			time.sleep(0.5)
		pdb.set_trace()

	def Test5(self): # Description: Orient Grasp relative to Object
		V = Vis()
		Hand1 = HandVis(V)
		Hand1.loadHand()
		Hand2 = HandVis(V)
		Hand2.loadHand()
		Obj1 = ObjectVis(V)
		Obj1.loadObject(4)
		Data = ParseGraspData()
		Data.parseAllTransforms()
		grasps = Data.findGrasp(objnum = 4, subnum = 4, graspnum = 11, list2check = Data.all_transforms)
		grasp = grasps[0]
		HandT = grasp['HandTransformation']
		ObjT = grasp['ObjTransformation']
		Arm_JA = grasp['JointAngles'][:7]
		Hand_JA = grasp['JointAngles'][7:]
		Hand1.orientHandtoObj(HandT, ObjT, Obj1)
		Hand1.setJointAngles(Hand_JA)
		Hand1.getPalmPoint()
		retract_finger.retract_fingers(V.env, Hand1.obj, Obj1.obj)

		grasp = grasps[1]
		HandT = grasp['HandTransformation']
		ObjT = grasp['ObjTransformation']
		Arm_JA = grasp['JointAngles'][:7]
		Hand_JA = grasp['JointAngles'][7:]
		Hand2.orientHandtoObj(HandT, ObjT, Obj1)
		Hand2.setJointAngles(Hand_JA)
		Hand2.getPalmPoint()
		retract_finger.retract_fingers(V.env, Hand2.obj, Obj1.obj)
		pdb.set_trace()

	def Test6(self): # Description: Rotate one grasp around center of object
		V = Vis()
		Hand1 = HandVis(V)
		Hand1.loadHand()
		Hand2 = HandVis(V)
		Hand2.loadHand()
		Obj1 = ObjectVis(V)
		Obj1.loadObject(4)
		Data = ParseGraspData()
		Data.parseAllTransforms()
		grasps = Data.findGrasp(objnum = 4, subnum = 4, graspnum = 11, list2check = Data.all_transforms)
		grasp = grasps[1]
		HandT = grasp['HandTransformation']
		ObjT = grasp['ObjTransformation']
		Arm_JA = grasp['JointAngles'][:7]
		Hand_JA = grasp['JointAngles'][7:]
		Hand1.orientHandtoObj(HandT, ObjT, Obj1)
		Hand1.setJointAngles(Hand_JA)
		Hand1.getPalmPoint()
		contact_points1, __ = retract_finger.retract_fingers(V.env, Hand1.obj, Obj1.obj)
		V.drawPoints(contact_points1, c = 'blue')
		Hand2.changeColor()
		Hand2.orientHandtoObj(HandT, ObjT, Obj1)
		T_zero = Hand1.obj.GetTransform()
		rot1 = matrixFromAxisAngle([0, 0, np.pi])
		rot2 = matrixFromAxisAngle([0, np.pi, 0])
		rot3 = matrixFromAxisAngle([np.pi, 0, 0])
		# Hand2.obj.SetTransform(np.dot(rot1, T_zero))
		Hand2.obj.SetTransform(np.dot(rot2, T_zero))
		# Hand2.obj.SetTransform(np.dot(rot3, T_zero))

		Hand2.setJointAngles(Hand_JA)
		Hand2.getPalmPoint()
		contact_points2, __ = retract_finger.retract_fingers(V.env, Hand2.obj, Obj1.obj)
		V.drawPoints(contact_points2, c = 'green')

		pdb.set_trace()


	def Test7(self): # Description: Interpolate grasp around the center axis of object
		V = Vis()
		Hand1 = HandVis(V)
		Hand1.loadHand()
		Hand2 = HandVis(V)
		Hand2.loadHand()
		Obj1 = ObjectVis(V)
		Obj1.loadObject(4)
		Data = ParseGraspData()
		Data.parseAllTransforms()
		grasps = Data.findGrasp(objnum = 4, subnum = 4, graspnum = 11, list2check = Data.all_transforms)
		grasp = grasps[1]
		HandT = grasp['HandTransformation']
		ObjT = grasp['ObjTransformation']
		Arm_JA = grasp['JointAngles'][:7]
		Hand_JA = grasp['JointAngles'][7:]
		Hand1.orientHandtoObj(HandT, ObjT, Obj1)
		Hand1.setJointAngles(Hand_JA)
		Hand1.getPalmPoint()
		contact_points1, __ = retract_finger.retract_fingers(V.env, Hand1.obj, Obj1.obj)
		V.drawPoints(contact_points1, c = 'blue')
		Hand2.changeColor()
		T_zero = Hand1.obj.GetTransform()
		start_axis_angle = np.array([0,0,0])
		end_axis_angle = np.array([0, np.pi, 0])
		rot2 = matrixFromAxisAngle(end_axis_angle)
		Hand2.obj.SetTransform(np.dot(rot2, T_zero))
		Hand2.setJointAngles(Hand1.obj.GetDOFValues())
		Hand2.getPalmPoint()
		contact_points2, __ = retract_finger.retract_fingers(V.env, Hand2.obj, Obj1.obj)
		V.drawPoints(contact_points2, c = 'green')

		Hand3 = HandVis(V)
		Hand3.loadHand()
		start_quat = quatFromAxisAngle(start_axis_angle)
		end_quat = quatFromAxisAngle(end_axis_angle)
		alpha = 0.8
		interp_axis_angle = (end_axis_angle - start_axis_angle) * alpha
		interp_rotation = matrixFromAxisAngle(interp_axis_angle)
		Hand3.obj.SetTransform(np.dot(interp_rotation, T_zero))
		Hand3.setJointAngles(Hand1.obj.GetDOFValues())
		Hand3.getPalmPoint()
		contact_points3, __ = retract_finger.retract_fingers(V.env, Hand3.obj, Obj1.obj)
		V.drawPoints(contact_points3, c = 'red')

		pdb.set_trace()

		pass

	def Test8(self): # Description: Add noise to the grasp
		V = Vis()
		Hand1 = HandVis(V)
		Hand1.loadHand()
		Hand2 = HandVis(V)
		Hand2.loadHand()
		Obj1 = ObjectVis(V)
		Obj1.loadObject(4)
		Data = ParseGraspData()
		Data.parseAllTransforms()
		grasps = Data.findGrasp(objnum = 4, subnum = 4, graspnum = 11, list2check = Data.all_transforms)
		grasp = grasps[1]
		HandT, ObjT, Arm_JA, Hand_JA = Data.matricesFromGrasp(grasp)
		Hand1.orientHandtoObj(HandT, ObjT, Obj1)
		Hand1.setJointAngles(Hand_JA)
		Hand1.getPalmPoint()
		contact_points1, contact_links1 = retract_finger.retract_fingers(V.env, Hand1.obj, Obj1.obj)
		Contact_JA = Hand1.obj.GetDOFValues()
		V.drawPoints(contact_points1, c = 'blue')
		T_noise, JA_noise = Hand2.addNoiseToGrasp(Obj1, T_zero = Hand1.obj.GetTransform(), Contact_JA = Contact_JA, TL_n = 0.01, R_n = 0.1, JA_n = 0.1)
		pdb.set_trace()
		return JA_noise, T_noise


	def Test9(self): # Description: Record image of scene
		V = Vis()
		Hand1 = HandVis(V)
		Hand1.loadHand()
		Hand2 = HandVis(V)
		Hand2.loadHand()
		Obj1 = ObjectVis(V)
		Obj1.loadObject(4)
		pdb.set_trace()
		fname_save = 'test.png'
		V.takeImage(fname_save) # test this!

		pdb.set_trace()


	def Test10(self): # Description: Add noise and interpolate (take image at end)
		# do STLs with noise after this.

		
		V = Vis()
		Hand1 = HandVis(V)
		Hand1.loadHand()
		Hand2 = HandVis(V)
		Hand2.loadHand()
		Obj1 = ObjectVis(V)
		Obj1.loadObject(4)

		Data = ParseGraspData()
		grasps = Data.findGrasp(objnum = 4, subnum = 4, graspnum = 11, list2check = Data.all_transforms)
		grasp = grasps[1]
		HandT, ObjT, Arm_JA, Hand_JA = Data.matricesFromGrasp(grasp)
		Hand1.orientHandtoObj(HandT, ObjT, Obj1)
		Hand1.setJointAngles(Hand_JA)
		Hand1.getPalmPoint()
		contact_points1, contact_links1 = Hand1.retractFingers(Obj1)
		Contact_JA = Hand1.obj.GetDOFValues()

		filename_base = "obj%s_sub%s_graspnum%s_grasptype%s" %(4, 4, 11, 'extreme0')
		if False:
			T_noise, JA_noise = Hand2.addNoiseToGrasp(Obj1, T_zero = Hand1.obj.GetTransform(), Contact_JA = Contact_JA, TL_n = 0.01, R_n = 0.1, JA_n = 0.1)
			np.savetxt(filename_base + "_%s.txt" %'T_noise', T_noise)
			np.savetxt(filename_base + "_%s.txt" %'JA_noise', JA_noise)
		else:
			JA_noise = np.genfromtxt(filename_base + "_%s.txt" %'JA_noise')
			T_noise = np.genfromtxt(filename_base + "_%s.txt" %'T_noise')
		Hand2.setJointAngles(JA_noise)
		Hand2.obj.SetTransform(T_noise)
		contact_points2, contact_links2 = Hand2.retractFingers(Obj1)
		alpha = np.linspace(0,1,6)[1:-1]
		start_axis_angle = np.array([0,0,0])
		end_axis_angle = np.array([0, np.pi, 0])
		Hand1.hide()
		for a in alpha:
			filename = filename_base + "_alpha%s.png" %(int(10*a))
			Hand2.ZSLERP(start_axis_angle, end_axis_angle, a, T_zero = T_noise)
			V.clearPoints()
			V.takeImage(filename)
			time.sleep(1)


		pdb.set_trace()

	def Test11(self): # Description: Generating Images for Interpolated Grasps
		# Oriignal is grey
		# 180 + noise grasp is pink
		# interpolated is violet

		# do STLs with noise after this.
		
		V = Vis()
		Hand1 = HandVis(V)
		Hand1.loadHand()
		Hand2 = HandVis(V)
		Hand2.loadHand()
		Obj1 = ObjectVis(V)
		Obj1.loadObject(4)
		Obj1.changeColor('green')

		Data = ParseGraspData()
		Data.parseOutputData()
		Data.parseAllTransforms()
		# obj4_cluster13_sub5_grasp2_optimal0_prime.jpg obj4_cluster13_sub5_grasp3_extreme1_target.jpg -- don't have the data.  Tried without class but extreme grasp was too far!
		# grasp1 = Data.findGrasp(objnum = 4, subnum = 5, graspnum = 2, grasptype = 'optimal0', list2check = Data.all_transforms)
		# grasp2 = Data.findGrasp(objnum = 4, subnum = 5, graspnum = 3, grasptype = 'extreme1', list2check = Data.all_transforms)
		# obj4_cluster8_sub4_grasp14_extreme1_prime.jpg obj4_cluster8_sub4_grasp14_optimal0_target.jpg -- don't have the data
		# grasp1 = Data.findGrasp(objnum = 4, subnum = 4, graspnum = 14, grasptype = 'extreme1', list2check = Data.all_transforms)
		# grasp2 = Data.findGrasp(objnum = 4, subnum = 4, graspnum = 14, grasptype = 'optimal0', list2check = Data.all_transforms)
		# obj4_cluster8_sub4_grasp14_extreme1_prime.jpg obj4_cluster8_sub4_grasp9_optimal0_target.jpg -- don't have the data

		#ones that I think look good

		# grasp1 = Data.findGrasp(objnum = 4, subnum = 4, graspnum = 11, grasptype = 'optimal0', list2check = Data.all_transforms)
		# grasp2 = Data.findGrasp(objnum = 4, subnum = 4, graspnum = 11, grasptype = 'optimal0', list2check = Data.all_transforms)

		grasp1 = Data.findGrasp(objnum = 4, subnum = 5, graspnum = 3, grasptype = 'optimal0', list2check = Data.all_transforms)
		grasp2 = Data.findGrasp(objnum = 4, subnum = 5, graspnum = 3, grasptype = 'extreme0', list2check = Data.all_transforms)

		# filename_base = "obj%s_sub%s_graspnum%s_%s_%s" %(4, 4, 11, 'optimal0', 'optimal0')
		# filename_base = "obj%s_sub%s_graspnum%s_%s_%s" %(4, 5, '2&3', 'optimal0', 'extreme1')
		filename_base = "obj%s_sub%s_graspnum%s_%s_%s" %(4, 5, 3, 'optimal0', 'extreme0')
		HandT1, ObjT1, Arm_JA1, Hand_JA1 = Data.matricesFromGrasp(grasp1[0])
		HandT2, ObjT2, Arm_JA2, Hand_JA2 = Data.matricesFromGrasp(grasp2[0])
		Hand1.orientHandtoObj(HandT1, ObjT1, Obj1)
		Hand1.setJointAngles(Hand_JA1)
		Hand1.changeColor('greyI')
		Hand2.orientHandtoObj(HandT2, ObjT2, Obj1)
		Hand2.setJointAngles(Hand_JA2)
		Hand2.changeColor('pinkI')
		Hand1.getPalmPoint()
		contact_points1, contact_links1 = Hand1.retractFingers(Obj1)
		contact_points2, contact_links2 = Hand2.retractFingers(Obj1)

		start_axis_angle = np.array([0,0,0])
		end_axis_angle = np.array([0, np.pi, 0])
		Hand2.ZSLERP(start_axis_angle, end_axis_angle, 1, T_zero = Hand2.obj.GetTransform())
		Hand3 = HandVis(V); Hand3.loadHand()
		Hand3.makeEqual(Hand1)
		Hand3.changeColor('blueI')
		alpha = np.linspace(0,1,6)[1:-1]
		for a in alpha:
			filename = filename_base + "_alpha%s.png" %(int(10*a))
			Hand3.ZSLERP(start_axis_angle, end_axis_angle, a, T_zero = Hand1.obj.GetTransform())
			V.clearPoints()
			V.takeImage(filename)
			time.sleep(1)


		# pdb.set_trace()

## may want to use quatRotate for some of the rotations?

if __name__ == '__main__':
	DT = DataTester()
	DT.Test11()


