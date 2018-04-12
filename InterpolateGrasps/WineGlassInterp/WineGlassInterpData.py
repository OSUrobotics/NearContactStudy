import pdb
import numpy as np
import csv, time
import rosbag
import copy


from NearContactStudy import Vis, ArmVis, ObjectVis, AddGroundPlane, HandVis, ArmVis_OR
from NearContactStudy import UtilTransforms
from NearContactStudy import BagReader
import openravepy

from cv_bridge import CvBridge, CvBridgeError
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import pyquaternion

object_transforms = {'grasp1': np.array([[-0.940495  ,  0.06519729,  0.33349432,  0.00246401],
										 [ 0.33195813, -0.03344439,  0.94270105,  0.84647357],
										 [ 0.07261507,  0.99731178,  0.00981151,  0.11387653],
										 [ 0.        ,  0.        ,  0.        ,  1.        ]]),
					'grasp2': np.array([[-0.940495  ,  0.06519729,  0.33349432, -0.02447402],
										[ 0.33195813, -0.03344439,  0.94270105,  0.8609255 ],
										[ 0.07261507,  0.99731178,  0.00981151,  0.11387654],
										[ 0.        ,  0.        ,  0.        ,  1.        ]])
					
					}

SLERP_center = {'grasp2': np.array([[ 0.717638,  0.      , -0.696417, -0.051881],
									[-0.      ,  1.      ,  0.      ,  0.938581],
									[ 0.696417, -0.      ,  0.717638,  0.276977],
									[ 0.      ,  0.      ,  0.      ,  1.      ]])
}

'''
from WineGlassInterpData import WineGlassInterpData, readRosBag, InterpHandPositions, readTextCapturedGrasps, object_transforms
import numpy as np
import matplotlib.pyplot as plt
W = WineGlassInterpData(fn='grasp1.bag')
I = InterpHandPositions(W)
W.data.showRGB()
I.loadGrasp(0)
I.alignToManualTransform(object_transforms['grasp1'])

# I.alignToObject()
# b = readRosBag('nothing_on_table.bag')
# b = readRosBag('glass_on_table.bag')
b = readRosBag('grasp1.bag')
b.loadAllMessages()
b.getIndices()
b.getXYZRGB()
b.getRGB()
b.showRGB()
b.showPC(b.xyzrgb)
b.showPlot()
'''


FIELDNAMES = ['JA_arm', 'JA_hand']


class readRosBag(BagReader):
	# this class is intended to be used with bag files that recor a single snapshot
	# expect there to be joint angles for arm and hand, depth image, rgb image

	def __init__(self, fn):
		super(readRosBag, self).__init__()
		self.FIELDNAMES = FIELDNAMES
		self.loadBagFile(fn)
		self.loadAllMessages()
		self.getIndices()
		self.createDictionary()
		self.getRGB()
		self.getXYZRGB()

	def loadBagFile(self, fn, start_time = 0, duration = None): #load a bag file
		super(readRosBag, self).loadBagFile(fn, start_time, duration)
		self.bag_gen = self.bag.read_messages() # need to start from beginning of bag file -- lose a message when loading

	def loadAllMessages(self):
		# loads all the messages in the file
		self.data = []
		empty_dict = dict.fromkeys(['topic', 'msg', 't'])
		for topic, msg, t in self.bag_gen:
			msg_dict = copy.deepcopy(empty_dict)
			msg_dict['topic'] = topic
			msg_dict['msg'] = msg
			msg_dict['t'] = t
			self.data.append(msg_dict)

	def getIndices(self):
		# gets the indices for each message
		self.idx_arm_ja =  self.getIdx('/wam/joint_states')
		self.idx_hand_ja =  self.getIdx('/bhand/joint_states')
		self.idx_depth =  self.getIdx('/camera1/depth/points')
		self.idx_rgb =  self.getIdx('/camera1/rgb/image_raw/compressed')

	def getIdx(self, topic):
		# returns the index of a certain topic in list
		idx = [i for i,d in enumerate(self.data) if d['topic']==topic][0]
		return idx

	def createDictionary(self):
		# builds a dictionary that has the same format as readTextCapturedGrasps
		self.joint_angles = [dict.fromkeys(FIELDNAMES)]
		self.joint_angles[0][FIELDNAMES[0]] = list(self.data[self.idx_arm_ja]['msg'].position)
		self.joint_angles[0][FIELDNAMES[1]] = list(self.data[self.idx_hand_ja]['msg'].position)

	def getRGB(self):
		bridge = CvBridge()
		self.rgb = cv_image1 = bridge.compressed_imgmsg_to_cv2(self.data[self.idx_rgb]['msg'], "bgr8")

	def showRGB(self):
		imgplot = plt.imshow(self.rgb)
		plt.ion()
		plt.show()

	def getXYZRGB(self):
		self.xyzrgb = np.array(self.pc2ToXYZRGB(self.data[self.idx_depth]['msg']))

	def showPC(self, pc, n =100):
		# plot the point cloud in matplotlib
		fig = plt.figure()
		ax = fig.add_subplot(111, projection='3d')
			# ax.scatter(xs, ys, zs, c=c, marker=m)
		ax.scatter(pc[::n,0], pc[::n,1], pc[::n,2], c=pc[::n, 3:])
		ax.set_xlabel('X Label')
		ax.set_ylabel('Y Label')
		ax.set_zlabel('Z Label')
		plt.ion()
		plt.show()

	def showPlot(self):
		plt.show()

