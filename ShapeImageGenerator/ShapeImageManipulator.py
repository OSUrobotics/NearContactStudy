import subprocess, os, pdb
import paramiko
from  PIL import Image

#Editted: Ammar Kothari -- Last Update: 7/13/17
class ShapeImageManipulator: #manipulate images that have been produced (most likely with ShapeImageGenerator)
	def __init__(self):
		self.i = 1

	def combineImagesTopRight(self, image1, image2): #combine images so that the second one is smaller and in top right corner
		i = 1

	def cropOpenRAVEBoarder(self,image1): # crops image.  image1 is a PIL.Image object
		cur_box = image1.getbbox()
		if cur_box != (0,0,640,480):
			print("Image has been cropped already")
			return image1
		crop_box = (30,20,600,420)
		image1_cropped = image1.crop(crop_box)
		return image1_cropped

	def previewImage(self, image1): # preview image, image is a PIL.Image object or string of path to file
		if type(image1) is str:
			im = Image.open(image1)
		else:
			im = image1
		im.show()

	def saveImage(self, image1, fn): #save an image. image = PIL.Image object, fn is a string path
		image1.save(fn)

	def closeImage(self,image1):
		image1.close()

	def uploadMultipleImages(self):
		filename = 'GeneratedImages/'
		subprocess.Popen(["scp", "-r", filename, "%s@%s:%s" %('kotharia', 'shell.onid.oregonstate.edu', 'public_html/')]).wait()
		# requires password
		# images can be found at website: http://people.oregonstate.edu/~kotharia/GeneratedImages/

	def cropAllImages(self, dir_name):
		for files in os.walk(dir_name):
			for im_path in files[2]:
				if os.path.splitext(im_path)[1] == '.png':
					image_fn = os.path.join(files[0], im_path)
					image_orig = Image.open(image_fn)
					image_cropped = self.cropOpenRAVEBoarder(image_orig)
					self.saveImage(image_cropped, image_fn) #overwrite previous image
					try:
						self.closeImage(image_orig)
						self.closeImage(image_cropped)
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
	SIM.cropAllImages('GeneratedImages')
	SIM.uploadMultipleImages()