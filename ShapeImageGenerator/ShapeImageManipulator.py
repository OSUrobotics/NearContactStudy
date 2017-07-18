import subprocess, os, pdb
import paramiko
from  PIL import Image

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

	def combineImagesTopRight(self, image1, image2, percent_image2 = 25): #combine images so that the second one is smaller and in top right corner
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
		self.previewImage(im_out)
		pdb.set_trace()

	def cropOpenRAVEBoarder(self,image1): # crops image.  image1 is a PIL.Image object
		im1 = self.imageTypeCheck(image1)
		cur_box = im1.getbbox()
		if cur_box != (0,0,640,480): #should crop images down to desired size if they are larger
			print("Image has been cropped already")
			return image1
		crop_box = (30,20,600,420)
		im1_cropped = im1.crop(crop_box)
		return im1_cropped

	def previewImage(self, image1): # preview image
		im = self.imageTypeCheck(image1)
		im.show()

	def saveImage(self, image1, fn): #save an image
		im1 = self.imageTypeCheck(image1)
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
	# SIM.cropAllImages('GeneratedImages', 'GeneratedImagesCropped')
	# SIM.reduceSizeAllImages('GeneratedImagesCropped', 'GeneratedImagesReduced', size = (285, 200))
	SIM.uploadMultipleImages('GeneratedImages')
	SIM.uploadMultipleImages('GeneratedImagesCropped')
	SIM.uploadMultipleImages('GeneratedImagesReduced/')

	# SIM.combineImagesTopRight('GeneratedImages/Grasps/cone_h3_w3_e3_a10_grasp0_cam0.png', 'GeneratedImages/Grasps/cone_h3_w3_e3_a10_grasp0_cam1.png', percent_image2 = 30)