import csv
import math
import numpy as np
import pdb
import re
import copy
from buildPolytopeFromResponses import BuildPolytope, PolytopeParametric, PolytopeNonparametric
from DiscreteAnalysis import DiscreteAnalysis
from ContinuousAnalysis import ContinuousAnalysis
from Parametric import Parametric
from Nonparametric import Nonparametric

# import matplotlib.pyplot as plt
import os
import sys
import matplotlib.pyplot as plt

class csvReader(object):
	#This class reads the exported csv file with the survey results
	#and adjusts its data object accordingly

	def __init__(self, fileName, data):
		#fileName is a string of the csv file's name
		#data is a blank dataResults object
		#this sets up the local variables for the object
		self.file = fileName
		self.data = data

	def readCSV(self):
		#this opens up the csvfile passed in initialization
		#this calls handleRow with special stipulations for the first two rows (title rows)
		dataFile = open(self.file)
		reader = csv.reader(dataFile)
		firstRow=True
		secondRow = False
		for row in reader:
			self.handleRow(firstRow, secondRow, row)
			secondRow = False
			if firstRow == True:
				firstRow = False
				secondRow = True

	def handleRow(self, firstRow, secondRow, row):
		#firstRow and secondRow are booleans, row is csv reader element
		#this adjusts self.data by seting category names or adding data appropriately
		if firstRow:
			self.addCategories(row)
		elif secondRow:
			self.reviseCategories(row)
		else:
			self.addData(row)

	def addCategories(self, row):
		#row is a csv reader element
		#this creates a set of new categories from row elements into it's dataResults variable
		for category in row:
			self.data.addCategory(category)

	def reviseCategories(self, row):
		#row is a csv reader element
		#this takes the old category name for every category and revises it according to how dataResults revises category names
		#revises based on columnNum
		columnNum = 0
		for value in row:
			self.data.reviseCategory(value, columnNum)
			columnNum += 1

	def addData(self, row):
		#row is a csv reader element
		#this adds the appropriate data values to the dataResults class by columnNumber
		columnNum = 0
		for dataPoint in row:
			self.data.addDataPoint(columnNum, dataPoint)
			columnNum += 1






