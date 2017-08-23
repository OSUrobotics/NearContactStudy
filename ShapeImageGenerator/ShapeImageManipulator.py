import subprocess, os, pdb, re, copy, sys
import paramiko
from  PIL import Image, ImageDraw
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from multiprocessing import Process, Pool
# sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
from ShapeImageGeneratorTest import ShapeImageGenerator

#Editted: Ammar Kothari -- Last Update: 8/8/17
class ShapeImageManipulator: #manipulate images that have been produced (most likely with ShapeImageGenerator)
	def __init__(self):
		self.i = 1

	def imageTypeCheck(self, image1): # deals with input that is either path to file or object
		if type(image1) is str:
			im = Image.open(image1)
		else:
			im = image1
		return im

	def folderCheck(self, dir_name): # checks if a folder exists.  If it doesn't, makes folders and parent folders
		if not os.path.isdir(dir_name):
			os.makedirs(dir_name)
			print("New Directory Made")

	def combineImagesTopRight(self, image1, image2, percent_image2 = 35): #combine images so that the second one is smaller and in top right corner
		im1 = self.imageTypeCheck(image1)
		im2 = self.imageTypeCheck(image2)

		im_out = im1.copy()
		w,h = im_out.size
		w_out = percent_image2 * w / 100
		h_out = percent_image2 * h / 100

		im2_reduced = self.reduceSize(im2, size = (w_out, h_out))
		# add border to left and bottom
		border_size = 5
		im2_reduced_border = Image.new("RGB", (w_out + border_size, h_out + border_size), color = 'white')
		im2_reduced_border.paste(im2_reduced, (border_size,0))

		im_out.paste(im2_reduced_border, box = (w-w_out-border_size, 0))
		return im_out

	def combineMultipleImages(self, dir_name_in, dir_name_out): # combine multiple images from a directory
		#look through all the files in the directory
		#find matching second camera angle
		# combine images
		# save image

		for files in os.walk(dir_name_in):
			files[2].sort()
			while len(files[2]) > 0: # keep going until list is empty
				im_path = files[2][0]
				# print("Current Image: %s" %im_path)
				if os.path.splitext(im_path)[1] == '.png':
					if 'cam0' in im_path or 'camera' in im_path: #check that camera angles are being considered
						next_camera_angle_name = re.sub('cam0','cam1',im_path) #replace 1 with 2 for camera angle
						im_out = self.combineImagesTopRight(os.path.join(files[0], im_path), os.path.join(files[0], next_camera_angle_name))
						#remove those two files from the list
						# print('Combined: %s, %s' %(im_path, next_camera_angle_name))
						files[2].remove(im_path)
						files[2].remove(next_camera_angle_name)
						save_name = '%s/%s' %(files[0].replace(dir_name_in, dir_name_out, 1), re.sub('_cam\d', '', im_path)) #remove camera angle identifier for save name
						self.saveImage(im_out, save_name)
					elif 'cam1' in im_path: #just keep going look for cam1
						continue
					else:
						files[2].remove(im_path)


	def cropOpenRAVEBoarder(self,image1): # crops image.  image1 is a PIL.Image object
		im1 = self.imageTypeCheck(image1)
		try:
			cur_box = im1.getbbox()
			if cur_box != (0,0,640,480): #should crop images down to desired size if they are larger
				print("Image has been cropped already: %s" %im1.filename)
				return im1
			# crop_box = (30,20,600,420)
			crop_box = (130, 0, 510, 350)
			im1_cropped = im1.crop(crop_box)
		except:
			print("File may be damaged.  Unable to crop file: %s" %(im1.filename))
			return False
		return im1_cropped

	def boundingPixels(self, bbox): #returns a list of pixels along the edge of the bounding box
		pixel_loc = list()
		y = bbox[1]
		for x in xrange(bbox[0], bbox[2] - 1, 1):
			pixel_loc.append([x, y])
		for y in xrange(bbox[1], bbox[3] - 1, 1):
			pixel_loc.append([x, y])

		for x in xrange(bbox[2] - 1, bbox[0], -1):
			pixel_loc.append([x, y])
		for y in xrange(bbox[3] - 1, bbox[1], -1):
			pixel_loc.append([x, y])
		pixel_loc = np.array(pixel_loc).astype(int)
		return pixel_loc

	def bboxToHand(self, im1, crop = False): #crop images so only hand and object remain
		# this depends on the choice of hand color and object color.
		# potentially do some smart sampling, but it is unclear


		image_orig = self.imageTypeCheck(im1)
		print("Current File: %s" %image_orig.filename)
		image_orig.convert("RGB") # occasionally will get RGBA values if not converted
		bbox = image_orig.getbbox()
		pixel_loc = self.boundingPixels(bbox)

		#linear search at middle
		## build line
		# midline = bbox[2:] / 2
		# mid_pixel_loc = list()
		# for x in xrange(midline[0]):
		# 	mid_pixel_loc.append([x, midline[1]])
		# for y in xrange(midline[1]):
		# 	mid_pixel_loc.append([midline[0], y])
		# mid_pixel_loc = np.array(mid_pixel_loc).astype(int)
		search_box = copy.deepcopy(bbox)
		search_pixel = self.boundingPixels([search_box[2] / 2 - 10, search_box[3] / 2 - 10, search_box[2] / 2 + 10, search_box[3] / 2 + 10])
		search_result = self.checkOverCrop(image_orig, search_box)
		pdb.set_trace()



		ground_plane_color = np.array([137, 132, 132])
		obj_color = np.array([238, 183, 4])
		hand_color = np.array([118, 46, 152])
		im = self.imageTypeCheck(image1)
		im_grey = im.convert('L')
		hist = im_grey.histogram()
		indx_sorted = np.argsort(hist)
		data = np.asarray(im)
		data_old = copy.deepcopy(data)
		data.setflags(write = 1) # make image writable
		# pdb.set_trace()
		box_limits = np.array([1000, 1000, 0, 0]) #xmax, xmin, ymax, ymin
		box_bool = [False, False] #track if last point was in box
		for xind in range(data.shape[0]):
			# limit from top side
			for yind in range(data.shape[1]):
				if np.linalg.norm(data[xind, yind] - obj_color) < 50 \
				or np.linalg.norm(data[xind, yind] - hand_color) < 50:
					# update limits
					if yind < box_limits[1]:
						box_limits[1] = yind
					elif yind > box_limits[3]:
						box_limits[3] = yind

					if xind < box_limits[0]:
						box_limits[0] = xind
					elif xind > box_limits[2]:
						box_limits[2] = xind

					# break
				else: #say that it wasn't in the box
					data[xind, yind] = [0,0,0]
			# # limit from the bottom side
			# for yind in range(data.shape[1]-1, 0, -1):
			# 	if np.linalg.norm(data[xind, yind] - obj_color) < 50 \
			# 	or np.linalg.norm(data[xind, yind] - hand_color) < 50:
			# 		# update limits
			# 		if yind > box_limits[3]:
						
			# 		break
			# 	else: #say that it wasn't in the box
			# 		data[xind, yind] = [0,0,0]

		# crop original image
		# pdb.set_trace()
		box_limits += [-10, -10, 10, 10] # padding around limit
		# box_limits = np.clip(box_limits, [0,0,0,0], [im.size[0],im.size[1],im.size[0],im.size[1]]) #clamp values
		fig, ax = plt.subplots(1)
		ax.imshow(data_old)
		rect = patches.Rectangle((box_limits[0], box_limits[1]), box_limits[2] - box_limits[0], box_limits[3] - box_limits[1], edgecolor = 'r', facecolor = 'none')
		ax.add_patch(rect)
		# plt.imshow(data)
		plt.show()
		pdb.set_trace()
		# pdb.set_trace()
		# # box_limits = np.clip(box_limits, [0, 0, box_limits[0],box_limits[1]], [box_limits[2], box_limits[3], im.size[0], im.size[1]])
		# im_box_limits = copy.deepcopy(box_limits[[1,0,3,2]]) # swap around between matrix and image dimensions
		# im_cropped = im.crop(box_limits)
		# self.previewImage(im_cropped)



				# if np.linalg.norm(data[xind, yind] - ground_plane_color) < 10: #almost the same color
				# 	data[xind, yind] = [0,0,0]
				# elif np.linalg.norm(data[xind, yind] - obj_color) < 50: #almost the same color
				# 	data[xind, yind] = [255,255,255]
				# elif np.linalg.norm(data[xind, yind] - hand_color) < 50: #almost the same color
				# 	data[xind, yind] = [120,120,120]
		plt.imshow(data)
		# plt.plot(hist)


	def previewImage(self, image1): # preview image
		im = self.imageTypeCheck(image1)
		im.show()

	def saveImage(self, image1, fn): #save an image
		im1 = self.imageTypeCheck(image1)
		if not os.path.isdir(os.path.split(fn)[0]): #make a directory if it doesn't exist
			os.makedirs(os.path.split(fn)[0])
		im1.save(fn)

	def closeImage(self,image1):
		image1.close()

	def uploadMultipleImages(self, dir_name): # upload all the files in the folder
		subprocess.Popen(["scp", "-r", dir_name, "%s@%s:%s" %('kotharia', 'shell.onid.oregonstate.edu', 'public_html/')]).wait()
		# requires password
		# images can be found at website: http://people.oregonstate.edu/~kotharia/GeneratedImagesCropped

	def cropAllImages(self, dir_name_in, dir_name_out): # crop all the images in a folder and sub folders
		for files in os.walk(dir_name_in):
			for im_path in files[2]:
				if os.path.splitext(im_path)[1] == '.png':
					image_fn = os.path.join(files[0], im_path)
					image_orig = Image.open(image_fn)
					image_cropped = self.cropOpenRAVEBoarder(image_orig)
					if image_cropped is not False:
						#putting images in the same folder based on source folder structure
						image_cropped_fn = '%s/%s' %(files[0].replace(dir_name_in, dir_name_out, 1), im_path)
						self.folderCheck(os.path.split(image_cropped_fn)[0])
						self.saveImage(image_cropped, image_cropped_fn) #overwrite previous image
						try:
							self.closeImage(image_orig)
							self.closeImage(image_cropped)
						except:
							pass

	def reduceSize(self, image1, size = (128, 128)): # reduce the size of an image
		im = self.imageTypeCheck(image1)
		im_reduced = im.resize(size, resample = Image.NEAREST)
		return im_reduced

	def reduceSizeAllImages(self, dir_name_in, dir_name_out, size = (128, 128)): # reduce the size of all images in a folder and subfolders:
		for files in os.walk(dir_name_in):
			for im_path in files[2]:
				if os.path.splitext(im_path)[1] == '.png':
					image_fn = os.path.join(files[0], im_path)
					image_orig = Image.open(image_fn)
					try:
						image_reduced = self.reduceSize(image_orig, size)
						#putting images in the same folder based on source folder structure
						image_reduced_fn = '%s/%s' %(files[0].replace(dir_name_in, dir_name_out, 1), im_path)
						self.folderCheck(os.path.split(image_reduced_fn)[0])
						self.saveImage(image_reduced, image_reduced_fn) #overwrite previous image
						try:
							self.closeImage(image_orig)
							self.closeImage(image_reduced)
						except:
							pass
					except:
						print("File may be damaged.  Unable to reduce size of file: %s" %(image_orig.filename))

	# def uploadSingleImage(self): #upload images, specific to Ammar's folder
	# 	ssh = paramiko.SSHClient() 
	# 	ssh.load_host_keys(os.path.expanduser(os.path.join("~", ".ssh", "known_hosts")))
	# 	ssh.connect(server, username=username, password=password)
	# 	sftp = ssh.open_sftp()
	# 	sftp.put(localpath, remotepath)
	# 	sftp.close()
	# 	ssh.close()

	def checkOverCropAll(self, dir_name_in): #checks for colors at the border of each image to see if the image was cropped too much
		for files in os.walk(dir_name_in):
			for im_path in files[2]:
				if os.path.splitext(im_path)[1] == '.png':
					self.checkOverCrop(os.path.join(files[0], im_path))
					
	def checkOverCrop(self, im1, bbox = None): # checks for colors at the border of each image to see if hand or object has been cropped
		# could implement a luminescence check as a better/alternate scheme
		# manually set these ranges based on examining images
		hand_color_range = np.array(([255, 205, 50], [134, 103, 0]))
		obj_color_range = np.array(([120, 0, 178], [150, 0, 230]))
		image_orig = self.imageTypeCheck(im1)
		print("Current File: %s" %image_orig.filename)
		image_orig.convert("RGB") # occasionally will get RGBA values if not converted
		if bbox == None: #check the box if given one, otherwise use image size
			bbox = image_orig.getbbox()
		pixel_loc = self.boundingPixels(bbox)
		# pdb.set_trace()
		for pt in pixel_loc:
			try:
				pixel_color = image_orig.getpixel((pt[0], pt[1]))
			except:
				print("Failure: %s,%s" %(pt[0], pt[1]))
			color_range = np.vstack((hand_color_range, obj_color_range))
			diff_color = color_range - pixel_color
			if ((diff_color[0] > 0).all() and (diff_color[1] < 0).all()) or \
				((diff_color[2] > 0).all() and (diff_color[3] < 0).all()):
				print("Overcropping: %s" %image_orig.filename)
				draw = ImageDraw.Draw(image_orig)
				r = 10
				draw.ellipse((pt[0] - r, pt[1] - r, pt[0] + r, pt[1] + r), fill = (255, 0,0))
				image_orig.show()
				return False
		return True #success is getting through all the pixels

	def meanSquaredError(self, im1, im2): #check how similar two images are
		# the 'Mean Squared Error' between the two images is the
		# sum of the squared difference between the two images;
		# NOTE: the two images must have the same dimension
		im1 = np.array(self.imageTypeCheck(im1))
		im2 = np.array(self.imageTypeCheck(im2))
		try:
			err = np.sum((im1.astype("float") - im2.astype("float")) ** 2)
			err /= float(im1.shape[0] * im1.shape[1])
			
			# return the MSE, the lower the error, the more "similar"
			# the two images are
			return err
		except:
			print('Images not the same size')
			return 100000

	def viewImagesSideBySide(self, image_list): # view multiple images in a row
		images = map(Image.open, image_list)
		widths, heights = zip(*(i.size for i in images))  # extract sizes from images
		total_width = sum(widths) # comparison total width
		max_height = max(heights) # comparison total height
		new_im = Image.new('RGB', (total_width, max_height))
		x_offset = 0
		for im in images:
		  new_im.paste(im, (x_offset,0))
		  x_offset += im.size[0]

		# new_im.save('test.jpg')
		new_im.show()

	def checkForDuplicateImages(self, dir_name_in, retake = False): #check all files against each other for similarity
		# pool = Pool(processes = 3)
		self.SIG = ShapeImageGenerator()
		self.SIG.readParameterFile('HandCenteredImageGeneratorParameters.csv')
		for files in os.walk(dir_name_in):
			# pick the first image
			for im_path1 in files[2]:
				if os.path.splitext(im_path1)[1] == '.png':
					im1 = self.imageTypeCheck(os.path.join(files[0], im_path1))
					# pick the second image
					for im_path2 in files[2]:
						if os.path.splitext(im_path2)[1] == '.png' and im_path1 != im_path2:
							im2 = self.imageTypeCheck(os.path.join(files[0], im_path2))
							sim_err = self.meanSquaredError(im1, im2)
							if sim_err == 0:
								# pdb.set_trace()
								print('Similarity Error: %s, files:%s, %s' %(sim_err, im_path1, im_path2))
								if retake:
									# pdb.set_trace()
									image_params2 = im_path2.split('_')
									a = None
									if len(image_params2) == 10:
										a = int(image_params2.pop(4).strip('a'))
									shape = image_params2.pop(0)
									h = int(image_params2.pop(0).strip('h'))
									w = int(image_params2.pop(0).strip('w'))
									e = int(image_params2.pop(0).strip('e'))
									obj_or = image_params2.pop(0)
									grasp_type = image_params2.pop(0)
									grasp_app = image_params2.pop(0)
									grasp_or = image_params2.pop(0)
									cam = image_params2.pop(0).strip('cam').strip('.png')
									if a is not None:
										param = self.SIG.getParameterFromFeatures(shape, h, w, e, obj_or, grasp_type, grasp_app, grasp_or, cam, a = a)
									else:
										param = self.SIG.getParameterFromFeatures(shape, h, w, e, obj_or, grasp_type, grasp_app, grasp_or, cam)
									# pdb.set_trace()
									self.SIG.createImageFromParameters(param)
									# self.viewImagesSideBySide([os.path.join(files[0], im_path1), os.path.join(files[0], im_path2)])
									# raw_input('Hit enter to continue')


