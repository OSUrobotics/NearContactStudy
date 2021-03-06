import cv2
import os, pdb, copy, time, sys, csv, shutil
import numpy as np
import rosbag
import sensor_msgs.point_cloud2
curdir = os.path.dirname(os.path.realpath(__file__))
classdir = curdir +'/../InterpolateGrasps/'
sys.path.insert(0, classdir) # path to helper classes
from Visualizers import Vis, ArmVis
from cv_bridge import CvBridge, CvBridgeError
import struct, ctypes
import pcl.registration, pcl

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

	def setJA(self, JA): self.arm.setJointAngles(JA) # set joint angles of arm
		
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

	def AllPoses(self, save_poses = False, dir_name = None, align_pc = False): #read a message, display pose, and write to file
		print('Showing All Poses from Robot in openRAVE')
		save_time_interval = 0.1 # amount of time between saved stls

		# some directory checking for file creation
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
		#read all messages
		#if there is a timestamp with enough information, show the pose
		# if there is a timestamp with enough information, save the pointcloud data from that timestep
		bridge = CvBridge()
		last_save_time = 0
		for topic, msg, t in self.bag_gen:
			self.parseData(topic,msg,t) #adds message to all_data with topic as key

			if '/wam/joint_states' in self.all_data[-1].keys() and '/bhand/joint_states' in self.all_data[-1].keys():
				# pdb.set_trace()
				# if the necessary data is in the last entry of list to show a pose
				JA = self.robotStateToArray(self.all_data[-1]['/wam/joint_states'], self.all_data[-1]['/bhand/joint_states'])
				# pdb.set_trace()
				self.setJA(JA)
				print('Pose at time: %s' %self.all_data[-1]['time'])
				time.sleep(0.01)
				if save_poses:
					if '/camera1/depth/points' in self.all_data[-1].keys() \
					and '/camera1/rgb/image_raw/compressed' in self.all_data[-1].keys() \
					and '/camera2/depth/points' in self.all_data[-1].keys() \
					and '/camera2/rgb/image_raw/compressed' in self.all_data[-1].keys() \
					and abs(self.all_data[-1]['time'] - last_save_time) > save_time_interval:
					# if '/kinect2/hd/points' in self.all_data[-1].keys() and '/camera/depth/points' in self.all_data[-1].keys():
						
						camera1_pts = self.pc2ToXYZRGB(self.all_data[-1]['/camera1/depth/points'])
						camera2_pts = self.pc2ToXYZRGB(self.all_data[-1]['/camera2/depth/points'])
						# camera1_pts = self.pc2ToXYZ(self.all_data[-1]['/camera1/depth/points'])
						# camera2_pts = self.pc2ToXYZ(self.all_data[-1]['/camera2/depth/points'])
						self.showPointCloud(camera1_pts)
						self.showPointCloud(camera2_pts)
						# pdb.set_trace()
						
						# saving image from camera -- should check this at the if statement...
						try:
							cv_image1 = bridge.compressed_imgmsg_to_cv2(self.all_data[-1]['/camera1/rgb/image_raw/compressed'], "bgr8")
							cv_image2 = bridge.compressed_imgmsg_to_cv2(self.all_data[-1]['/camera2/rgb/image_raw/compressed'], "bgr8")
						except CvBridgeError, e:
							print e
						
						# save point clouds
						camera_pts = [camera1_pts, camera2_pts]
						# camera_pts = [camera1_pts]
						camera_filename = ['%s/frame%s_pc%s.csv' %(dir_name,self.frame_count,ci) for ci in range(len(camera_pts))]
						for i in range(len(camera_pts)): # won't work with only one camera
							with open(camera_filename[i], 'wb') as f:
								cam_writer = csv.writer(f, delimiter = ',')
								for pt in camera_pts[i]:
									cam_writer.writerow(pt)
							print("CSV File Created: %s" %camera_filename[i])

						# save STL
						self.arm.generateSTL('%s/frame%s.stl' %(dir_name, self.frame_count))

						# save image
						cv2.imwrite('%s/frame%s_camera%s.png' %(dir_name, self.frame_count, 1), cv_image1)
						cv2.imwrite('%s/frame%s_camera%s.png' %(dir_name, self.frame_count, 2), cv_image2)

						self.frame_count += 1
						last_save_time = self.all_data[-1]['time']

				if align_pc:
					# check if data is there
					if '/camera1/depth/points' in self.all_data[-1].keys() \
					and '/camera2/depth/points' in self.all_data[-1].keys() :
						# get mesh from STL
						self.arm.getSTLFeatures()

						# convert to proper format
						pcarm = pcl.PointCloud()
						pcarm.from_list(self.arm.all_vertices)

						# get data
						camera1_pts = np.array(self.pc2ToXYZRGB(self.all_data[-1]['/camera1/depth/points']))
						camera2_pts = np.array(self.pc2ToXYZRGB(self.all_data[-1]['/camera2/depth/points']))

						# convert to proper format
						pc1 = pcl.PointCloud()
						pc2 = pcl.PointCloud()
						# seperate from colors
						pc1.from_list(camera1_pts[:,0:3]) 
						pc2.from_list(camera2_pts[:,0:3])
						pdb.set_trace()
						if pc1.size == 0 and pc2.size == 0:
							print('No Points to align')
						elif pc1.size != 0 and pc2.size ==0:
							print("Aligning PC1 with arm")
							icp_success1, pc1_T, pc1_transfomed, fitness1 = pcl.registration.icp_nl(source = pc1, target = pcarm, max_iter = None)
							pc1_transformed_list = np.hstack((pc1_transformed.to_list(), camera1_pts[:,3:])) # reassemble with colors
							self.showPointCloud(pc1_transformed_list)

						elif pc1.size == 0 and pc2.size != 0:
							print("Aligning PC2 with arm")
							icp_success2, pc2_T, pc2_transformed, fitness2 = pcl.registration.icp_nl(source = pc2, target = pcarm, max_iter = None)
							pc2_transformed_list = np.hstack((pc2_transformed.to_list(), camera2_pts[:,3:])) # reassemble with colors
							self.showPointCloud(pc2_transformed_list)

						elif pc1.size != 0 and pc2.size != 0:
							print("Aligning PC1 to PC2")  # align point clouds to other point cloud
							icp_success12, pc12_T, pc12_transfomed, fitness12 = pcl.registration.icp_nl(source = pc1, target = pc2, max_iter = None)
							pc12_transformed_list = np.hstack((pc12_transformed.to_list(), camera1_pts[:,3:])) # reassemble with colors
							self.showPointCloud(pc12_transformed_list)

						else:
							print("Should not be here...")

			for idx, frame in enumerate(self.all_data):
				if frame['time'] < self.all_data[-1]['time']: #if entry time is less than current time, pop
					self.all_data.pop(idx)
					print('List Entry Popped')

	def writeAllPosesToFile(self, dir_name, save_poses = False): self.AllPoses(dir_name = dir_name, save_poses = save_poses) # saves all poses in a bag file

	def viewAlignAllposes(self): self.AllPoses(align_pc = True) #view point clouds aligned to arm

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

	def parseData(self, topic, msg, t): # adds a message from a bag file to a list of messages
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
		for val in pt:
			print("x: %s, y: %s, z: %s" %(val[0], val[1], val[2]))
		return pt

	def pc2ToXYZRGB(self, msg): # convert pointcloud2 message into a set of points with color
		xyzrgb = list()
		for point in sensor_msgs.point_cloud2.read_points(msg, skip_nans = True, field_names=("x", "y", "z", "rgb")):
			# pdb.set_trace()
			if np.linalg.norm(point[:3]) < 1e-10: # if the point is close to zero, don't bother processing
				continue
			if np.linalg.norm(point[:3]) > 10: # if the point is too far away don't worry about it
				continue
			# converts rgb color from 24bit integer to seperate values
			RGBint = point[3]
			# found conversion at:
			# http://answers.ros.org/question/208834/read-colours-from-a-pointcloud2-python/
			# cast float32 to int so that bitwise operations are possible
			s = struct.pack('>f', RGBint)
			i = struct.unpack('>l', s)[0]
			# you can get back the float value by the inverse operations
			pack = ctypes.c_uint32(i).value
			r = (pack & 0x00FF0000)>> 16
			g = (pack & 0x0000FF00)>> 8
			b = (pack & 0x000000FF)
			# print r,g,b # prints r,g,b values in the 0-255 range
			# print("x: %s, y: %s, z: %s, r: %s, g: %s, b: %s" %(point[0], point[1], point[2], r,g, b))
			xyzrgb.append([point[0], point[1], point[2], r/255.0, g/255.0, b/255.0])
		return(xyzrgb)
		
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
		openRave_hand_JA = np.zeros(10)
		# set finger spread - coupled so they are set to the same values
		openRave_hand_JA[2] = hand_JA[3] # Finger-1 Rotation
		openRave_hand_JA[5] = hand_JA[3] # Finger-2 Rotation

		openRave_hand_JA[3] = hand_JA[0] # Finger-1 Base
		openRave_hand_JA[6] = hand_JA[1] # Finger-2 Base
		openRave_hand_JA[8] = hand_JA[2] # Finger-3 Base

		openRave_hand_JA[4] = hand_JA[4] # Finger-1 Tip
		openRave_hand_JA[7] = hand_JA[5] # Finger-2 Tip
		openRave_hand_JA[9] = hand_JA[6] # Finger-3 Tip

		JA[7:] = openRave_hand_JA
		return JA

	def showPointCloud(self,xyzrgb):  # shows point cloud from list of points
		self.vis.clearPoints()
		if len(xyzrgb) == 0: # check if array has any values
			print("Empty Array")
			return
		if len(xyzrgb[0]) == 6: # with color
			[self.vis.drawPoints(pt[0:3], c = pt[3:]) for pt in xyzrgb[::10]] #this will likely crash openRAVE
		elif len(xyzrgb[0]) == 3: #without color
			[self.vis.drawPoints(pt[0:3]) for pt in xyzrgb[::100]] #this will likely crash openRAVE
		else:
			print("Input array has incorrect dimension")


if __name__ == '__main__':
	# B = BagReader('DataCollectionTest/DataCollectionTest2', 20, 10)
	# B = BagReader('DataCollectionTest/DataCollectionTest_realsenseOnly', 20, 30)
	# B = BagReader('DataCollectionTest/DataCollectionTest_2cam', 10, 30)
	B = BagReader('DataCollectionTest/DataCollectionTest2_2cam')

	
	# topic, msg, t = B.readNextMsg()
	# B.parseAllData()
	B.createEnv()
	# for idx, frame in enumerate(B.all_data):
	# 	pdb.set_trace()
	# 	B.createSTL(frame['/wam/joint_states'], frame['/bhand/joint_states'], "frame%s" %idx)
	# B.viewAllPoses()
	# B.writeAllPosesToFile('test1')
	# B.writeAllPosesToFile('test3_2RealSense', save_poses = True)
	# B.writeAllPosesToFile('test4_2RealSense', save_poses = True)
	B.viewAlignAllposes()

	pdb.set_trace()
	B.closeBag()
