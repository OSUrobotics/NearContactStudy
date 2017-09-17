import os
import pdb
import sys
import csv
import copy
import numpy as np
from NearContactStudy import csvReader, dataResults, removeUnfinishedRows, removeUnnecessaryColumns


class DataProcessing(object):
	def __init__(self, filename, mapping_filename = None):
		i = 1
		self.dR = dataResults()
		self.csvR = csvReader(filename, self.dR)
		self.csvR.readCSV()
		removeUnfinishedRows(self.dR)
		self.parseAllQuestions()
		if mapping_filename:
			self.replaceLMVarWithGrasp(mapping_filename)
		self.writeResponseToCSV()
		self.writeAllResponseToCSV()
		# self.summarizeResponses('AllResponses.csv', 'Analyzed.csv', ignore_columns = 3, ignore_rows = 1)
		self.aggregateReponses()
		pdb.set_trace()

	def responseDicts(self):
		self.response_count = len(self.dR.data['workerId: workerId'])
		response_dict = {'WorkerID':[], \
						'Cube h':self.questionDict(),\
						'Cylinder h':self.questionDict(),\
						'Cylinder w/e':self.questionDict(),\
						'Cone h':self.questionDict(),\
						'Cone w/e':self.questionDict(),\
						'Ellipse h': self.questionDict()}
		self.response_list = []
		for i in range(self.response_count):
			self.response_list.append(copy.deepcopy(response_dict))

	def questionDict(self): #returns a dictionary for storing the answers
		question_dict = {'Viable': dict(), 'Confidence': dict(), 'Rank': dict()}
		return copy.deepcopy(question_dict)

	def parseWorkerID(self): #finds field for worker id and parses them out
		worker_ids = self.dR.data['workerId: workerId']
		for i in range(self.response_count):
			self.response_list[i]['WorkerID'] = worker_ids[i]

	def parseQuestion(self, question): #parses the questions(keys) of the dictionary
		q_type = question.split(' ', 1)[0].strip()
		o_type = question.split(' ', 1)[1].split('_', 1)[0].strip()
		r_type = question.rsplit('-', 1)[1].strip()
		return q_type, o_type, r_type

	def storeResponse(self, resp, feat): #enters the response into the dictionary based on parsed features from parseQuestion
		for i in range(self.response_count):
			if 'Con' in feat[1]:
				if 'w/e' in feat[1]:
					o_type = 'Cone w/e'
				elif 'h' in feat[1]:
					o_type = 'Cone h'
			elif 'Ell' in feat[1]:
				o_type = 'Ellipse h'
			elif 'Cyl' in feat[1]:
				if 'h' in feat[1]:
					o_type = 'Cylinder h'
				elif 'w/e' in feat[1]:
					o_type = 'Cylinder w/e'
			elif 'Cube' in feat[1]:
				o_type = 'Cube h'
			else:
				return
			self.response_list[i][o_type][feat[0]][feat[2]] = resp[i]

	def writeResponseToCSV(self): #writes values from response_list to csv files with workerIDs
		keygen = self.keyGenerator(self.response_list[0])
		for i in range(self.response_count):
			file_name = self.response_list[i]['WorkerID'] + '.csv'
			with open(file_name, 'wb') as worker_file:
				writer = csv.writer(worker_file)
				for keys in keygen:
					k1, k2, k3 = keys
					writer.writerow([k1, k2, k3, self.response_list[i][k1][k2][k3]])

	def writeAllResponseToCSV(self): #writes values from all entries response_list to one csv file with workerIDs as header
		keygen = self.keyGenerator(self.response_list[0])
		file_name = 'AllResponses.csv'
		with open(file_name, 'wb') as all_file:
			writer = csv.writer(all_file)
			headers = ['Shape', 'Question Type', 'Grasp Choice']
			for i in range(self.response_count):
				headers.append(self.response_list[i]['WorkerID'])
			writer.writerow(headers)
			for keys in keygen:
				k1, k2, k3 = keys
				for i in range(self.response_count):
					keys.append(self.response_list[i][k1][k2][k3])
				writer.writerow(keys)

	def keyGenerator(self, search_dict): #generates the deepest dictioanary key as an ordered list. Hardcoded to be three levels deep, so not very flexible
		for k1,v1 in search_dict.iteritems():
			if isinstance(v1, dict): #checks for worker ID
				for k2,v2 in v1.iteritems():
					for k3,v2 in v2.iteritems():
						yield [k1, k2, k3]

	def parseAllQuestions(self): #parses all the questions in self.data
		self.responseDicts()
		self.parseWorkerID()
		for question in self.dR.data.keys():
			try:
				q,o,r = self.parseQuestion(question)
				self.storeResponse(self.dR.data[question], [q, o ,r])
			except IndexError:
				continue

	def replaceLMVarWithGrasp(self, filename):
		#replaces the loop and merge variables with the name of the grasp
		#this mapping should be generated when creating the survey
		#load values from mapping into dictionary
		filename = os.path.abspath(filename)
		LMV_dict = dict()
		with open(filename, 'rb') as csvfile:
			reader = csv.reader(csvfile)
			for row in reader:
				LMV_dict['%s %s' %(row[1], row[0])] = row[2]
		self.LMV_dict = LMV_dict
		# walk through dictionary and replace LM values for each response
		for resp in self.response_list:
			self.searchDict(resp)

	def searchDict(self, search_dict, shape = None):
		# searches for LM values and replaces it from the loaded mapping
		for k, v in search_dict.iteritems():
			if '$' in k:
				pre_size = len(search_dict.keys())
				# if '%s %s' %(shape, k) == 'ellipse h ${lm://Field/4}':
				# 	pdb.set_trace()
				search_dict[self.LMV_dict['%s %s' %(shape, k)]] = search_dict.pop(k)
				post_size = len(search_dict.keys())
				# print("Shape: %s,  LM Val: %s, Replace: %s" %(shape, k, self.LMV_dict['%s %s' %(shape, k)]))
				# print("Dict Length Change: %s" %(post_size - pre_size))
				if (post_size - pre_size) < 0:
					pdb.set_trace()
			if isinstance(v, dict):
				if k == 'Cone w/e':
					shape = k.lower()
				elif k == 'Cone h':
					shape = k.lower()
				elif k == 'Cube h':
					shape = k.lower()
				elif k == 'Cylinder w/e':
					shape = k.lower()
				elif k == 'Cylinder h':
					shape = k.lower()
				elif k == 'Ellipse h':
					shape = k.lower()
				self.searchDict(v, shape)

	def aggregateReponses(self): #aggregate responses from multiple users
		agg_dict = self.copyRecursiveDict(self.response_list[0])
		keygen = self.keyGenerator(agg_dict)
		for keys in keygen:
			k1, k2, k3 = keys
			for i in range(0,self.response_count):
				try:
					agg_dict[k1][k2][k3] += self.response_list[i][k1][k2][k3]
					# print(self.response_list[i][k1][k2][k3])
				except:
					print('Blank: %s' %self.response_list[i][k1][k2][k3])
						# print("Keys: %s" %(keys))
						# print("Value: %s" %(self.response_list[1][k1][k2][k3]))
		self.agg_dict = agg_dict

	def summarizeResponses(self, csv_file_in, csv_file_out, ignore_columns = 3, ignore_rows = 1): #takes a csv file and provides some analysis in the last column.  writes out to new csv file
		open_style = 'wb'
		def writeOut(line): #writes a line to the out file
			with open(csv_file_out, open_style) as out_file:
				writer = csv.writer(out_file)
				writer.writerow(line)

		out_file_holder = []
		with open(csv_file_in, 'rb') as in_file:
			reader = csv.reader(in_file)
			header = next(reader) # assumes first row is header
			header.extend(['Total', 'Average', 'Standard Deviation'])
			writeOut(header)
			open_style = 'ab'
			for i in range(ignore_rows - 1):
				reader.next()
			for row in reader:
				total = 0
				count = 0
				vals = []
				for val in row:
					try:
						vals.append(int(val))
					except:
						continue
				if vals != []:
					total = np.sum(vals)
					avg = np.mean(vals)
					stdev = np.std(vals)
					row.extend([total, avg, stdev])
				writeOut(row)
				# pdb.set_trace()

	def copyRecursiveDict(self, d): #copy a recursive dictionary and sets all values to []
		for k, v in d.iteritems():
			if isinstance(v, dict):
				self.copyRecursiveDict(v)
			else:
				d[k] = []
		return d

if __name__ == '__main__':
	DP = DataProcessing('Near_Contact_20__Verification_filled_results.csv', '../../QualtricsGeneration/Near Contact 2.0 - Verification/mapping.csv')

