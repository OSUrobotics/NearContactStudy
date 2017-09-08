import os
import math
import csv
import pdb

class csvGenerator(object):
	# This class creates a list of urls for all the pregrasp approache combinations with shapes
	#The combinations are based on the "Survey Question Tree" files in Near Contact Study folder
	#It outputs a csv file with the list of urls in the first column going down
	
	def __init__(self):
		self.setDefaults()
	
	def setDefaults(self):
		#If different urls need to be generated this needs to be changed
		#If the files are found in a different location this needs to be changed
		self.shapes = {"cone_e_":['h','w','e','a'],'cone_h_':['h','w','e','a'],'cube_h_':['h','w','e'],'cylinder_w_':['h','w','e'], 'cylinder_e_':['h','w','e'], 'cylinder_h_':['h','w','e'],'ellipse_h_':['h','w','e']}
		self.dimensionSizes = {'h':['1','9','17','25','33'], 'w':['1','9','17','25','33'], 'e':['1','9','17','25','33'], 'a':['0','10','20']}
		
		#self.questions = ((preGraspApproach((block(shape(grasp), shape(grasp))), (block(shape(grasp)))), preGraspApproach((block(shape(grasp)))))
		self.questions = (("equidistant_top", (("3 down the sides",(("cylinder_h_","up"), ("ellipse_h_","up"), ("cone_h_","up"))), ("3 around the sides",(("cylinder_e_","angled"), ("cone_e_","90"), ("cube_h_","angled"))),("2 around the sides, 1 on the base",(("cylinder_e_","up"), ("cone_e_","up"), ("cube_h_","up"))))),
							("equidistant_side",(("3 around the sides, palm on flat",(("cylinder_e_","up"), ("cube_h_","down"), ("cone_e_","up"))), ("3 around the sides, palm on round",(("ellipse_h_","up"), ("cylinder_h_","down"), ("cone_h_","90"))),("2 pinch the sides, 1 on the top",(("cylinder_h_","up"), ("cone_h_","up"), ("cube_h_","up"))))),
							("3fingerpinch_top",(("opposite sides",(("cylinder_h_","up"), ("cylinder_w_","up"), ("cube_h_","up"), ("ellipse_h_","up"), ("cone_h_","up"))), ("around the sides",(("cylinder_e_","up"), ("cone_e_","up"), ("cube_h_","angled"))))),
							("3fingerpinch_side",(("around the sides",(("cylinder_h_","up"), ("ellipse_h_","up"), ("cone_h_","up"))), ("end to end",(("cylinder_w_","up"), ("cone_e_","up"), ("cube_h_","up"))))), 
							("hook_side",(("over the top",(("cylinder_h_","up"), ("cylinder_e_","up"), ("cube_h_","up"), ("ellipse_h_","up"))), ("around the sides",(("cylinder_e_","90"), ("cube_h_","90"), ("cylinder_h_","90"), ("ellipse_h_","90"), ("cone_h_","90"))))),
							("2fingerpinch_top",(("2 around the sides",(("ellipse_h_","up"), ("cone_e_","up"), ("cylinder_e_","up"), ("cube_h_","angled"))), ("end to end",(("cylinder_w_","up"), ("cube_h_","up"), ("cone_h_","up"), ("cylinder_h_","up"))))),
							("2fingerpinch_side",(("around the sides",(("cylinder_h_","up"), ("ellipse_h_","up"), ("cone_h_","up"))), ("end to end",(("cylinder_w_","up"), ("cone_e_","up"), ("cube_h_","up"))))))

		self.baseURL = "http://people.oregonstate.edu/~kotharia/GeneratedImagesReduced/Grasps/"
	
	def generateCSV(self, fileName):
		#fileName is a string of where the csv file is to be saved
		#for each question as stated in the Default this calls to generate the URLs
		with open(fileName, 'wb') as csvfile:
			self.csvwriter = csv.writer(csvfile)
			for preGraspApproach in self.questions:
				self.getPreGraspApproachURLs(preGraspApproach)

	def getPreGraspApproachURLs(self, preGraspApproach):
		#preGraspApproach is one entry in self.questions (preGrasp+approach angle, (wrist angle...))
		#this gets the URLs in for a given pregrasp+approach angle
		for block in preGraspApproach[1]:
		 	self.getBlockURLs(block, preGraspApproach[0])

	def getBlockURLs(self, block, preGraspApproach):
		#block is a wrist angle, shapes as in self.questions
		#preGraspApproach is the preGrasp+Approach in self.questions
		#Every iteration of the loop creates one version of the question such that 3 different shapes are asked about
		#for the 3 different dimensions
		shapeCount = len(block[1])
		for i in range(shapeCount):
			self.getShapeURLs(block[1][i][0], block[1][i][1], preGraspApproach, 'h')
			self.getShapeURLs(block[1][(i+1)%shapeCount][0], block[1][(i+1)%shapeCount][1], preGraspApproach, 'w')
			self.getShapeURLs(block[1][(i+2)%shapeCount][0], block[1][(i+2)%shapeCount][1], preGraspApproach, 'e')

	def getShapeURLs(self, shape, graspRot, preGraspApproach, dimension):
		#takes all the aspects about the image and creates the generator to get the URLs
		#writes the new URL from the Generator to the CSV starting at the smallest size and ending at the biggest size
		urlGenerator = self.getURLsAlongDimension(shape, graspRot, preGraspApproach, dimension)
		for size in self.dimensionSizes[dimension]:
			self.csvwriter.writerow([next(urlGenerator)])

	def getURLsAlongDimension(self, shape, graspRot, preGraspApproach, dimension):
		#Generator that takes all aspects about the image and yields the corresponding URL
		#yields urls starting at smallest value of the dimension and ending at the largest value
		sizes = {}
		for dim in self.shapes[shape]:
			sizes[dim] = self.dimensionSizes[dim][int(math.ceil(len(self.dimensionSizes[dim])/2))]
		if "_h_" != shape[-3:] and (dimension == "h" or dimension == shape[-2]):
			if dimension == "h":
				dimension = shape[-2]
			else:
				dimension = "h"
		for size in self.dimensionSizes[dimension]:
			sizes[dimension] = size
			result = self.baseURL + shape[:-3]
			for dim in self.shapes[shape]:
				result = result + "_" + dim + sizes[dim]
			result += shape[-3:]
			result = result +preGraspApproach + "_" + graspRot + ".png"
			yield result