class dataResults(object):
	#This class holds the data values under the categories
	#This class is filled by csvReader
	#This class is analyzed by dataAnalyzer

	def __init__(self):
		#self.columns is {columnNumbers:categoryName}
		#self.data is {categoryName:dataList} to start and {categoryName:dataArray} after calling toArray
		self.columns = {}
		self.categoryCount = 0
		self.data = {}
		self.dataAdded = False

	def addCategory(self, category):
		#category is a string representing the category title's name
		#This assumes you add categories in sequential order
		#This assumes addDataPoint has not been called yet
		self.columns[self.categoryCount] = category
		self.categoryCount += 1
	
	def reviseCategory(self, addition, categoryNum):
		#addition is a string representing the category addition and categoryNum is an unsigned int
		#this assumes addDataPoint has not been called yet
		#appends the addition string to the end of the current categoryName at that categoryNum
		if addition != '':
			self.columns[categoryNum] = "{}: {}".format(self.columns[categoryNum], addition)
	
	def changeCategories(self, questions):
		#questions is a 3-depth tuple that matches the tuple used to fill in the loop and merge
		#generates new category names that replace the current category names but iterating through the questions and replacing them sequnetially
		#assumes unnecessary columns have been removed
		newCatGenerator = self.getNextCategoryNameFromQuestions(questions)
		for columnNum in sorted(self.columns.keys()):
			try:
				newCat =  "{}: {}".format(next(newCatGenerator), self.getDimension(columnNum))
			except:
				pdb.set_trace()
			self.changeCategory(newCat, columnNum)

	def getNextCategoryNameFromQuestions(self, questions):
		#questions is a 3-depth tuple that matches the tuple used to fill in the loop and merge
		#generator that returns new category names based on the questions/sliders
		for pregraspApproach in questions:
			for wrist in pregraspApproach[1]:
				for startingShapeNum in [0, 1, 2]:
					for shapeNum in range(len(wrist[1])):
						shape = (startingShapeNum+shapeNum)%len(wrist[1])
						yield "Shortest: {}: {}: {}".format(pregraspApproach[0], wrist[0], wrist[1][shape][0])
						yield "Longest: {}: {}: {}".format(pregraspApproach[0], wrist[0], wrist[1][shape][0])

	def getDimension(self, columnNum):
		#columnNum is an unsigned int
		#gets the last letter (dimension that is growing) of the category name 
		#associated with columnNum
		category = self.columns[columnNum]
		category = category[:category.find(":")]
		for character in reversed(category):
			if character.isalpha():
				return character

	def changeCategory(self, newCategory, columnNum):
		#newCategory is a string representing the new Category name columnNum is an unsigned int
		#changes the category name associated with the columnNum to a new name
		#assumes addDataPoint has been called at least once
		oldCategory = self.columns[columnNum]
		self.columns[columnNum] = newCategory
		self.data[newCategory] = self.data[oldCategory]
		self.data.pop(oldCategory, None)

	def addDataPoint(self, categoryNum, dataPoint):
		#categoryNum is an unsigned int and dataPoint is any value
		#creates empty lists for data for each category the first time called
		#adds the value to the end of the list to dataPoints in self.data for the specified categoryNum
		if not self.dataAdded:
			for category in self.columns.values():
				self.data[category] = []
			self.dataAdded = True
		self.data[self.columns[categoryNum]].append(dataPoint)

	def removeRow(self, rowNum):
		#removes the dataPoints at the rowNum index within all the data lists
		#cannot remove the title columns (rowNum 0 is the first row involving data)
		for column in self.data:
			del self.data[column][rowNum]

	def removeCat(self, columnNum = None, category=None):
		#category is a string and columnNum is an unsigned int
		#EITHER CATEGORY OR COLUMNNUM MUST BE PROVIDED
		#If both are provided, breaks if they are not associated with each other
		#removes the category from both self.data and self.columns
		print columnNum
		print category
		if category and columnNum:
			if self.columns[columnNum] != category:
				raise ValueError("Column and Category did not match")
		if columnNum != None:
			category = self.columns[columnNum]
			self.columns.pop(columnNum, None)
			self.data.pop(category, None)
		elif category != None:
			for cNum in self.columns:
				if self.columns[cNum] == category:
					self.columns.pop(cNum, None)
			self.data.pop(category, None)
		else:
			raise ValueError("Need to pass either a column or a category")

	def getRow(self, category, value):
		result = []
		if category not in self.data:
			return result
		else:
			row = 0
			for dataPoint in self.data[category]:
				if dataPoint == value:
					result.append(row)
				row += 1
		return result

	def printData(self):
		#This prints every category in sequential order
		for count in sorted(self.columns.keys()):
			self.printCol(count)

	def printCol(self, columnNum):
		#columnNum is an unsigned int
		#This prints all the data associated with the columnNum
		category = self.columns[columnNum]
		print("{:10}: {:100}: {:30}".format(columnNum, category, self.data[category]))

	def printCat(self, category):
		#category is a string
		#This prints all the data associated with the category name but does not print the columnNum for the category
		print("{:100}: {}". format(category, self.data[category]))

	def toArray(self):
		#This converts all the lists in the values of self.data to arrays
		#This allows stats to be done more easily
		#This assumes all data has been correctly added to self.data
		for category in self.data:
			self.data[category] = np.array([int(x) for x in self.data[category] if x])

	def getWorkerIDs(self):
		# pulls the individual workerIDs
		# before removing any columns
		self.workerIDs = self.data['workerId: workerId']

	def removeWorkers(self):
		#removes any data from workers that are blank
		keep_workers = [i for i, id_num in enumerate(self.workerIDs) if id_num != '']
		for category in self.data:
			self.data[category] = [w for i,w in enumerate(self.data[category]) if i in keep_workers]

	def questionMapper(self, questions):
		# maps questions from vicky's terminology to Ammar's (should make loading images easier)
		# questions is the same tuple given to changeCategories
		self.mapper = []
		for q in questions:
			grasp_approach_V = q[0]
			grasp_A = q[0].split('_')[0]
			approach_A = q[0].split('_')[1]
			for t in q[1]:
				orientation_V = t[0]
				for s in t[1]:
					obj = s[0].split('_')[0]
					obj_or = s[0].split('_')[1]
					hand_or = s[1]
					self.mapper.append([grasp_A, approach_A, obj, obj_or, hand_or, orientation_V])

	def questionMapperToCSV(self):
		header = ['Grasp', 'Approach', 'Shape', 'Shape Orientation', 'Hand Orienation - Ammar', 'Hand Orientation - Vicky']
		filename = 'QuestionMapper.csv'
		with open(filename, 'wb') as csvfile:
			writer = csv.writer(csvfile)
			writer.writerow(header)
			for r in self.mapper:
				writer.writerow(r)

	def writeSingleResultToCSV(self):
		#writes the results to a csv file.
		# name of file is workerId
		# count_unlabeled = 0
		for i_ID, ID in enumerate(self.workerIDs):
			if ID == '': # blank ID so probably a test, but they aren't blank
				# ID = 'Unlabeled%s' %count_unlabeled
				# count_unlabeled += 1
				continue
			file_name = '%s.csv' %ID
			with open(file_name, 'wb') as csvfile:
				writer = csv.writer(csvfile)
				for k,v in self.data.iteritems():
					writer.writerow([k, v[i_ID]])

	def writeAllResultsToCSV(self, file_name = 'AllResponses.csv'):
		#writes the all of the results to a single csv file
		with open(file_name, 'wb') as csvfile:
			writer = csv.writer(csvfile)
			keep_workers = [i for i, id_num in enumerate(self.workerIDs) if id_num != ''] #skip blank
			header = [id_num for i, id_num in enumerate(self.workerIDs) if i in keep_workers] #skip blank
			header.insert(0, 'Question')
			writer.writerow(header)
			for k,v in self.data.iteritems():
				k = [k]
				k.extend([w for i,w in enumerate(v) if i in keep_workers])
				writer.writerow(k)

	def array2int(self, arr): #converts array with strings and blanks to values
		vals = []
		for val in arr:
				try:
					vals.append(int(val))
				except:
					continue
		return vals

	def checkHistograms(self):
		#plots and saves histograms for all the data
		#change folder for each project!
		f_names = ['Small', 'Large']
		for i,d in enumerate((self.small_shapedata, self.large_shapedata)):
			Folder = 'Near Contact 2.0 - Verification/Histograms/' + f_names[i] + '/'
			for k1,v1 in d.iteritems():
				for k2,v2 in v1.iteritems():
					plt.hist(v2, [0, 5, 13, 21, 29, 33])
					plt.xlim([0,33])
					plt.title('_'.join([k1,k2]))
					plt.savefig(Folder + '_'.join([k1,k2]) + '.png')
					plt.close()
	
	def RearrangeDictToShapeSpace(self): # creates a dictionary from data.data where key is the scenario
		self.small_shapedata = dict()
		self.large_shapedata = dict()
		for k,v in self.data.iteritems():
			question_parts = k.split(':')
			if question_parts[0] == 'Shortest':
				dict_to_update = self.small_shapedata
			else:
				dict_to_update = self.large_shapedata
			#check if question exists in dict
			question_key = ':'.join(question_parts[1:-1])
			if question_key in dict_to_update.keys():
				#check if dictionary has been created in that spot
				if isinstance(dict_to_update[question_key], dict):
					dict_to_update[question_key][question_parts[-1]] = v
				else:
					pdb.set_trace()
			else:
				dict_to_update[question_key] = {question_parts[-1] : v}

	def CleanData(self, d, val_to_pop = 0, greater = True):
		# removes 'starting' value of survey i.e. for largest question, if slider reads 0, then remove value
		# signals that someone did not sufficiently answer a question
		d_copy = copy.deepcopy(d)
		for k1,v1 in d.iteritems():
			for k2, v2 in v1.iteritems():
				if greater: tf_array = (v2 > val_to_pop) 
				if not greater: tf_array = (v2 < val_to_pop-1)
				d_copy[k1][k2] = v2[tf_array]
		d = d_copy
		return d_copy

	def CleanDataGreater(self, d, val_to_pop = 0): return self.CleanData(d, val_to_pop = val_to_pop, greater = True) #helper function
	def CleanDataLess(self, d, val_to_pop = 100): return self.CleanData(d, val_to_pop = val_to_pop, greater = False) #helper function


	def mapShapeSpace(self, d, Analysis_Object):
		# takes a dictionary in shape space and replaces values with mapped values to shape dimensions
		# Analysis_Object is an object that has an array conversion ability
		for k1,v1 in d.iteritems():
			for k2,v2 in v1.iteritems():
				d[k1][k2] = Analysis_Object.array(v2)
		return d

	def createPolytopeAllPoints(self, key = None): #plots values from survey for a single scenario
		if not key: key = self.small_shapedata.keys()[10]
		dim_mapper = {' H': 0, ' W': 1, ' E': 2}
		# gets all the data points for a particular key from the survey -- only makes sense if they have been discretized?
		responses = []
		for d in (self.small_shapedata[key], self.large_shapedata[key]):
			for k1,v1 in d.iteritems():
				for r in v1:
					moderate_array = [17, 17, 17]
					moderate_array[dim_mapper[k1]] = r
					responses.append(moderate_array)
		responses = np.array(responses)
		# plot it on an array
		P = BuildPolytope()
		ax = P.plotPoints(responses, show = False)
		ax.set_title(key)
		hull = P.fitConvexHull(responses)
		eqs, simps = P.uniqueHullEquations(hull)
		hull_simp = copy.deepcopy(hull)
		hull_simp.equations = eqs
		hull_simp.simplices = simps
		P.paramsForNewQuestions(responses, hull_simp)
		P.drawPlanesFromHull(responses, hull_simp, ax, show = False)
		P.drawAvgPointOnHull(responses, hull_simp, ax, show = True, hull_original = hull)
		pdb.set_trace()


