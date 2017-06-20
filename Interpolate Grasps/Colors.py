import numpy as np

class ColorsDict(object): # General class for holding colors
	colors = dict()
	colors['pink'] = np.array([1,0,1])
	colors['grey'] = np.array([0.9, 0.9, 0.9])
	colors['blue'] = np.array([0, 0, 1])
	colors['green'] = np.array([0, 1, 0])
	colors['red'] = np.array([1, 0, 0])
	colors['black'] = np.array([0.01, 0.01, 0.01])
	colors['greenI'] = np.array([115, 224, 2]).astype('float')  / 255 # from paper
	colors['pinkI'] = np.array([242, 143, 145]).astype('float') / 255 # from paper
	colors['greyI'] = np.array([148, 146, 148]).astype('float') / 255 # from paper
	colors['blueI'] = np.array([132, 132, 228]).astype('float') / 255 # from paper


class bcolors():
	def __init__(self):
		self.HEADER = '\033[95m'
		self.OKBLUE = '\033[94m'
		self.OKGREEN = '\033[92m'
		self.WARNING = '\033[93m'
		self.FAIL = '\033[91m'
		self.ENDC = '\033[0m'
		self.BOLD = '\033[1m'
		self.UNDERLINE = '\033[4m'
	
	def printFail(errorString):
		print(bcolors.Fail + errorString + bcolors.ENDC)

