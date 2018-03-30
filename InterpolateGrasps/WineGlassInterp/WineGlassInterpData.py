import pdb
import numpy as np
import csv, time
import rosbag
import copy


from NearContactStudy import Vis, ArmVis, ObjectVis, AddGroundPlane
from NearContactStudy import BagReader


from cv_bridge import CvBridge, CvBridgeError
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

object_transform = {'grasp1': np.array([[-0.940495    0.06519729  0.33349432  0.00246401]
										 [ 0.33195813 -0.03344439  0.94270105  0.84647357]
										 [ 0.07261507  0.99731178  0.00981151  0.11387653]
										 [ 0.          0.          0.          1.        ]])



					}

'''
from WineGlassInterpData import WineGlassInterpData, readRosBag, InterpHandPositions, readTextCapturedGrasps
import numpy as np
import matplotlib.pyplot as plt
W = WineGlassInterpData(fn='grasp1.bag')
I = InterpHandPositions(W)
W.data.showRGB()
I.loadGrasp(0)
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
	def __init__(self, fn = None):
		# change the object that is getting the data
		# self.data = readTextCapturedGrasps()
		self.data = readRosBag(fn)

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

	def loadGrasp(self, i):
		# loads a grasp from the file and displays in OpenRave
		JA_robot = self.W.getArmArray(i)
		JA_openrave = self.A.convertRobot2OpenRAVE(JA_robot)
		self.A.setJointAngles(JA_openrave)
		print('Grasp %s' %i)
		time.sleep(1)

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

	def manuallyAlignObject(self):
		# allows the user to align the object with OR utilities
		# outputs the final transformation to the terminal?
		# save to file so it can be loaded when loading grasps
		# pdb.set_trace()
		# all_transforms = self.A.obj.GetLinkTransformations()
		# for link in self.A.obj.GetLinks():
		# 	link_pt = link.GetTransform()[:3,3]
		# 	self.V.drawPoints(link_pt)
		pdb.set_trace()
		self.alignToObject()
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
		







if __name__ == '__main__':
	I = InterpHandPositions()
	# for i in range(len(I.W.joint_angles)):
	# 	I.loadGrasp(i)
	I.loadGrasp(1)
	I.manuallyAlignObject()
	pdb.set_trace()