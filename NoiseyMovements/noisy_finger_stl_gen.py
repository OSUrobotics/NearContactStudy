import pdb
from NearContactStudy import Vis,HandVis,ObjectVis
from NearContactStudy import ParseGraspData
# from NearContactStudy import noiseJoints
import numpy as np
import os


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


	def noisyGrasp_single(self, noise, percent=False):
		grasp_noisy = self.H.addNoiseToGrasp(noise, percent)
		self.H.setJointAngles(grasp_noisy)
		return grasp_noisy

	def generateSTL(self, fn):
		self.H.multiGenerateSTL(fn, [self.O])

	def showAllGraspsForObject(self, objNum):
		self.O.loadObject(objNum)
		grasp_list = self.grasp_data.findGrasp(objnum=objNum, list2check=self.grasp_data.all_transforms)
		for grasp in grasp_list:
			self.showGrasp(grasp)
			raw_input("Obj: %s, Sub: %s, Grasp: %s, Type: %s, Press Enter to continue..."
						%(grasp['obj'], grasp['sub'], grasp['grasp'], grasp['type']))

	def showGrasp(self, grasp):
		HandT, ObjT, Arm_JA, Hand_JA = self.grasp_data.matricesFromGrasp(grasp)
		ObjT_0 = np.matmul(np.linalg.inv(ObjT), ObjT) # move to 0
		HandT_0 = np.matmul(np.linalg.inv(ObjT), HandT) # adjust hand position accordingly
		self.H.setJointAngles(Hand_JA)
		self.H.globalTransformation(HandT_0)
		self.O.globalTransformation(ObjT_0)

	def N_noisyGrasp(self, noise, N, folder=None, percent=False):
		start_JA = self.H.getJointAngles()
		fn = 'noise_grasp%s.stl'
		if folder is not None:
			fn = os.path.join(folder, fn)
			try:
				os.makedirs(folder)
			except:
				print('Folder %s already exists' %folder)
				pass
		for i in range(N):
			self.noisyGrasp_single(noise, percent=percent)
			self.generateSTL(fn %i )
			self.H.setJointAngles(start_JA)
			print('File %s Created' %(fn %i))













if __name__ == '__main__':
	V = Vis()
	H = HandVis(V)
	H.loadHand()
	O = ObjectVis(V)
	O.loadObject(2) # SprayBottle
	# H.setJointAngles(H_spray_JA)
	# H.globalTransformation(H_spray_T)
	# H.closeFingersToContact()
	NJ = noiseJoints(H, O)
	# NJ.showAllGraspsForObject(2)
	grasp = NJ.grasp_data.findGrasp(objnum=2, subnum=4, graspnum=6, grasptype='optimal0', list2check=NJ.grasp_data.all_transforms)[0]
	NJ.showGrasp(grasp)
	H.moveToMakeValidGrasp()
	NJ.N_noisyGrasp(1e-4, 10)
	NJ.noisyGrasp_single(1e-4)
	NJ.generateSTL('noise_grasp.stl')


	# grab bottle from squarish part with palm on narrower side
	# Obj: 2, Sub: 4, Grasp: 6, Type: optimal0
	# Obj: 2, Sub: 4, Grasp: 6, Type: extreme0
	# Obj: 2, Sub: 6, Grasp: 3, Type: optimal0