if __name__ == '__main__':
	SIM = ShapeImageManipulator()

	# crop images down to size
	# SIM.cropAllImages('GeneratedImages', 'GeneratedImagesCropped')
	# combine images

	# SIM.combineMultipleImages('GeneratedImagesCropped', 'GeneratedImagesCombined')
	# # reduce image size
	# SIM.reduceSizeAllImages('GeneratedImagesCropped/ObjectsOnly', 'GeneratedImagesReduced/ObjectsOnly', size = (285, 200))
	# SIM.reduceSizeAllImages('GeneratedImagesCombined/Grasps', 'GeneratedImagesReduced/Grasps', size = (285, 200))
	# #upload Images
	# SIM.uploadMultipleImages('GeneratedImagesReduced/')

	# SIM.checkOverCrop('test_cone_h25_w9_e9_cam1')
	# SIM.checkOverCrop('test_cone_h9_w9_e25_cam2')
	# SIM.checkOverCrop('test_cone_h9_w9_e25_cam2')
	# SIM.checkOverCropAll('GeneratedImagesCropped')
	# SIM.bboxToHand('test_cone_h9_w9_e25_cam2')

	SIM.checkForDuplicateImages('GeneratedImages', retake = True)
	# SIM.meanSquaredError('test_cone_h9_w9_e25_cam2','test_cone_h33_w9_e9_cam1' )





	# SIM.cropAllImages('GeneratedImages', 'GeneratedImagesCropped')
	# SIM.reduceSizeAllImages('GeneratedImagesCropped', 'GeneratedImagesReduced', size = (285, 200))


	# SIM.combineImagesTopRight('GeneratedImages/Grasps/cone_h3_w3_e3_a10_grasp0_cam0.png', 'GeneratedImages/Grasps/cone_h3_w3_e3_a10_grasp0_cam1.png', percent_image2 = 30)
	# SIM.cropToHand('GeneratedImages/Grasps/cone_h3_w3_e3_a10_grasp0_cam0.png')
	# im1 = SIM.cropOpenRAVEBoarder('GeneratedImages/Grasps/cone_h12_w12_e12_a10_grasp0_cam1.png')
	# im1 = SIM.cropOpenRAVEBoarder('GeneratedImages/Grasps/handle_h6_w60_e12_a12_grasp1_cam1.png')
	# SIM.previewImage(im1)