class csvGenerator2_1(csvGenerator): #class to build csv for follow up survey
	def __init__(self):
		super(csvGenerator2_1, self).__init__()
		super(csvGenerator2_1, self).setDefaults()
		self.setDefaults()

	def setDefaults(self):
		self.questions = (("equidistant_top", (("3 down the sides",(("cylinder_h_","up"), ("ellipse_h_","up"), ("cone_h_","up"))), 
												("3 around the sides",(("cylinder_e_","angled"), ("cube_h_","angled"))),
												("2 around the sides, 1 on the base",(("cylinder_e_","up"), ("cube_h_","up"))))),
							("equidistant_side",(("3 around the sides, palm on flat",(("cylinder_e_","up"), ("cube_h_","down"), ("cone_e_","up"))), 
												("3 around the sides, palm on round",(("ellipse_h_","up"), ("cylinder_h_","down"), ("cone_h_","90"))),
												("2 pinch the sides, 1 on the top",(("cylinder_h_","up"), ("cone_h_","up"), ("cube_h_","up"))))),
							("3fingerpinch_top",(("opposite sides",(("cylinder_h_","up"), ("cylinder_w_","up"), ("cube_h_","up"), ("ellipse_h_","up"))), 
												("around the sides",(("cylinder_e_","up"), ("cone_e_","up"), ("cube_h_","angled"))))),
							("3fingerpinch_side",(("around the sides",(("cylinder_h_","up"), ("ellipse_h_","up"), ("cone_h_","up"))), 
												("end to end",(("cylinder_w_","up"), ("cone_e_","up"), ("cube_h_","up"))))), 
							("hook_side",(("over the top",(("cylinder_h_","up"), ("cylinder_e_","up"), ("cube_h_","up"), ("ellipse_h_","up"))), 
											("around the sides",(("cylinder_e_","90"), ("cube_h_","90"), ("cylinder_h_","90"), ("ellipse_h_","90"), ("cone_h_","90"))))),
							("2fingerpinch_top",(("2 around the sides",(("ellipse_h_","up"), ("cone_e_","up"), ("cylinder_e_","up"), ("cube_h_","angled"))), 
											("end to end",(("cylinder_w_","up"), ("cube_h_","up"), ("cone_h_","up"), ("cylinder_h_","up"))))),
							("2fingerpinch_side",(("around the sides",(("cylinder_h_","up"), ("ellipse_h_","up"), ("cone_h_","up"))), 
											("end to end",(("cylinder_w_","up"), ("cone_e_","up"), ("cube_h_","up"))))))
		# removed follow:
		# Cube h side hook up

