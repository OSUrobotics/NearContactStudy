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
				print('R Pressed, returning image')
				return frame
			if cv2.waitKey(1) & 0xFF == ord('s'):
				print('S Pressed, saving image')
				cv2.imwrite('test_image.png', frame)
				return frame

		cv2.destroyAllWindows()

	def loadImage(self, fn):
		frame = cv2.imread(fn)
		return frame

	def showImage(self, frame, frame_title = 'Frame Preview', time_open = 0, new_window = True):
		cv2.namedWindow(frame_title, flags = cv2.WINDOW_NORMAL)
		cv2.imshow(frame_title, frame)
		if cv2.waitKey(time_open) & 0xFF == ord('q'):
			return
		if new_window == True:
			cv2.destroyAllWindows() # displays image

	def gridCorners(self, image, showImage = False):
		# convert to gray scale
		grey = self.convertToGray(image)
		# self.showImage(grey, frame_title = 'Grey Scale')
		# grey = np.float32(grey)
		self.showImage(grey)

		# blur image
		# grey_blur = cv2.GaussianBlur(grey, (0, 0), 11) #arbitrarily choose blurring parameter
		# self.showImage(grey_blur, frame_title = 'Blurred Image')

		# find harris corners
		blockSize = 2
		aperatureSize = 11
		k = 0.01
		pdb.set_trace()
		image_out = cv2.cornerHarris(grey, blockSize, aperatureSize, k)
		# self.showImage(image_out, 'Harris Corners Detected') # very small white dots on black background
		
		# get location of harris corners
		x, y = np.where(image_out >= 0.1 * image_out.max()) # can change threshold if necessary

		# remove corners that are sufficiently close
		xy = np.array(zip(x,y))
		xy_trimmed = self.uniquePointsNoOverlap(xy, distance_limit = 20)

		# for the cylinder, 952 pixels = 32.75 mm --> i am not sure what this conversion should be
		# get actual distance between points to do triangle inequality
		xy_pos = xy_trimmed.astype(float) / 3.275 # locations in "image" in pixels

		if showImage:
			self.plotPointsOnImage(image, xy_trimmed)
			pdb.set_trace()

			# image_out = cv2.dilate(image_out, None)
			# self.showImage(image_out, frame_title = 'Dilated Image')

			# image_out[image_out>0.5*image_out.max()]=[0,0,255] # threshold for being a corner!
			# self.showImage(image_out, frame_title = 'Harris Corners Marked')

		return xy_pos

	def uniquePointsNoOverlap(self, xy, distance_limit = 100):
		pop_indxs = np.ones(xy.shape[0], dtype = bool) #keeps which locations are repeats
		for i,p in enumerate(xy[:-1]): #for all points. don't need to check last point
			for ie, pe in enumerate(xy[i+1:], i+1): # for all remaining points in list
				dist = p - pe
				if np.linalg.norm(dist) < distance_limit: # if sufficiently close
					pop_indxs[ie] = False # add point to be removed
			print("Unique Points Percent Complete: %s \r" %(i/float(len(xy)))),
		xy_trimmed = np.array([p for i,p in enumerate(xy) if pop_indxs[i]])
		xy_trimmed = xy_trimmed[xy_trimmed[:,0].argsort()] #sort by first value (x dim in picture)
		return xy_trimmed

	def plotPointsOnImage(self, image, points):
		# show points on original image
		image_circle = copy.deepcopy(image)
		for i in range(len(points)):
			image_circle = cv2.circle(image_circle, center = (points[i,0], points[i,1]), radius = 10, color = [0, 255, 0], thickness  = -1)
			self.showImage(image_circle, frame_title = 'Harris Corners:', time_open = 100, new_window = False)
		self.showImage(image_circle, frame_title = 'Harris Corners: %s' %i)


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

	def cannyEdgeDetection(self, frame, showImage = False): # canny edge to a an image
		edges = cv2.Canny(frame,200,300)
		if showImage:
			self.showImage(edges, frame_title = 'Edge Image')
		return edges

	def cannyEdgeDetectionTest(self, frame, showImage = False): # test various values of canny edge detector
		# detection limits may have to be different for different locations or image sources
		for i in range(400):
			edges = cv2.Canny(frame,i + 100,i + 200)
			self.showImage(edges, frame_title = 'Edge Image', time_open = 100, new_window = False)






if __name__ == '__main__':
	fn = ''
	# C = Compress()
	# C.compress('Videos/test2_realsense.avi')
	E = Estimation()
	# frame = E.viewer('Videos/test2_kinect.avi')
	# frame = E.viewer('Videos/test2_realsense.avi')
	# frame = E.loadImage('test_image_kinect.png')
	# frame = E.loadImage('Checkerboard_pattern.png')
	# frame = E.loadImage('Colored Checkerboard/CylinderColoredCheckerboard.png') # works with calibration
	# frame = E.loadImage('ColoredCheckerboard.png')
	frame = E.loadImage('test_image_kinect.png')
	# frame = E.loadImage('test_image_realsense.png')

	# E.calibration(frame, grid_x = 5, grid_y = 7)

	# E.showImage(frame)
	E.cannyEdgeDetectionTest(frame, showImage = True)
	# E.gridCorners(frame, showImage = True)
	pdb.set_trace()