class readRosBags(object):
	# reads multiple bag files in and stores data
	def __init__(self, fns):
		self.data = []
		for fn in fns:
			self.data.append(readRosBag(fn))
		self.getJAsFromExtractedMsgs()

	def getJAsFromExtractedMsgs(self):
		#extracts the joint angles from each grasp capture and sets as an array
		self.joint_angles = []
		for d in self.data:
			self.joint_angles.append(d.joint_angles[0])

class readTextCapturedGrasps(object):
	# This just takes the input from the command line for captured grasps and turns it into a dict for easier use
	def __init__(self):
		self.FIELDNAMES = FIELDNAMES
		self.joint_angles = self.importWineGlassInterpDict()

	def importWineGlassInterpDict(self, FILENAME='INTDATA'):
		OUTNAME = 'WineGlassInterpGrasps_dict.csv'
		with open(FILENAME, 'rb')  as fn:
			all_text = fn.readlines()
			arm_idx = [i+1 for i,ln in enumerate(all_text) if 'Arm Joints' in ln]
			hand_idx = [i+1 for i,ln in enumerate(all_text) if 'Hand Joints' in ln]
			grasp_count = len(arm_idx)

			joint_angles = [dict.fromkeys(self.FIELDNAMES) for i in range(grasp_count)]
			for i in range(grasp_count):
				joint_angles[i][self.FIELDNAMES[0]] = self.convertText2Array(all_text[arm_idx[i]])
				joint_angles[i][self.FIELDNAMES[1]] = self.convertText2Array(all_text[hand_idx[i]])

		return joint_angles

	def convertText2Array(self, txt):
		return np.array(txt.strip('(').strip('\n').strip(')').split(',')).astype(float)


		# with open(OUTNAME, 'wb') as dictfile:
		# 	writer = csv.DictWriter(dictfile, fieldnames = FIELDNAMES)
		# 	writer.writeheader()
		# 	for i in range(grasp_count):
		# 		writer.writerow(joint_angles[i])

		# test to see if you can load the file -- too much work. just load it and use that dict
		# joint_angles = []
		# with open(OUTNAME, 'rb') as dictfile:
		# 	reader = csv.DictReader(dictfile)
		# 	for row in reader:
		# 		# pdb.set_trace()
		# 		print(row)
		# 		joint_angles.append(row)
		# pdb.set_trace()
		# print(joint_angles)

class WineGlassInterpData(object):
	def __init__(self, fns = None):
		# change the object that is getting the data
		# self.data = readTextCapturedGrasps()
		self.data = readRosBags(fns)
		self.object_transforms = object_transforms

	def getArmArray(self, i):
		# returns a single array with all the joints that can be passed to OpenRave Object
		JA = np.array([self.data.joint_angles[i][FIELDNAMES[0]], self.data.joint_angles[i][FIELDNAMES[1]]]).flatten()
		return JA

