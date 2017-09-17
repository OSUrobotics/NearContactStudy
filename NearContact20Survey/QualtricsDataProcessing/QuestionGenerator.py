import csv
import pdb
import numpy as np
import Image
import os
import NearContactStudy
from pprint import pprint
from matplotlib.pyplot import show
import pickle

img_base_url = 'http://people.oregonstate.edu/~kotharia/RefinementSurvey/GeneratedImagesReduced/Grasps/'
#<img src="https://oregonstate.qualtrics.com/CP/Graphic.php?IM=IM_a5lHZYUV1YBU4nz" style="width: 363px; height: 377px;" />
img_temp = '<img src="%s" style="width: %spx; height: %spx;" />' #imgurl, width of image, height of image

class QuestionGenerator(object):
	#looks through multiple files to aggregate all the questions
	def __init__(self, file_list):
		self.files = file_list
		self.ImageDir = '/home/ammar/Documents/Projects/NearContactStudy/NearContact20Survey/QualtricsDataProcessing/RefinementImages/'


	def Gen(self):
		for FN in self.files:
			with open(FN, 'rb') as csvfile:
				reader = csv.reader(csvfile)
				for row in reader:
					if len(row) == 1: #its the question description
						try:
							shape,_,_,_,obj_or,grasp,approach,hand_or = row[0].split('_')
						except:
							shape,_,_,_,_,obj_or,grasp,approach,hand_or = row[0].split('_') #for when a cone happens!
						pass
					else:
						row.pop(0) #removes the descriptor (i.e. Question X)
						row = np.array(row).astype(float).reshape(-1,3)
						yield shape, row, obj_or, grasp, approach, hand_or

	def ImagePath(self, shape, dims, obj_or, grasp, approach, hand_or):
		#returns the path to an image file
		h, w, e = dims[:]
		P = '%s_h%.2f_w%.2f_e%.2f_%s_%s_%s_%s' %(shape, h, w, e, obj_or, grasp, approach, hand_or)
		P = P.replace('.', 'D')
		P += '.png'
		return P

	def ImageURL(self, shape, dims, obj_or, grasp, approach, hand_or):
		img_url = img_base_url + self.ImagePath(shape, dims, obj_or, grasp, approach, hand_or)
		img_block = img_temp %(img_url, 285, 200)
		return img_block

	def AggregateQuestions(self, FN_out):
		#looks through all files and pulls out questions into a usable format
		try:
			os.remove(FN_out)
		except:
			pass

		gen = self.Gen()
		QID_counter = 1
		for shape, images, obj_or, grasp, approach, hand_or in gen:
			if shape != 'cube':
				continue
			if grasp != 'equidistant':
				continue
			if hand_or != 'up':
				continue
			if approach =='top':
				continue
			if obj_or != 'h':
				continue

			i = 1
			questionText = 'Which of the following grasps do you think will work?'
			impath = [self.ImageURL(shape, i, obj_or, grasp, approach, hand_or) for i in images]
			QID = 'QID_%s' %QID_counter

			with open(FN_out, 'ab') as csvfile:
				writer = csv.writer(csvfile)
				row = [QID]
				[row.append(i) for i in impath]
				writer.writerow(row)

			QID_counter += 1

	def plotQuestionPoints(self): #plots all the dimensions for all the possibilities on a single plot
		Plotter = NearContactStudy.BuildPolytope()
		f, ax = Plotter.createPlot()
		gen = self.Gen()
		ps = []
		for shape, images, obj_or, grasp, approach, hand_or in gen:
			if shape != 'cube':
				continue
			if grasp != 'equidistant':
				continue
			if hand_or != 'up':
				continue
			if approach != 'side':
				continue
			if obj_or != 'h':
				continue
			ps = np.array([i for i in images])
			ax.scatter(ps[:,0], ps[:,1], ps[:,2], c = np.random.rand(3))
		# ps = np.array(ps).flatten().reshape(-1,3)
		# Plotter.plotPoints(ps, ax)
		Plotter.formatPlot(ax)
		# pdb.set_trace()
		# pickle.dump(ax, file('SpaceOfQuestions.fig.pickle', 'wb'))
		show()






if __name__ == '__main__':
	file_list = ['-0.5_NonparametricNextQuestions.csv',
				'0.0001_NonparametricNextQuestions.csv',
				'0.5_NonparametricNextQuestions.csv'
				]
	# file_list = ['0.5_NonparametricNextQuestions.csv']
	QG = QuestionGenerator(file_list)
	QG.AggregateQuestions(FN_out = 'AllQuestions.csv')
	QG.plotQuestionPoints()
