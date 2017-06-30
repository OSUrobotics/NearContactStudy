import cv2
import os, pdb, copy
import numpy as np

class Compress(object):
	def __init__(self):
		self.i = 1

	## TODO: Compress video
	## TODO: find corners in checkerboard

	def compress(self, fn):
		scale_factor = 0.5
		if not os.path.isfile(fn):
			print('Could not load Video. Not a valid file path')
			return
		self.cap = cv2.VideoCapture(fn)
		count = 0
		while self.cap.isOpened():
			ret, frame = self.cap.read()
			frame_red = cv2.resize(frame, None, fx = scale_factor, fy = scale_factor, interpolation = cv2.INTER_AREA)
			cv2.imshow('Frame Preview', frame_red)
			if cv2.waitKey(1) & 0xFF == ord('q'):
				break


class Estimation(object):
	def __init__(self):
		self.i = 1

	def viewer(self, fn):
		if not os.path.isfile(fn):
			print('Could not load Video. Not a valid file path')
			return
		self.cap = cv2.VideoCapture(fn)
		count = 0
		while self.cap.isOpened():
			ret, frame = self.cap.read()
			cv2.imshow('Frame Preview', frame)
			if cv2.waitKey(1) & 0xFF == ord('q'):
				break
			if cv2.waitKey(1) & 0xFF == ord('r'):
				print('R Pressed')
				return frame
			if cv2.waitKey(1) & 0xFF == ord('s'):
				print('S Pressed')
				cv2.imwrite('test_image.png', frame)
				return frame

		cv2.destroyAllWindows()

	def loadImage(self, fn):
		frame = cv2.imread(fn)
		return frame

	def showImage(self, frame, frame_title = 'Frame Preview'):
		cv2.namedWindow(frame_title, flags = cv2.WINDOW_NORMAL)
		cv2.imshow(frame_title, frame)
		if cv2.waitKey(0) & 0xFF == ord('q'):
			return
		cv2.destroyAllWindows() # displays image

	def harrisCorners(self, image):
		# convert to gray scale
		grey = self.convertToGray(image)
		# self.showImage(grey, frame_title = 'Grey Scale')
		# grey = np.float32(grey)
		# self.showImage(grey)

		# blur image
		grey_blur = cv2.GaussianBlur(grey, (0, 0), 11) #arbitrarily choose blurring parameter
		# self.showImage(grey_blur, frame_title = 'Blurred Image')

		# find harris corners
		blockSize = 2
		aperatureSize = 21
		k = 0.01
		image_out = cv2.cornerHarris(grey, blockSize, aperatureSize, k)
		# self.showImage(image_out, 'Harris Corners Detected') # very small white dots on black background
		
		# get location of harris corners
		x, y = np.where(image_out >= 0.5 * image_out.max()) # can change threshold if necessary

		# show harris corners on original image
		image_circle = copy.deepcopy(image)
		for i in range(min(len(x), len(y))):
			image_circle = cv2.circle(image_circle, center = (x[i], y[i]), radius = 50, color = [0, 255, 0], thickness  = -1)
		self.showImage(image_circle, frame_title = 'Harris Corners: %s' %i)
		pdb.set_trace()

		image_out = cv2.dilate(image_out, None)
		# self.showImage(image_out, frame_title = 'Dilated Image')

		image_out[image_out>0.5*image_out.max()]=[0,0,255] # threshold for being a corner!
		self.showImage(image_out, frame_title = 'Harris Corners Marked')

	def convertToGray(self, image):
		gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
		return gray

	def calibration(self, image, grid_x = 4, grid_y = 4):

		gray = self.convertToGray(image)
		# for i in range(3,10):
		if grid_x is None or grid_y is None: # try a bunch of grid sizes
			for i in range(4,5):
				print('Trying %s Corners' %i)
				ret, corners = cv2.findChessboardCorners(gray, (i,i), None, flags = cv2.CALIB_CB_ADAPTIVE_THRESH+cv2.CALIB_CB_NORMALIZE_IMAGE+cv2.CALIB_CB_FILTER_QUADS)
				if corners is not None:
					new_gray = copy.deepcopy(gray)
					cv2.drawChessboardCorners(new_gray, (3,3), corners, ret)
					# cv2.imshow('Initial Chessboard',new_gray)
					# if cv2.waitKey(0) & 0xFF == ord('q'):
					# 	continue
		else: # know grid size and just looking for intersections
			ret, corners = cv2.findChessboardCorners(gray, (grid_x, grid_y), None, flags = cv2.CALIB_CB_ADAPTIVE_THRESH+cv2.CALIB_CB_NORMALIZE_IMAGE+cv2.CALIB_CB_FILTER_QUADS)

		# If found, add object points, image points (after refining them)
 		if corners is not None:
 			# make points for each grid location
 			grid_points = [[(x, y, 0) for x in range(grid_x)] for y in range(grid_y)]
 			grid_points = np.array(grid_points).reshape(-1,3)

 			# Arrays to store object points and image points from all the images.
			objpoints = [] # 3d point in real world space
			imgpoints = [] # 2d points in image plane.

			# termination criteria
			criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
			objpoints.append(grid_points)
			cv2.cornerSubPix(gray,corners,(11,11),(-1,-1),criteria)
			imgpoints.append(corners)
			# Draw and display the corners
			pdb.set_trace()
			cv2.drawChessboardCorners(image, (grid_x, grid_y), corners, ret)
			pdb.set_trace()
			self.showImage(image, frame_title = 'Optimized Chessboard')





if __name__ == '__main__':
	fn = ''
	# C = Compress()
	# C.compress('Videos/test2_realsense.avi')
	E = Estimation()
	# frame = E.viewer('Videos/test2_kinect.avi')
	# frame = E.viewer('Videos/test2_realsense.avi')
	# frame = E.loadImage('test_image_kinect.png')
	# frame = E.loadImage('Checkerboard_pattern.png')
	frame = E.loadImage('Colored Checkerboard/CylinderColoredCheckerboard.png') # works with calibration
	# E.calibration(frame, grid_x = 5, grid_y = 7)

	# E.showImage(frame)
	E.harrisCorners(frame)
	pdb.set_trace()