class InterpHandPositions(object):
	def __init__(self, W):
		self.V = Vis()
		self.A = ArmVis(self.V)
		self.W = W
		self.A.loadArm()
		self.O = ObjectVis(self.V)
		self.O.loadObject(4) #loads wineglass
		self.G = AddGroundPlane(self.V)
		self.G.createGroundPlane(y_height=0.5, x=0.65, y=0.51, z=0, x_pos=0, z_pos=0.04)
		self.H = None

	def showGrasp(self, i):
		# loads a grasp from the file and displays in OpenRave
		JA_robot = self.W.getArmArray(i)
		JA_openrave = self.A.convertRobot2OpenRAVE(JA_robot)
		self.A.setJointAngles(JA_openrave)
		print('Grasp %s' %i)

	def swapIndices(self, arr, i1, i2):
		# swap two indexes in array -- assumes they are values and not arrays which will just move the pointers and not be what you want (i don't think)
		a,b = arr[i1], arr[i2]
		arr[i1], arr[i2] = b,a
		return arr

	def tryIndices(self):
		# trying to figure out which indices are being mapped incorrectly
		for i1 in range(-1,-9,-1):
			for i2 in range(-1,-9,-1):
				JA_robot = self.W.getArmArray(0)
				JA_openrave = self.A.convertRobot2OpenRAVE(JA_robot)
				JA_openrave = self.swapIndices(JA_openrave, i1, i2)
				print('Swapping %s for %s' %(i1, i2))
				self.A.setJointAngles(JA_openrave)
				time.sleep(1)

	def alignObjectToTable(self):
		# roughly know where on the table the object should be
		table_ctr = self.G.groundPlane.GetTransform()
		self.O.globalTransformation(table_ctr)
		self.O.globalTransformation(self.O.GetCentroidTransform())

	def alignToObject(self):
		palm_base = self.A.obj.GetLink('wam/bhand/bhand_palm_surface_link')
		palm_pt = palm_base.GetTransform()[:3,3] 
		self.O.globalTransformation(palm_base.GetTransform())
		self.O.globalTransformation(self.O.GetCentroidTransform())

	def alignToManualTransform(self, T):
		# name is the name of the grasp
		# maybe think of a better way to store data?
		# write object transform to bag file?
		self.O.globalTransformation(T)

	def manuallyAlignObject(self, grasp_name=None):
		# allows the user to align the object with OR utilities
		# outputs the final transformation to the terminal?
		# save to file so it can be loaded when loading grasps
		pdb.set_trace()
		if grasp_name is None:
			self.alignToObject()
		else:
			self.alignToManualTransform(object_transforms[name])
		
		pdb.set_trace()
		raw_input("Align object with OR utilities into Hand.  Then hit enter to adjust grasp and display final values.")
		pdb.set_trace()
		# record object position
		#load a hand
		# align it to the current hand position
		# use the find valid grasp
		# use IK to find solution for valid grasp
		# record final joint angles

	def recordObjectPosition(self):
		# record object position
		print(self.O.obj.GetTransform())

	#### NEXT STEPS

	# initialize hand where the current hand is
	def initializeNewHand(self, return_hand=False):
		H = HandVis(self.V)
		H.loadHand()
		H.show()
		H.globalTransformation(self.A.getEETransform())
		H.setJointAngles(self.A.getJointAngles()[-10:])
		if return_hand is False:
			if self.H is not None: # in case another hand is present so it doesn't get abandoned
				self.H.remove()
			self.H = H
		else:
			return H

	# run the find good grasp nearby -- doesn't work when fingers inside of object
	def moveToMakeValidGrasp(self):
		self.H.moveToMakeValidGrasp(self.O.obj)

	# move the arm fingers to that position
	def moveArmFingersToPosition(self, hand):
		i = 1


	def manuallyMarkSLERPCenter(self):
		self.markPoint([1,1,1])
		# make other bodies lighter color and not moveable?
		raw_input('Move point to location that hand positions should be interpolated around.  Press Enter to show location.')
		print(self.center_pt.GetTransform().round(4))

	def markPoint(self, pt):
		self.center_pt = openravepy.RaveCreateKinBody(self.V.env,'')
		self.center_pt.SetName('CenterPoint')
		self.center_pt.InitFromSpheres(np.array([[0,0,0,0.01]]))
		T_orig = np.eye(4); T_orig[0:3,3] = pt
		self.center_pt.SetTransform(T_orig)
		self.V.env.Add(self.center_pt, True)

	def inFrameA(self, frameA, pose):
		# gives the pose relateive to frameA
		pose_A = np.matmul(np.linalg.inv(frameA), pose)
		return pose_A

	def loadHandWithGrasp(self, grasp):
		# show hands associated with grasp
		self.showGrasp(grasp)
		return self.initializeNewHand(return_hand = True)

	def interpolateBetweenGrasps(self, H1_global, H2_global, center_pt_T, prcnt):
		# # transform pose into center point reference frame
		H1_local = np.matmul(np.linalg.inv(center_pt_T), H1_global)
		H2_local = np.matmul(np.linalg.inv(center_pt_T), H2_global)
		center_pt_local = np.eye(4)

		# # build circle
		v_c_1 = H1_local[0:3,3] - center_pt_local[0:3,3]
		v_c_2 = H2_local[0:3,3] - center_pt_local[0:3,3]
		u_v_c_1 = v_c_1/np.linalg.norm(v_c_1)
		u_v_c_2 = v_c_2/np.linalg.norm(v_c_2)
		r1 = np.sqrt(np.matmul(v_c_1, v_c_1))
		r2 = np.sqrt(np.matmul(v_c_2, v_c_2))
		theta = np.arccos(np.dot(u_v_c_1, u_v_c_2) / (np.linalg.norm(u_v_c_1)*np.linalg.norm(u_v_c_2)))

		# # build the plane
		plane_normal = np.cross(v_c_1, v_c_2)
		# # determine adaptive radius
		r = (1-prcnt)*r1+prcnt*r2

		interp_pos = center_pt_local[0:3,3] + r*np.cos(prcnt*theta)*u_v_c_1 + r*np.sin(prcnt*theta)*u_v_c_2
		Q1 = pyquaternion.Quaternion(matrix = H1_local)
		Q2 = pyquaternion.Quaternion(matrix = H2_local)
		Qi = pyquaternion.Quaternion.slerp(Q1, Q2, prcnt*theta)

		T_mvd = np.matmul(UtilTransforms.TL2T(interp_pos), UtilTransforms.Q2T(Qi))
		T_world = np.matmul(center_pt_T, T_mvd)

		return T_world

	def loadORArm(self):
		self.A_OR = ArmVis_OR(self.V)
		self.A_OR.loadArm()
		self.A_OR.loadIK()

	def showSolutions(self, goalT, bitmask=0):
		# bitmask defines which settings to use
		# each bit (1,2,4,8...) will turn a setting on and off
		sols = self.A_OR.ikmodel.manip.FindIKSolutions(goalT, bitmask)
		pdb.set_trace()
		for sol in sols:
			self.A_OR.setJointAngles(sol)
			time.sleep(0.1)


	def showAllSolutions(self, goalT):
		for i in range(32):
			self.showSolutions(goalT, bitmask = i)

	def interpolateHandPositions(self, grasp1, grasp2, prcnt = 0.5):
		# interpolate current hand location
		# grasp 1 is 0 interpolation
		# grasp 2 is 1 interpolation
		# prcnt is between 0 and 1 and defines how much interpolation
		# # initialize hands
		self.H1 = self.loadHandWithGrasp(grasp1)
		self.H2 = self.loadHandWithGrasp(grasp2)
		
		# # need a center position
		self.markPoint(SLERP_center['grasp2'][0:3,3])

		T_world = self.interpolateBetweenGrasps(self.H1.obj.GetTransform(), self.H2.obj.GetTransform(), self.center_pt.GetTransform(), prcnt)
		self.initializeNewHand()
		self.H.obj.SetTransform(T_world)
		self.H.changeColor([0,1,1])

		# # extract palm position (or whatever IK needs)
		self.loadORArm()
		# array([[-1.   , -0.003,  0.003,  0.004],
  #      [ 0.003, -1.   , -0.   , -0.009],
  #      [ 0.003, -0.   ,  1.   , -0.156],
  #      [ 0.   ,  0.   ,  0.   ,  1.   ]])
		# need to fix some parameter here to find solutions
		self.IK()
		pdb.set_trace()
		i = 1

	def IK(self):
  		pdb.set_trace()
  		RotX = UtilTransforms.RotX(np.pi/2)
  		T_updated = np.matmul(self.H.getGlobalTransformation(), np.matmul(self.A_OR.obj.GetManipulators()[0].GetLocalToolTransform(), RotX))

		self.showSolutions(T_updated)

	# # solve for IK positions
	def moveArmEEToPosition(self,pose):
		i =1

	# # Generate trajectories the way WAMPy does?
	def armTrajectory(self, start_pose, end_pose):
		i=1
		

## just try collecting data again

# alternative strategy
# align object with each grasp manually
# extract a relative pose to the object and then put the hands in the same frame
# then run slerp
# then use IK to get joint angles -- given the variation, what is the guarantee that this will work?
# run that on the real robot





if __name__ == '__main__':
	I = InterpHandPositions()
	# for i in range(len(I.W.joint_angles)):
	# 	I.loadGrasp(i)
	I.loadGrasp(1)
	I.manuallyAlignObject()
	pdb.set_trace()