def removeUnfinishedRows(data):
	#data is a dataResults object
	#One of the columns in the CSV should be 'V10: Finished'
	#This looks for users that entered the survey but did not complete it and removes all data associated with those users
	for row in reversed(data.getRow("V10: Finished", '0')):
		data.removeRow(row)

def removeUnnecessaryColumns(data):
	#data is a dataResults object
	#This assumes all columns from 0-38 are unvaluable and removes them
	#This assumes all columns from 424-427 are unvaluable and removes them
	#Of the remaining categories (just the slider questions), this looks for categories including 'I'
	# (instuctional questions) and removes them
	removeableCols = []
	for i in range(41):
		removeableCols.append(i)
	for i in range(426, 431):
		removeableCols.append(i)
	for col in removeableCols:
		data.removeCat(col)
	removeableCols = []
	for columnNum in data.columns:
		if 'I' in data.columns[columnNum]:
			removeableCols.append(columnNum)
	for col in removeableCols:
		data.removeCat(col)





class dataAnalyzer(object):
	#This object handles performing statistical operations on the dataResults object

	def __init__(self, dataArrays):
		#dataArrays is a dataResults object that has already been filled in
		self.data = dataArrays

	def centerPercent(self, dataArray):
		#dataArray is one np.array
		#gets the center of the array depending on the standard deviation
		std = np.std(dataArray)
		if std < 10:
			return np.average(dataArray)
		else:
			return np.median(dataArray)

	def centerSize(self, dataArray):
		#dataArray is an np.array
		#this converts the center of the array as a percentage to its value in cm
		#this is based on the smallest object image at 1cm (10%) and the largest object image at 9cm (90%)
		percent = self.centerPercent(dataArray)
		if percent < 10:
			return percent *.1
		elif percent > 90:
			return ((percent-90)*.1) + 33
		else:
			return (percent-7.5)*.4

	def getShapeBoundaries(self, shape, printResults = "N"):
		#shape is a string representing the shape of an object
		#printResults is either 'N'(othing), 'S'(ummary), or 'E'(verything)
		#finds the average shortest and average longest values for one shape across all grasps
		#returns ((smallCenter, smallStd), (largeCenter, largeStd))
		result = []
		if printResults == "E" or printResults == "S":
			print(shape)
		for dimension in ['H', 'W', 'E']:
			shortValues = []
			longValues = []
			for category in self.data.data.keys():
				self.addCategoryData(printResults, dimension, category, shortValues, longValues)
			shortValues = np.array(shortValues)
			longValues = np.array(longValues)
			result.append(((self.centerSize(shortValues), np.std(shortValues)), (self.centerSize(longValues), np.std(longValues))))
			if printResults == "E" or printResults == "S":
				print("- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -")
				print("Boundaries: {}({}) - {}({})".format(self.centerSize(shortValues), np.std(shortValues), self.centerSize(longValues), np.std(longValues)))
				print("- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -")
		
		return result

	def addCategoryData(self, printResults, dimension, category, shortValues, longValues):
		#printResults is either 'N'(othing), 'S'(ummery), or 'E'(verything)
		#dimension is either 'H', 'W', or 'E'
		#category is a string, shortValues are a list, longValues are a list
		#takes both slider's data for a certain question and adds these values to shortValues and longValues
		if category.find(shape) != -1 and category[0] == 'S' and category[-1] == dimension:
			baseCat = category[category.find(":")+1:]
			longCat = "Longest:"+ baseCat
			for value in self.data.data[category]:
				shortValues.append(value)
			for value in self.data.data[longCat]:
				longValues.append(value)
			if printResults == "E":
				print("{:15} ({:15})\t{:15} ({:15})\t{}".format(self.centerSize(self.data.data[category]), np.std(self.data.data[category]), self.centerSize(self.data.data[longCat]), np.std(self.data.data[longCat]), baseCat))

	def sortShapeGraspByStd(self, reverse=False, printResults=False, key = None):
		#reverse is a boolean, printResults is a boolean, and key is a function
		#looks at all grasp groups (all sliders for all dimensions for a grasp and shape) and sorts these groups by the key
		#returns a list representing the category, std, and center of questions sorted in the same order 
		if key == None:
			key = self.graspShapeMaxStd
		result = []
		for category in sorted(self.data.data, reverse=reverse, key=key):
			result.append((category, np.std(self.data.data[category]), self.centerSize(self.data.data[category])))
			if printResults:
				print("{:20}\t{:20}:\t\t Std Dv: {}, Center: {}cm".format(key(category), category, np.std(self.data.data[category]), self.centerSize(self.data.data[category])))
		return result

	def graspShapeSumStd(self, category):
		#category is a string
		#this finds all grasps in the same grasp group as category and returns their summed std
		result = 0
		baseCat = category[category.find(":")+1:-2]
		for dimension in [" H", " W", " E"]:
			result += self.dimensionSumStd(baseCat, dimension)
		return result

	def graspShapeMaxStd(self, category):
		#category is a string
		#this finds all grasps in the same grasp group as category and returns the maximum of their std
		result = 0
		baseCat = category[category.find(":")+1:-2]
		for dimension in [" H", " W", " E"]:
			value = self.dimensionMaxStd(baseCat, dimension)
			if value > result:
				result = value
		return result

	def dimensionSumStd(self, baseCat, dimension):
		#baseCat is a string representing the grasp and shape while dimension is a string representing the dimension to check
		#returns the sum of the shortest and longest sliders' stds 
		return self.sliderStd(baseCat + dimension, "Shortest:") + self.sliderStd(baseCat + dimension, "Longest:")

	def dimensionMaxStd(self, baseCat, dimension):
		#baseCat is a string representing the grasp and shape while dimension is a string representing the dimension to check
		#returns the max of the shortest and longest sliders' stds 
		return max(self.sliderStd(baseCat + dimension, "Shortest:"), self.sliderStd(baseCat + dimension, "Longest:"))

	def sortKeysByStd(self, keys, reverse=False, printResults=False):
		#keys is an iterable of strings, reverse is a bool, printResults is a bool
		#this finds all categories that include a particular key and creates a group out of them
		#these groups are then sorted by self.keyStd
		result = []
		for key in sorted(keys, reverse=reverse, key=self.keyStd):
			result.append((key, self.keyStd(key)))
			if printResults:
				print("{}\t{}".format(self.keyStd(key), key))
		return result

	def keyStd(self, key):
		#key is a string
		#returns the average std over all the categories with a certain key
		result = 0
		count = 0
		for category in self.data.data.keys():
			if category.find(key) != -1:
				result += self.sliderStd(category, "")
				count += 1
		if count != 0:
			return result/count
		else:
			return 0

	def sliderStd(self, baseCat, slider):
		#baseCat is a string and slider is a string
		#returns a std based score for a slider that is heavily increased if there were less than 3 dataPoints
		#lower scores are much better than higher scores
		values = self.data.data[slider + baseCat].size
		if values == 0:
			return 333
		elif values < 3:
			return ((3-values)*111) + np.std(self.data.data[slider + baseCat])
		else:
			return np.std(self.data.data[slider + baseCat])


