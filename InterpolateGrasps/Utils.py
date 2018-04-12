import numpy as np
from openravepy import *
import pyquaternion

class UtilTransforms(object): #class for holding all transform operations -- this may be useless!
	def __init__(self):
		self.i = 1
	
	@staticmethod
	def TL2T(Tl):
	# converts a translation vector into a transformation matrix
		#Tl = np.array(Tl)
		#T_pose = np.hstack((np.array([1,0,0,0]), Tl)) # zero rotation quaternion
		#T_new = matrixFromPose(T_pose)
		T_new = np.eye(4);
		T_new[0:3,3] = Tl
		return T_new

	@staticmethod
	def R2T(R):
	# converts a rotation matrix into a transformation matrix
		T = np.eye(4)
		T[:3,:3] = R
		return T

	#@classmethod
	#def AddTranslationToTransformation(cls,Tl, T):
#		T[:3,3] += Tl[:]
#		if len(Tl) == 3:
#			T[:3,3] += Tl[:]
#		else: # if it is a transformation matrix
#			T[:3,3] += Tl[:3,3]
#		return T

	@classmethod
	def RTL2T(cls, R, Tl):
		T = np.eye(4)
		T = cls.R2T(R) * cls.TL2T(Tl)
		return T

	@staticmethod
	def Q2T(q):
	# converts a quaternion to a transformation matrix
		Q = pyquaternion.Quaternion(q)
		return Q.transformation_matrix

	@staticmethod
	def RotZ(Beta):
		Tz = [	[np.cos(Beta), -np.sin(Beta), 0, 0],
				[np.sin(Beta), np.cos(Beta), 0, 0],
				[0, 0, 1, 0],
				[0, 0, 0, 1]
		]
		return np.array(Tz)

	@staticmethod
	def RotX(Gamma):
		s = np.sin(Gamma);
		c = np.cos(Gamma);
		Tx = [
		[1,	0,	0,	0],
		[0,	c,	-s,	0],
		[0,	s,	c,	0],
		[0,	0,	0,	1]
		]
		return np.array(Tx)

	@staticmethod
	def RotY(Beta):
		s = np.sin(Beta);
		c = np.cos(Beta);
		Ty = [
		[c,		0,	s,	0],
		[0,		1,	0,	0],
		[-s,	0,	c,	0],
		[0,		0,	0,	1]
		]
		return np.array(Ty)