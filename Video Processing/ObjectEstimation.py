import cv2
import os, pdb, copy, time
import numpy as np
import rosbag
import sensor_msgs.point_cloud2

class BagReader(object):
	# Do general bag operations
	def __init__(self, fn, duration = None):
		self.bagFileNameCheck(fn)
		self.bag = self.loadBag()
		self.bag_gen = self.bag.read_messages() # generator of each time step in bag file
		self.all_data = list() # list of dicts for each frame by time?
		self.frame_exists_count = 0
		topic, msg, t = self.readNextMsg()
		self.start_time = t

		if duration is not None: #limiting section of bag file to read
			self.end_time = copy.deepcopy(self.start_time)
			self.end_time.secs += duration
			self.bag_gen = self.bag.read_messages(start_time = self.start_time, end_time = self.end_time)

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

	def readNextMsg(self):
		try:
			topic, msg, t = next(self.bag_gen)
			# print("Topic: %s" %topic)
			return topic, msg, t
		except:
			print("There was an error")
			pdb.set_trace()


	def parseAllData(self): # get messages from each frame of bag_gen and do any manipulation
		# this method won't work on large segments of bag file.
		# need to read a frame and write to file in a more condensed format
		print('Getting data from Each Frame')
		for topic, msg, t in self.bag_gen:
			self.parseData(topic, msg, t)

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
			self.addNewTimeStamp(t)
		# check if time in list
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
				# 	print('Frame Exists %s \r' %self.frame_exists_count)
				# 	self.frame_exists_count += 1
				# 	if self.frame_exists_count % 100000 == 0:
				# 		pdb.set_trace()
				# 	if topic not in time_step.keys() and topic not in ignore_topics: #check if that message has been saved
				# 		# pdb.set_trace()
				# 		# use ros opencv bridge to create image!
				# 		time_step[topic] = msg # extract important information here

				# else: #if it doesn't exist
				# 	self.addNewTimeStamp(t) # adding time stamp

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
		pt = [point for point in sensor_msgs.point_cloud2.read_points(msg, skip_nans = True)]
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



class STLGenerator(object):
	def __init__(self):
		self.i = 1
		self.arm_path = '../NearContactStudy/Interpolate Grasps/models/robots/barrett_wam.dae'
	# def createArmSTL(self, pose_arm, pose_hand): # create an stl for Barrett arm with hand based on pose





# Description: Class that can parse data from bag file
# seperate out depth cloud data
# create STL file for frame

class DataExtraction(object):
	def __init__(self):
		self.i = 1



if __name__ == '__main__':
	B = BagReader('DataCollectionTest/DataCollectionTest2', 5)
	
	topic, msg, t = B.readNextMsg()
	B.parseAllData()
	pdb.set_trace()

	B.closeBag()