class overnightRun(object):
	#just a holder for an overnight run of parameters
	def __init__(self, data):

		NpStats = Nonparametric()
		NpSurf = PolytopeNonparametric()
		CIs = [-.5, 0.0001, 0.5]
		for CI in CIs:
			NpStats.AnalyzeResults((data.small_shapedata, data.large_shapedata), P=CI)
			NpSurf.setDicts(NpStats.small_shapedata_stats, NpStats.large_shapedata_stats)
			NpSurf.writeAllQuestions('%s_NonparametricNextQuestions.csv' %CI, CI)
			NpSurf.createPolytopeStatsAll(CI_amount = 0.5 + CI/2.0)


		for CI in CIs:
			NpStats.AnalyzeResults((data.small_shapedata, data.large_shapedata), P=CI)
			NpSurf.setDicts(NpStats.small_shapedata_stats, NpStats.large_shapedata_stats)
			NpSurf.createMultiplePolytopeStatsAll(CI_amount = 0.5 + CI/2.0)


		PStats = Parametric()
		PSurf = PolytopeParametric()
		PStats.AnalyzeResults((data.small_shapedata, data.large_shapedata))
		PSurf.setDicts(PStats.small_shapedata_stats, PStats.large_shapedata_stats)
		PSurf.createPolytopeStatsAll()
		PSurf.createMultiplePolytopeStatsAll()


		print('Overnight Run Has Ended!')
		pdb.set_trace()


