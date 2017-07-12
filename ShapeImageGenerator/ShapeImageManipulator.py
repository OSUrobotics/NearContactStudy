import subprocess, os
import paramiko

#Editted: Ammar Kothari -- Last Update: 7/13/17
class ShapeImageManipulator: #manipulate images that have been produced (most likely with ShapeImageGenerator)
	def __init__(self):
		self.i = 1

	def combineImagesTopRight(self, image1, image2): #combine images so that the second one is smaller and in top right corner
		i = 1

	def uploadMultipleImages(self):
		filename = 'GeneratedImages/'
		subprocess.Popen(["scp", "-r", filename, "%s@%s:%s" %('kotharia', 'shell.onid.oregonstate.edu', 'public_html/')]).wait()
		# requires password
		# images can be found at website: http://people.oregonstate.edu/~kotharia/GeneratedImages/

	# def uploadSingleImage(self): #upload images, specific to Ammar's folder
	# 	username = 'KothariA'
	# 	password = 'Amm@r1234'
	# 	ssh = paramiko.SSHClient() 
	# 	ssh.load_host_keys(os.path.expanduser(os.path.join("~", ".ssh", "known_hosts")))
	# 	ssh.connect(server, username=username, password=password)
	# 	sftp = ssh.open_sftp()
	# 	sftp.put(localpath, remotepath)
	# 	sftp.close()
	# 	ssh.close()


if __name__ == '__main__':
	SIM = ShapeImageManipulator()
	SIM.uploadMultipleImages()