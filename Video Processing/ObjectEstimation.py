import cv2
import os, pdb, copy, time, sys, csv, shutil
import numpy as np
import rosbag
import sensor_msgs.point_cloud2
curdir = os.path.dirname(os.path.realpath(__file__))
classdir = curdir +'/../Interpolate Grasps/'
sys.path.insert(0, classdir) # path to helper classes
from Visualizers import Vis, ArmVis

class BagReader(object):
	# Do general bag operations
	def __init__(self, fn, start_time = 0, duration = None):
		self.bagFileNameCheck(fn)
		self.bag = self.loadBag()
		self.bag_gen = self.bag.read_messages() # generator of each time step in bag file
		self.all_data = list() # list of dicts for each frame by time?
		self.frame_exists_count = 0
		topic, msg, t = self.readNextMsg()
		self.start_time = copy.deepcopy(t)
		self.start_time.secs += start_time # change start time of reading
		self.end_time = None
		self.frame_count = 0

		if duration is not None: #limiting section of bag file to read
			self.end_time = copy.deepcopy(self.start_time)
			self.end_time.secs += duration

		self.bag_gen = self.bag.read_messages(start_time = self.start_time, end_time = self.end_time)

	def createEnv(self): # create scene and arm to it
		self.vis = Vis()
		self.arm = ArmVis(self.vis)
		self.arm.loadArm()
		self.cameraT = np.array([[-0.21123264, -0.25296545,  0.94413413, -2.66172409],
       [-0.96114868,  0.22935609, -0.15358708,  0.70581472],
       [-0.17769068, -0.93989588, -0.2915849 ,  1.37028074],
       [ 0.        ,  0.        ,  0.        ,  1.        ]])
		self.vis.viewer.SetCamera(self.cameraT)

	def setJA(self, JA): # set joint angles of arm
		self.arm.setJointAngles(JA)

	def loadBag(self): # load bag file into object
		# does some error correction
		try:
			b = rosbag.Bag(self.fn, "r")
		except rosbag.bag.ROSBagUnindexedException:
			print "unindexed bag... Trying to reindex."
			os.system("rosbag reindex " + self.fn)
			try:
				b = rosbag.Bag(self.fn, "r")
			except:
				print "Could not reindex and open "
				raise IOError
		print("Bag File Loaded")
		return b

	def bagFileNameCheck(self, fn): # check file name
		if '.bag' not in fn:
			fn += '.bag' # add .bag if it isn't in the file name?  I suppose you could have a file that doesn't end in bag but that seems confusing
		self.fn = fn

	def readNextMsg(self): # read one message from bag file
		try:
			topic, msg, t = next(self.bag_gen)
			# print("Topic: %s" %topic)
			return topic, msg, t
		except:
			print("There was an error")
			pdb.set_trace()

	def viewAllPoses(self, save_poses = False, dir_name = None): #read a message, display pose
		print('Showing All Poses from Robot in openRAVE')
		if save_poses:
			if dir_name is not None:
				try:
					shutil.rmtree(dir_name)
					print("Folder Exists.  Deleting Folder")
				except:
					print("Folder Did not Exist")
				os.mkdir(dir_name, 0777)
			else:
				print("no directory name")
				return
		for topic, msg, t in self.bag_gen:
			self.parseData(topic,msg,t)

			if '/wam/joint_states' in self.all_data[-1].keys() and '/bhand/joint_states' in self.all_data[-1].keys():
				# pdb.set_trace()
				# if the necessary data is in the last entry of list to show a pose
				JA = self.robotStateToArray(self.all_data[-1]['/wam/joint_states'], self.all_data[-1]['/bhand/joint_states'])
				self.setJA(JA)
				print('Pose at time: %s' %self.all_data[-1]['time'])
				time.sleep(0.01)
				if save_poses:
					if '/kinect2/hd/points' in self.all_data[-1].keys() and '/camera/depth/points' in self.all_data[-1].keys():
						camera1_pts = self.pc2ToXYZ(self.all_data[-1]['/camera/depth/points'])
						camera2_pts = self.pc2ToXYZ(self.all_data[-1]['/kinect2/hd/points'])
						# self.showPointCloud(self.all_data[-1]['/camera/depth/points'])
						
						# save point clouds
						camera_pts = [camera1_pts, camera2_pts]
						camera_filename = ['%s/frame%s_pc%s.csv' %(dir_name,self.frame_count,ci) for ci in range(len(camera_pts))]
						for i in range(2):
							with open(camera_filename[i], 'wb') as f:
								cam_writer = csv.writer(f, delimiter = ',')
								for pt in camera_pts[i]:
									cam_writer.writerow(pt)
							print("CSV File Created")

						# save STL
						self.arm.generateSTL('%s/frame%s.stl' %(dir_name, self.frame_count))


						self.frame_count += 1

			for idx, frame in enumerate(self.all_data):
				if frame['time'] < self.all_data[-1]['time']: #if entry time is less than current time, pop
					self.all_data.pop(idx)
					print('List Entry Popped')

	def writeAllPosesToFile(self, dir_name):
		self.viewAllPoses(dir_name = dir_name, save_poses = True)


	def parseAllData(self): # get messages from each frame of bag_gen and do any manipulation
		# this method won't work on large segments of bag file.
		# need to read a frame and write to file in a more condensed format
		print('Getting data from Each Frame')
		for topic, msg, t in self.bag_gen:
			self.parseData(topic, msg, t) # add message to list

		# clean list. Remove entries that only have a time stamp
		print('Converting messages and taking only interesting values')
		i = 0
		total_length = len(self.all_data)
		for frame in self.all_data:
			if i % 10 == 0: #status updater
				print("Complete: %.2f%%" %(float(i)*100/total_length))
			if frame.keys() == ['time']:
				self.all_data.pop(i)
			if '/camera/depth/points' in frame.keys():   # convert pointcloud to xyz points
				self.all_data[i]['/camera/depth/points'] = self.pc2ToXYZ(self.all_data[i]['/camera/depth/points'])
			if '/kinect2/hd/points' in frame.keys(): # convert pointcloud to xyz points
				self.all_data[i]['/kinect2/hd/points'] = self.pc2ToXYZ(self.all_data[i]['/kinect2/hd/points'])
			if '/wam/joint_states' in frame.keys():  # extract only joint states JointState message
				self.all_data[i]['/wam/joint_states'] = self.all_data[i]['/wam/joint_states'].position
			if '/wam/pose' in frame.keys():  # extract endpoint location and orientation from PoseStamped message
				self.all_data[i]['/wam/pose'] = self.poseToList(self.all_data[i]['/wam/pose'])
			if '/bhand/joint_states' in frame.keys():  # extract hand joint states from JointState message
				self.all_data[i]['/bhand/joint_states'] = frame['/bhand/joint_states'].position
			i += 1

	#TODO: show frames of 3d point cloud

	def parseData(self, topic, msg, t):
		if len(self.all_data) == 0: #first message
			self.addNewTimeStamp(t) # check if time in list
		'''
		TOPICS
		/camera/rgb/image_color
		/kinect2/hd/image_color
		/camera/depth/points
		'''
		ignore_topics = ['/camera/rgb/image_color', '/kinect2/hd/image_color']
		if topic not in ignore_topics: # only record topics we care about
			for time_step in self.all_data: # check all time_steps to see if it exists
				if time_step['time'] == round(t.to_sec(), 1):
					self.addMessage(time_step, topic, msg)
					break
			else:  # if pass through list and nothing, add new message
				self.addMessage(None, topic, msg, t)

	def addNewTimeStamp(self, t): # Create a dict with only a time value
		new_timestamp = dict()
		new_timestamp['time'] = round(t.to_sec(), 1) #extract number from ROS message. without roudning, no timestamp has multiple values
		self.all_data.append(new_timestamp)

	def addMessage(self, list_entry, topic, msg, t = None): # add message to data list
		if t is None:
			list_entry[topic] = msg
		if list_entry is None:
			self.addNewTimeStamp(t)
			self.all_data[-1][topic] = msg #recursively call addMessage here?

	def pc2ToXYZ(self, msg): #converts pointcloud2 message into a set of points -- significant reduction in array size
		pt = [point[0:3] for point in sensor_msgs.point_cloud2.read_points(msg, skip_nans = True)]
		return pt

	def poseToList(self, msg): # converts geometry_msg_PoseStamped to 7 element list of pose [pos, quaternion]
		# list instead of array because it is easier to read/write to csv
		pose = list()
		pose.append(msg.pose.position.x)
		pose.append(msg.pose.position.y)
		pose.append(msg.pose.position.z)
		pose.append(msg.pose.orientation.x)
		pose.append(msg.pose.orientation.y)
		pose.append(msg.pose.orientation.z)
		pose.append(msg.pose.orientation.w)
		return pose

	def JAToList(self, msg): #gets JA from sensor_msgs_JointState
		return msg.position

	def closeBag(self):
		self.bag.close()

	def readAllMsgs(self):
		data_remains = True
		while data_remains:
			try:
				self.readNextMsg()
				time.sleep(1)
			except:
				data_remains = False #break statement?

	def createSTL(self, arm_JA, hand_JA, stl_filename): # create stl file of arm from pose
		pdb.set_trace()
		JA = self.robotStateToArray(arm_JA, hand_JA)
		self.setJA(JA)
		self.arm.generateSTL('%s.stl' %stl_filename)

	def robotStateToArray(self, arm_JA, hand_JA): # convert from bag messages to array to set joint angles in openrave
		# can handle full message or arrays
		if type(arm_JA).__name__ == '_sensor_msgs__JointState':
			arm_JA = self.JAToList(arm_JA)
		if type(hand_JA).__name__ == '_sensor_msgs__JointState':
			hand_JA = self.JAToList(hand_JA)
		JA = np.zeros(17)
		JA[0:7] = arm_JA
		JA[10:] = hand_JA
		return JA

	def showPointCloud(self,point_cloud):  # shows point cloud from message
		# check point_cloud to handle list of points and message
		pts = self.pc2ToXYZ(point_cloud)
		out = [self.vis.drawPoints(pt[0:3]) for pt in pts] #this will likely crash openRAVE





# Description: Class that can parse data from bag file
# seperate out depth cloud data
# create STL file for frame

class DataExtraction(object):
	def __init__(self):
		self.i = 1



if __name__ == '__main__':
	B = BagReader('DataCollectionTest/DataCollectionTest2', 20, 10)
	
	# topic, msg, t = B.readNextMsg()
	# B.parseAllData()
	B.createEnv()
	# for idx, frame in enumerate(B.all_data):
	# 	pdb.set_trace()
	# 	B.createSTL(frame['/wam/joint_states'], frame['/bhand/joint_states'], "frame%s" %idx)
	# B.viewAllPoses()
	B.writeAllPosesToFile('test1')
	pdb.set_trace()
	B.closeBag()