if __name__ == "__main__":
	data = dataResults()
	reader = csvReader('Near Contact 2.0 - Initial/Near_Contact_20_Imported.csv', data)
	reader.readCSV()
	removeUnfinishedRows(data)
	data.getWorkerIDs()
	removeUnnecessaryColumns(data)
	#This 3-depth tuple was copy-pasted from fill_in_qsf.py in NearContact20Survey/QualtricsGeneration
	questions = (("equidistant_top", (("3 down the sides",(("cylinder_h_","up"), ("ellipse_h_","up"), ("cone_h_","up"))), ("3 around the sides",(("cylinder_e_","angled"), ("cone_e_","90"), ("cube_h_","angled"))),("2 around the sides, 1 on the base",(("cylinder_e_","up"), ("cone_e_","up"), ("cube_h_","up"))))),
							("equidistant_side",(("3 around the sides, palm on flat",(("cylinder_e_","up"), ("cube_h_","down"), ("cone_e_","up"))), ("3 around the sides, palm on round",(("ellipse_h_","up"), ("cylinder_h_","down"), ("cone_h_","90"))),("2 pinch the sides, 1 on the top",(("cylinder_h_","up"), ("cone_h_","up"), ("cube_h_","up"))))),
							("3fingerpinch_top",(("opposite sides",(("cylinder_h_","up"), ("cylinder_w_","up"), ("cube_h_","up"), ("ellipse_h_","up"), ("cone_h_","up"))), ("around the sides",(("cylinder_e_","up"), ("cone_e_","up"), ("cube_h_","angled"))))),
							("3fingerpinch_side",(("around the sides",(("cylinder_h_","up"), ("ellipse_h_","up"), ("cone_h_","up"))), ("end to end",(("cylinder_w_","up"), ("cone_e_","up"), ("cube_h_","up"))))), 
							("hook_side",(("over the top",(("cylinder_h_","up"), ("cylinder_e_","up"), ("cube_h_","up"), ("ellipse_h_","up"))), ("around the sides",(("cylinder_e_","90"), ("cube_h_","90"), ("cylinder_h_","90"), ("ellipse_h_","90"), ("cone_h_","90"))))),
							("2fingerpinch_top",(("2 around the sides",(("ellipse_h_","up"), ("cone_e_","up"), ("cylinder_e_","up"), ("cube_h_","angled"))), ("end to end",(("cylinder_w_","up"), ("cube_h_","up"), ("cone_h_","up"), ("cylinder_h_","up"))))),
							("2fingerpinch_side",(("around the sides",(("cylinder_h_","up"), ("ellipse_h_","up"), ("cone_h_","up"))), ("end to end",(("cylinder_w_","up"), ("cone_e_","up"), ("cube_h_","up"))))))
	shapes = ("cone_h_", "cone_e_", "cylinder_h_", "cylinder_w_", "cylinder_e_", "ellipse_h_", "cube_h_")
	# data.questionMapper(questions)
	# data.questionMapperToCSV()
	data.changeCategories(questions)
	# data.writeSingleResultToCSV()
	# data.writeAllResultsToCSV()
	data.removeWorkers()
	data.toArray()
	data.RearrangeDictToShapeSpace()
	data.small_shapedata = data.CleanDataLess(data.small_shapedata, val_to_pop = 100)
	data.large_shapedata = data.CleanDataGreater(data.large_shapedata, val_to_pop = 0)
	Analysis = ContinuousAnalysis()
	data.small_shapedata = data.mapShapeSpace(data.small_shapedata, Analysis)
	data.large_shapedata = data.mapShapeSpace(data.large_shapedata, Analysis)
	ON = overnightRun(data)
	Stats = Nonparametric()
	Surf = PolytopeNonparametric()
	CIs = [.5, 0.0001, -0.5]
	key = data.small_shapedata.keys()[05]
	for CI in CIs:
		Stats.AnalyzeResults((data.small_shapedata, data.large_shapedata), P = CI)
		# Stats.AnalyzeResultsToCSV(file_out = '%sNonParamContinuousAnalyzedResponses.csv' %abs(CI))
		Surf.setDicts(Stats.small_shapedata_stats, Stats.large_shapedata_stats)
		ax = Surf.createPolytopeStats(CI, key)
		if not ax: continue # polytope does not exist!
		# Surf.createPolytopeStats()
		qps = Surf.paramsForNewQuestionsGrid(CI, key)
		Surf.plotQuestionPoints(qps, ax = ax)
		Surf.writePointsToCSV('NonparametricNextQuestions.csv', key, qps, CI)
		# plt.show(block = True)
		# pdb.set_trace()
		# data.createPolytopeStatsAllNonparametric(CI_amount = 0.5 + CI/2.0)
	# data.createMultiplePolytopeStatsAll()
	pdb.set_trace()
	analyzer = dataAnalyzer(data)
	analyzer.sortShapeGraspByStd(printResults = True)
	print "-----------------------------------------------------------"
	keys = analyzer.sortKeysByStd(shapes)
	print "-----------------------------------------------------------"
	for key in keys:
		shape = key[0]
		analyzer.getShapeBoundaries(shape, printResults = "E")
		print("********************************************************************************************************************")