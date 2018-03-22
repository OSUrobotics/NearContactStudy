import pdb
from NearContactStudy import Vis,HandVis,ObjectVis
from NearContactStudy import ParseGraspData
import numpy as np


#################
# This script is intended to be used to vary finger position angles
# and then extract the stl's for analysis of a metric
#########################

H_spray_JA = np.array([  2.22044605e-16,   2.22044605e-16,   4.89630558e-12,
						 3.64985819e-15,   1.96149010e-08,  -4.89630558e-12,
						 3.64985819e-15,   1.96149010e-08,  -6.66133815e-16,
						 1.96149011e-08])

#fingers already closed
H_spray_JA = np.array([  2.22044605e-16,   2.22044605e-16,   4.89652763e-12,
						 1.00200000e+00,   1.96149007e-08,   6.66133815e-16,
						 1.00200000e+00,   1.96149007e-08,   9.80000000e-01,
						 1.96149010e-08])

H_spray_T = np.array([[  1.00000000e+00,   1.28183806e-07,  -1.18871021e-07, -7.53312046e-03],
					[  1.28183863e-07,  -7.52839399e-02,   9.97162137e-01, -2.49331415e-01],
					[  1.18870959e-07,  -9.97162137e-01,  -7.52839399e-02, 9.65596922e-03],
					[  0.00000000e+00,   0.00000000e+00,   0.00000000e+00, 1.00000000e+00]])


class noiseJoints:
	def __init__(self, Hand, Object):
		self.H = Hand
		self.O = Object
		self.grasp_data = ParseGraspData()
		self.grasp_data.parseAllTransforms()


	def noisyGrasp_single(self, noise):
		grasp_noisy = self.H.addNoiseToGrasp(noise)
		self.H.setJointAngles(grasp_noisy)

	def generateSTL(self, fn):
		self.H.multiGenerateSTL(fn, [self.O])

	def showAllGraspsForObject(self, objNum):
		self.O.loadObject(objNum)
		grasp_list = self.grasp_data.findGrasp(objnum=objNum, list2check=self.grasp_data.all_transforms)
		for grasp in grasp_list:
			HandT, ObjT, Arm_JA, Hand_JA = self.grasp_data.matricesFromGrasp(grasp)
			self.H.setJointAngles(Hand_JA)
			self.H.globalTransformation(HandT)
			self.O.globalTransformation(ObjT)
			raw_input("Obj: %s, Sub: %s, Grasp: %s, Type: %s, Press Enter to continue..."
						%(grasp['obj'], grasp['sub'], grasp['grasp'], grasp['type']))











if __name__ == '__main__':
	V = Vis()
	H = HandVis(V)
	H.loadHand()
	O = ObjectVis(V)
	O.loadObject(2) # SprayBottle
	pdb.set_trace()
	H.setJointAngles(H_spray_JA)
	H.globalTransformation(H_spray_T)
	H.closeFingersToContact()
	NJ = noiseJoints(H, O)
	NJ.noisyGrasp_single(1e-4)
	NJ.generateSTL('noise_grasp.stl')