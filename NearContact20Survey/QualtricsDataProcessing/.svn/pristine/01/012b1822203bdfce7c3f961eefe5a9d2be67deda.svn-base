import csv
import math
import numpy as np 

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
			newCat =  "{}: {}".format(next(newCatGenerator), self.getDimension(columnNum))
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
	for i in range(39):
		removeableCols.append(i)
	for i in range(424, 428):
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


if __name__ == "__main__":
	data = dataResults()
	reader = csvReader('Near_Contact_20_Imported.csv', data)
	reader.readCSV()
	removeUnfinishedRows(data)
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
	data.changeCategories(questions)
	data.toArray()
	analyzer = dataAnalyzer(data)
	analyzer.sortShapeGraspByStd(printResults = True)
	print "-----------------------------------------------------------"
	keys = analyzer.sortKeysByStd(shapes)
	print "-----------------------------------------------------------"
	for key in keys:
		shape = key[0]
		analyzer.getShapeBoundaries(shape, printResults = "E")
		print("********************************************************************************************************************")