# Author: Ammar
# Last Edit: 8/15/17
class csvGenerator2(csvGenerator): # class to build csv for verification survey
	def __init__(self):
		super(csvGenerator2, self).__init__()
		super(csvGenerator2, self).setDefaults()
		self.setDefaults()

	def setDefaults(self):
		self.dimensionSizes = {'h':['17'], 'w':['17'], 'e':['17'], 'a':['10']}
		self.questions = [\
		#cube h
		('cube', [17, 17, 17], 'h', '3fingerpinch', 'side', 'up'),\
		('cube', [17, 17, 17], 'h', 'equidistant', 'side', 'up'),\
		('cube', [17, 17, 17], 'h', 'equidistant', 'side', 'down'),\
		('cube', [17, 17, 17], 'h', 'hook', 'side', 'up'),\
		('cube', [17, 17, 17], 'h', 'hook', 'side', '90'),\
		('cube', [17, 17, 17], 'h', '2fingerpinch', 'side', 'up'),\
		('cube', [17, 17, 17], 'h', '3fingerpinch', 'top', 'up'),\
		('cube', [17, 17, 17], 'h', '3fingerpinch', 'top', 'angled'),\
		('cube', [17, 17, 17], 'h', 'equidistant', 'top', 'up'),\
		('cube', [17, 17, 17], 'h', 'equidistant', 'top', 'angled'),\
		('cube', [17, 17, 17], 'h', '2fingerpinch', 'top', 'up'),\
		('cube', [17, 17, 17], 'h', '2fingerpinch', 'top', 'angled'),\
		#cylinder h
		('cylinder', [17, 17, 17], 'h', '3fingerpinch', 'side', 'up'),\
		('cylinder', [17, 17, 17], 'h', 'equidistant', 'side', 'up'),\
		('cylinder', [17, 17, 17], 'h', 'equidistant', 'side', 'down'),\
		('cylinder', [17, 17, 17], 'h', 'hook', 'side', 'up'),\
		('cylinder', [17, 17, 17], 'h', 'hook', 'side', '90'),\
		('cylinder', [17, 17, 17], 'h', '2fingerpinch', 'side', 'up'),\
		('cylinder', [17, 17, 17], 'h', '3fingerpinch', 'top', 'up'),\
		('cylinder', [17, 17, 17], 'h', 'equidistant', 'top', 'up'),\
		('cylinder', [17, 17, 17], 'h', '2fingerpinch', 'top', 'up'),\
		#cylinder w/e
		('cylinder', [17, 17, 17], 'e', 'equidistant', 'side', 'up'),\
		('cylinder', [17, 17, 17], 'w', '3fingerpinch', 'side', 'up'),\
		('cylinder', [17, 17, 17], 'e', 'hook', 'side', 'up'),\
		('cylinder', [17, 17, 17], 'e', 'hook', 'side', '90'),\
		('cylinder', [17, 17, 17], 'w', '2fingerpinch', 'side', 'up'),\
		('cylinder', [17, 17, 17], 'e', 'equidistant', 'top', 'up'),\
		('cylinder', [17, 17, 17], 'e', 'equidistant', 'top', 'angled'),\
		('cylinder', [17, 17, 17], 'w', '3fingerpinch', 'top', 'up'),\
		('cylinder', [17, 17, 17], 'e', '3fingerpinch', 'top', 'up'),\
		('cylinder', [17, 17, 17], 'w', '2fingerpinch', 'top', 'up'),\
		# ellipse h
		('ellipse', [17, 17, 17], 'h', 'equidistant', 'side', 'up'),\
		('ellipse', [17, 17, 17], 'h', '3fingerpinch', 'side', 'up'),\
		('ellipse', [17, 17, 17], 'h', 'hook', 'side', 'up'),\
		('ellipse', [17, 17, 17], 'h', 'hook', 'side', '90'),\
		('ellipse', [17, 17, 17], 'h', '2fingerpinch', 'side', 'up'),\
		('ellipse', [17, 17, 17], 'h', 'equidistant', 'top', 'up'),\
		('ellipse', [17, 17, 17], 'h', '3fingerpinch', 'top', 'up'),\
		('ellipse', [17, 17, 17], 'h', '2fingerpinch', 'top', 'up'),\
		# cone h
		('cone', [17, 17, 17, 10], 'h', 'equidistant', 'side', '90'),\
		('cone', [17, 17, 17, 10], 'h', 'equidistant', 'side', 'up'),\
		('cone', [17, 17, 17, 10], 'h', '3fingerpinch', 'side', 'up'),\
		('cone', [17, 17, 17, 10], 'h', 'hook', 'side', '90'),\
		('cone', [17, 17, 17, 10], 'h', '2fingerpinch', 'side', 'up'),\
		('cone', [17, 17, 17, 10], 'h', 'equidistant', 'top', 'up'),\
		('cone', [17, 17, 17, 10], 'h', '3fingerpinch', 'top', 'up'),\
		('cone', [17, 17, 17, 10], 'h', '2fingerpinch', 'top', 'up'),\
		#cone w/e
		('cone', [17, 17, 17, 10], 'e', 'equidistant', 'side', 'up'),\
		('cone', [17, 17, 17, 10], 'e', '3fingerpinch', 'side', 'up'),\
		('cone', [17, 17, 17, 10], 'e', '2fingerpinch', 'side', 'up'),\
		('cone', [17, 17, 17, 10], 'e', 'equidistant', 'top', '90'),\
		('cone', [17, 17, 17, 10], 'e', 'equidistant', 'top', 'up'),\
		('cone', [17, 17, 17, 10], 'e', '3fingerpinch', 'top', 'up'),\
		('cone', [17, 17, 17, 10], 'e', '2fingerpinch', 'top', 'up'),\

		]

	def getURL(self, shape, size, object_or, grasp, approach, hand_or): # get a url based on features
		URL = self.baseURL + shape + '_'
		URL += 'h%s_w%s_e%s_' %(size[0], size[1], size[2])
		if shape == 'cone':
			URL += 'a%s_' %size[3]
		URL += object_or + '_'
		URL += grasp + '_'
		URL += approach + '_'
		URL += hand_or + '.png'
		return URL

	def generatorQuestions(self): # generator for returning parameters for building URLs
		for question in self.questions:
			shape, size, object_or, grasp, approach, hand_or = question
			yield shape, size, object_or, grasp, approach, hand_or
		print("uhoh! should not get to this point in generator")
		return

	def createCSV(self, csvfilename): #writes questions to csv file
		try:
			os.remove(csvfilename)
			print('Overwriting existing file')
		except:
			print('File does not exist')
		Qgen = self.generatorQuestions()
		for __ in self.questions: #just to keep going until questions run out
			with open(csvfilename, 'a') as f:
				self.csvwriter = csv.writer(f)
				shape, size, object_or, grasp, approach, hand_or = Qgen.next()
				URL = self.getURL(shape, size, object_or, grasp, approach, hand_or)
				print(URL)
				self.csvwriter.writerow([URL])

	def createMappingCSV(self, csvfilename):
	#this mapping is used to when analyzing data to know which values
	# to replace from loop and merge
		try:
			os.remove(csvfilename)
			print('Overwriting existing file')
		except:
			print('File does not exist')
		Qgen = self.generatorQuestions()
		count = 1
		shape_prev = None
		objector_prev = None
		object_or_label = None
		for __ in self.questions: #just to keep going until questions run out
			with open(csvfilename, 'a') as f:
				self.csvwriter = csv.writer(f)
				shape, size, object_or, grasp, approach, hand_or = Qgen.next()
				if object_or == 'w' or object_or == 'e': #deals with cases when on its side
					object_or_label = 'w/e'
				else:
					object_or_label = 'h'
				if shape_prev != shape or objector_prev != object_or_label:
					count = 1
				print('Shape: %s' %shape)
				# pdb.set_trace()
				shape_prev = shape
				objector_prev = object_or_label
				# record object orientation also
				self.csvwriter.writerow(['${lm://Field/%s}' %count, '%s %s' %(shape, object_or_label), '%s %s %s %s' %(object_or, approach, grasp, hand_or) ])
				count += 1







