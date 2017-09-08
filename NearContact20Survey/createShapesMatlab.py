import matlab
import matlab.engine
import pdb

class ShapeSTLGeneratorPython(object):
	def __init__(self):
		running_mats = matlab.engine.find_matlab()
		if len(running_mats) == 0:
			future = matlab.engine.start_matlab(async=True)
			eng = future.result()
		else: #if matlab is already running for some reason, just connect to it instead of opening another instance
			# because that will probably cause my computer to turn into flames
			eng =  matlab.engine.connect_matlab(running_mats[0])
		eng.addpath('/home/ammar/Documents/Projects/NearContactStudy/ShapeGenerator') #adding generator file to path
		self.eng = eng

	def ShapeSTLGenerator(self, shape, resolution, filename, h, w, e, alpha):
		#generates shape with matlab script
		self.eng.ShapeSTLGenerator(shape, resolution, filename, h, w, e, alpha, nargout=0)

	def quit(self): #stop matlab
		self.eng.quit()

if __name__ == '__main__':
	S = ShapeSTLGeneratorPython()
	S.ShapeSTLGenerator('cube', 30, 'pythoncube.stl', .1, .1, .1, 10)
	S.quit()