
import sys
sys.path.insert(0, '../')
from createShapesMatlab import ShapeSTLGeneratorPython

import csv
import pdb
import numpy as np
from pprint import pprint

resolution = {'cube':10.0, 'ellipse':100.0, 'cylinder':25.0, 'cone':50.0, 'vase':25.0}

class GenerateShapesFromCSV(object):
	def __init__(self):
		self.MShape = ShapeSTLGeneratorPython()
		i = 1

	def CSVGenerator(self, FN): #yields the next point in the file
		with open(FN, 'rb') as csvfile:
			reader = csv.reader(csvfile)
			for row in reader:
				if len(row) == 1: #its the question description
					shape = row[0].split(':')[-1].split('_')[0].strip()
					pass
				else:
					row.pop(0) #removes the descriptor (i.e. Question X)
					row = np.array(row).astype(float).reshape(-1,3)
					for r in row:
						yield shape, r


	def createShapes(self, FN, save_folder): #generates shapes from a csv file
		gen = G.CSVGenerator(FN)
		for shape,dims in gen:
			if shape != 'cube': #only do cubes for this part of the study
				continue
			h = float(dims[0])
			w = float(dims[1])
			e = float(dims[2])
			a = 25
			if shape == 'cone':
				save_name = '%s/%s_h%0.2f_w%0.2f_e%0.2f_a%0.2d' %(save_folder, shape, h, w, e, a)
			else:
				save_name = '%s/%s_h%0.2f_w%0.2f_e%0.2f' %(save_folder, shape, h, w, e)

			save_name = save_name.replace('.','D')
			h /= 100
			w /= 100
			e /= 100
			a = float(a/100.0)
			print('MShape.ShapeSTLGenerator(%s, %s, %s, %s, %s, %s, %s)' %(shape, resolution[shape], save_name, h, w, e, a))
			# pdb.set_trace()
			self.MShape.ShapeSTLGenerator(shape, resolution[shape], save_name, h, w, e, a)



if __name__ == '__main__':
	G = GenerateShapesFromCSV()
	G.createShapes('-0.5_NonparametricNextQuestions.csv', 'RefinementShapes')
	G.createShapes('0.0001_NonparametricNextQuestions.csv', 'RefinementShapes')
	G.createShapes('0.5_NonparametricNextQuestions.csv', 'RefinementShapes')
	G.MShape.quit()
	# pdb.set_trace()