class fileInterface(object):
	#Class that handles reading and writing of qsf and csv Files

	def __init__(self, csvFile, qsfFile, finalFile=None):
		#csvFile, qsfFile, and finalFile are all file Names/Locations from where to read and write
		self.csvFile = csvFile
		self.qsfFile = qsfFile
		if finalFile ==None:
			self.outputFile = qsfFile
		else:
			self.outputFile = finalFile

	def readOriginalQSF(self):
		#returns the entire text of the .qsf as a string
		inputFile = open(self.qsfFile, "r");
		fullFileText = inputFile.read();
		inputFile.close();
		return fullFileText;

	def writeFinalQSF(self, result):
		#result is a string that includes the entire new qsf text
		#overrights the .qsf file with the new, filled in, text
		outputFile = open(self.outputFile, "w");
		outputFile.write(result);
		outputFile.close();

	def readCSV(self):
		#Generator to read the URLs row by row
		with open(self.csvFile) as csvfile:
			reader = csv.reader(csvfile)
			for row in reader:
				yield row
	
	def generateCSV(self):
		#generates an entire csv file based on the defaults set in the csvGenerator class
		cg = csvGenerator()
		cg.generateCSV(self.csvFile)


class qsfFiller(object):
	#Takes a qsfFile and a csvFile and fills in the blank Loop Merge Spots with the entries in the first column of the csv File
	def __init__(self, csvFile, qsfFile, finalFile=None):
		self.setDefaults()
		self.fileInterface = fileInterface(csvFile, qsfFile, finalFile)
		# self.fileInterface.generateCSV()

	def setDefaults(self):
		#These macros are constants based on the format of a .qsf file
		#The Keyword begins every block's fields
		self.keyword = "Static\":"
		#The Blank location is where the urls need to be filled in
		self.blankLocation = "\"\""
		#The end question is the point at which all the fields for the block have come before
		self.endBlock = "}}"

	def fillIn(self):
		#gets the new string that is to be written to the new qsf file
		self.startParsingFiles()
		currentIndex = self.fillInLoopMerge()
		self.finishNewQSF(currentIndex)

	def startParsingFiles(self):
		#The provided files are set in the main
		self.fullFileText = self.fileInterface.readOriginalQSF();
		self.csvGenerator = self.fileInterface.readCSV();
	
	def fillInLoopMerge(self):
		#Finds all the blanks in the loop merge and fills them in from the csv
		#returns the index at the end of all the loop merge values
		self.result = "";
		currentIndex = 0;
		keywordStartIndex = self.fullFileText.find(self.keyword)
		while self.thereAreMoreBlocksToBeFilled(keywordStartIndex):
			currentIndex = self.fillInBlock(keywordStartIndex, currentIndex)
			keywordStartIndex = self.fullFileText.find(self.keyword, currentIndex)
			print('Index: %s' %keywordStartIndex)
		return currentIndex

	def thereAreMoreBlocksToBeFilled(self, keywordStartIndex):
		return keywordStartIndex != -1
		
	def thereIsAnotherBlankInBlock(self, replacementStartIndex, closingBracketIndex):
		return (replacementStartIndex < closingBracketIndex) and (replacementStartIndex != -1)

	def fillInBlock(self, keywordStartIndex, currentIndex):
		#keywordStartIndex is an int and currentIndex is an int
		#fills in all the blank spots with the corresponding url within one block's section
		closingBracketIndex = self.fullFileText.find(self.endBlock, keywordStartIndex)
		replacementStartIndex = self.fullFileText.find(self.blankLocation, keywordStartIndex)+1
		while self.thereIsAnotherBlankInBlock(replacementStartIndex, closingBracketIndex):
			currentIndex,replacementStartIndex = self.fillInBlankURL(currentIndex, replacementStartIndex)
		return currentIndex

	def fillInBlankURL(self, currentIndex, replacementStartIndex):
		#currentIndex and replacementStartIndex are ints
		#fills in a blank spot with the next URL in the csv with the necessary additions
		ImageFileURL = self.getNextURLFromCSV();
		self.result = "{}{}<img src={} />".format(self.result, self.fullFileText[int(currentIndex): int(replacementStartIndex)], ImageFileURL)
		currentIndex = replacementStartIndex
		replacementStartIndex = self.fullFileText.find(self.blankLocation, currentIndex+2)+1
		return currentIndex, replacementStartIndex

	def getNextURLFromCSV(self):
		#gets the next URL from the csv and changes all '/' to '\/' so that the qualtrics can read it
		csvURL = next(self.csvGenerator)[0];
		csvURL = csvURL.replace("/", "\/");
		print('CSV URL: %s' %csvURL)
		return csvURL;
	
	def finishNewQSF(self,currentIndex):
		#Once all blanks have been filled, copy the rest of the file onto the end of the string
		#Overwrite the original .qsf with the new, filled in text
		self.result += self.fullFileText[int(currentIndex):]
		self.fileInterface.writeFinalQSF(self.result)

