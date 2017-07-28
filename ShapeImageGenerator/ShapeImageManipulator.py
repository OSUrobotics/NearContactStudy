import subprocess, os, pdb, re
import paramiko
from  PIL import Image
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

#Editted: Ammar Kothari -- Last Update: 7/13/17
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
					elif 'cam2' in im_path: #just keep going look for cam1
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

	def cropToHand(self, image1): #crop images so only hand and object remain
		# this depends on the choice of hand color and object color.
		# potentially do some smart sampling, but it is unclear

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


if __name__ == '__main__':
	SIM = ShapeImageManipulator()

	# crop images down to size
	# SIM.cropAllImages('GeneratedImages', 'GeneratedImagesCropped')
	# combine images
	SIM.combineMultipleImages('GeneratedImagesCropped', 'GeneratedImagesCombined')
	# reduce image size
	SIM.reduceSizeAllImages('GeneratedImagesCropped/ObjectsOnly', 'GeneratedImagesReduced/ObjectsOnly', size = (285, 200))
	SIM.reduceSizeAllImages('GeneratedImagesCombined/Grasps', 'GeneratedImagesReduced/Grasps', size = (285, 200))
	#upload Images
	SIM.uploadMultipleImages('GeneratedImagesReduced/')







	# SIM.cropAllImages('GeneratedImages', 'GeneratedImagesCropped')
	# SIM.reduceSizeAllImages('GeneratedImagesCropped', 'GeneratedImagesReduced', size = (285, 200))


	# SIM.combineImagesTopRight('GeneratedImages/Grasps/cone_h3_w3_e3_a10_grasp0_cam0.png', 'GeneratedImages/Grasps/cone_h3_w3_e3_a10_grasp0_cam1.png', percent_image2 = 30)
	# SIM.cropToHand('GeneratedImages/Grasps/cone_h3_w3_e3_a10_grasp0_cam0.png')
	# im1 = SIM.cropOpenRAVEBoarder('GeneratedImages/Grasps/cone_h12_w12_e12_a10_grasp0_cam1.png')
	# im1 = SIM.cropOpenRAVEBoarder('GeneratedImages/Grasps/handle_h6_w60_e12_a12_grasp1_cam1.png')
	# SIM.previewImage(im1)