if __name__ == "__main__":
	curdir = os.path.dirname(os.path.realpath(__file__))
	# qsfFileName = curdir + "/Near_Contact_20.qsf"
	# outputQSF = curdir + "/NC20.qsf"
	# csvFileName = curdir + "/imageFiles.csv"
	# qF = qsfFiller(csvFileName, qsfFileName, outputQSF)
	# qF.fillIn()

	#### Verification
	# print(CG2.getURL('cube', [17, 17, 17], 'h', 'equidistant', 'side', 'up'))
	# folder_dir = curdir + '/Near Contact 2.0 - Verification/'
	csvFileName = folder_dir + 'imageFiles.csv'
	CG2 = csvGenerator2()
	CG2.createCSV(csvFileName)
	mappingCSV = folder_dir + 'mapping.csv'
	CG2.createMappingCSV(mappingCSV)
	# qsfFileName = folder_dir + 'Near_Contact_20_-_Verification.qsf'
	# outputQSF = qsfFileName.replace('.qsf', '_filled.qsf')
	# qF = qsfFiller(csvFileName, qsfFileName, outputQSF)
	# qF.fillIn()

	### Follow up survey
	# folder_dir = curdir + '/Near Contact 2.0 - Followup/'
	# csvFileName = folder_dir + 'imageFiles.csv'
	# CG2 = csvGenerator2_1()
	# CG2.generateCSV(csvFileName)
	# # mappingCSV = folder_dir + 'mapping.csv'
	# # CG2.createMappingCSV(mappingCSV)
	# qsfFileName = folder_dir + 'Near_Contact_20 - followup.qsf'
	# outputQSF = qsfFileName.replace('.qsf', '_filled.qsf')
	# qF = qsfFiller(csvFileName, qsfFileName, outputQSF)
	# qF.fillIn()

