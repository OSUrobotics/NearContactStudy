import csv
import pdb
import numpy as np
import platform
import os

class ParseGraspData(object):


	def __init__(self):
		self.val_grasp_file = list()
		self.val_grasp_data = list()
		self.all_transforms = list()
		self.output_data = list()
		if platform.node() == 'Sonny':
			self.fn_root = '/home/sonny/Desktop/'
		if platform.node() == 'Desktop':
			self.fn_root = os.path.dirname(os.path.realpath(__file__)) + '/'
		else:
			self.fn_root = 'C:\Users\KothariAmmar\Documents\Grasping Lab\Interpolate Grasps\\'
		self.fn_grasp_file = self.fn_root + 'all_grasp_file.csv'
		self.fn_grasp_data = self.fn_root + 'all_grasp_data.csv'
		# self.parseAllTransforms()


	def parseGraspFile(self):
		with open(self.fn_grasp_file, 'rb') as csv_file:
			reader = csv.reader(csv_file, delimiter = ',')
			for row in reader:
				self.val_grasp_file.append(np.array(row).astype('float'))

			self.val_grasp_file = np.array(self.val_grasp_file)

	def parseGraspData(self):
		with open(self.fn_grasp_data, 'rb') as csv_file:
			reader = csv.reader(csv_file, delimiter = ',')
			for row in reader:
				val_grasp_data = dict()
				val_grasp_data['obj'] = row[0] #TODO: fix this so that it is an int
				val_grasp_data['sub'] = row[1] #TODO: fix this so that it is an int
				val_grasp_data['grasp'] = row[2] #TODO: fix this so that it is an int
				val_grasp_data['type'] = row[3]
				val_grasp_data['HandRotation'] = self.text2Array(row[4]) #TODO: make these into single transform
				val_grasp_data['HandPosition'] = self.text2Array(row[5])
				val_grasp_data['ObjPosition'] = self.text2Array(row[7]) #TODO: make these into single transform
				val_grasp_data['ObjRotation'] = self.text2Array(row[8])

				try:
					val_grasp_data['array3'] = self.text2BigArray(row[6])
					
				except:
					print("issue?")
					print(val_grasp_data)

				self.val_grasp_data.append(val_grasp_data)

	def text2Array(self, s):
		out = s.strip('[]') # remove brackets
		out = out.split(',') # split up into individual values
		out = np.array(out).astype('float') # convert to floats
		return out

	def text2BigArray(self,s):
		# this is specifically for that one array that seems to change randomly.
		# i don't even know what it is for!
		try:
			out = s.split(']')
			out1 = out[0].strip('[')
			out1 = out1.split(',')
			out1 = np.array(out1).astype('float')
			out2 = out[1].strip(', [')
			out2 = out2.split(',')
			out2 = np.array(out2).astype('float')
			return np.vstack((out1, out2))
		except:
			out = s.strip('[]')
			if out != '':
				out = out.split(',')
				out = np.array(out).astype('float')
			return out
			
	def writeDict(self, dict_in, save_fn):
		fn = self.fn_root + save_fn
		with open(fn, 'wb') as csvfile:
			fieldnames = dict_in[0].keys()
			writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
			writer.writeheader()
			for v in dict_in:
				writer.writerow(v)

	def findGrasp(self, objnum = None, subnum  = None, grasptype  = None, graspnum  = None, graspclass = None, list2check = None):
		if list2check is None:
			out_dict = self.val_grasp_data
		else:
			out_dict = list2check
		if all([v is None for v in [objnum, subnum, grasptype, graspnum]]):
			pass
		else:
			if (objnum is not None):
				lambdaFunc = lambda g,obj = objnum: int(g['obj']) == obj
				out_dict = filter(lambdaFunc, out_dict)
			if (subnum is not None):
				lambdaFunc = lambda g,sub = subnum: int(g['sub']) == sub
				out_dict = filter(lambdaFunc, out_dict)
			if (grasptype is not None):
				lambdaFunc = lambda g,gtype = grasptype: g['type'] == gtype
				out_dict = filter(lambdaFunc, out_dict)
			if (graspnum is not None):
				lambdaFunc = lambda g,gnum = graspnum: int(g['grasp']) == gnum
				out_dict = filter(lambdaFunc, out_dict)
			if (graspclass is not None):
				lambdaFunc = lambda g,gclass = graspclass: g['class'] == gclass
				out_dict = filter(lambdaFunc, out_dict)

		return out_dict

	def parseAllTransforms(self):
		#load from file if it exists
		# save_file = self.fn_root + 'all_transforms_dict.csv'
		# if os.path.isfile(save_file):
		# 	with open(save_file, 'rb') as aft:
		# 		reader = csv.DictReader(aft)
		# 		for row in reader:
		# 			pdb.set_trace()
		# 			row['obj'] = int(row['obj'])
		# 			row['sub'] = int(row['sub'])
		# 			row['grasp'] = int(row['grasp'])
		# 			row['JointAngles'] = np.array(row['JointAngles']).astype(float)
		# 			self.all_transforms.append(row)
		# 	return

		# get file names
		all_transforms_path = self.fn_root + 'all_obj_transformation/'
		FolderList = os.listdir(all_transforms_path)
		FilesList = list()
		for Folder in FolderList:
			subfiles = os.listdir(all_transforms_path + '/' + Folder)
			if len(subfiles) > 1:
				for subf in subfiles:
					FilesList.append(all_transforms_path + Folder + '/' + subf)

		#load files into dictionary
		all_transforms_list = list()
		for f in FilesList:
			T_dict = dict()
			parts = f.split('/')[-1].split('_')
			obj = int(parts[0].strip('obj'))
			sub = int(parts[1].strip('sub'))
			graspnum = int(parts[2].strip('grasp'))
			grasptype = parts[3]
			# check if grasp is already in list
			T_dict['obj'] = obj
			T_dict['sub'] = sub
			T_dict['grasp'] = graspnum
			T_dict['type'] = grasptype

			count_list = self.findDictInList(T_dict, all_transforms_list)
			if count_list == -1:
				all_transforms_list.append(T_dict)

			count = self.findDictInList(T_dict, all_transforms_list)
			try:
				key_name = parts[4].strip('.txt')
				if key_name in all_transforms_list[count].keys():
					print("Overwriting Data")
				if key_name == 'ContactLinkNames':
					with open(f, 'rb') as fc:
						lines = fc.readlines()
						all_transforms_list[count][key_name] = [t.strip('\n') for t in lines]
				else:
					all_transforms_list[count][key_name] = np.genfromtxt(f, delimiter = ',')
			except:
				print("Skipping File")
		self.all_transforms = all_transforms_list

	def findDictInList(self, T_dict, T_list):
		count = 0
		for dict_list in T_list:
			matchFunc = lambda e, x = dict_list, y = T_dict: x[e] == y[e]
			match_array = map(matchFunc, T_dict.keys())
			if all(match_array):
				return count
			count += 1
		return -1 #failed to match anything

	def matricesFromGrasp(self, grasp): # Description: helper function to get individual arrays from dictionary
		HandT = grasp['HandTransformation']
		ObjT = grasp['ObjTransformation']
		Arm_JA = grasp['JointAngles'][:7]
		Hand_JA = grasp['JointAngles'][7:]
		return HandT, ObjT, Arm_JA, Hand_JA

	def parseOutputData(self):
		outputData_folder = self.fn_root + 'output_data_folder/'
		FilesList = self.getAllFiles(outputData_folder)
		all_output_transforms_list = list()
		for f in FilesList:
			T_dict = dict()
			parts = f.split('/')[-1].split('_')
			obj = int(parts[0].strip('obj'))
			sub = int(parts[1].strip('sub'))
			graspnum = int(parts[2].strip('grasp'))
			grasptype = parts[3]
			graspclass = parts[4]
			# check if grasp is already in list
			T_dict['obj'] = obj
			T_dict['sub'] = sub
			T_dict['grasp'] = graspnum
			T_dict['type'] = grasptype
			T_dict['class'] = graspclass
			count_list = self.findDictInList(T_dict, all_output_transforms_list)
			if count_list == -1:
				all_output_transforms_list.append(T_dict)

			count = self.findDictInList(T_dict, all_output_transforms_list)
			try:
				key_name = parts[5].strip('.txt')
				if key_name in all_output_transforms_list[count].keys():
					print("Overwriting Data")
				if key_name == 'ContactLinkNames':
					with open(f, 'rb') as fc:
						lines = fc.readlines()
						all_output_transforms_list[count][key_name] = [t.strip('\n') for t in lines]
				else:
					all_output_transforms_list[count][key_name] = np.genfromtxt(f, delimiter = ',')
			except:
				print("Skipping File")
		self.output_data = all_output_transforms_list

	def getAllFiles(self, directory): # get all files in directory
		FilesList = list()
		for root, dirs, filenames in os.walk(directory):
			if filenames != []:
				for fname in filenames:
					if os.path.splitext(fname)[1] == '.txt': #only want text files
						FilesList.append(root + '/' + fname)

		return FilesList




if __name__ == "__main__":
	pgd = ParseGraspData()
	# pgd.parseGraspFile()
	# pgd.parseGraspData()
	# pgd.findGrasp(objnum = 1, subnum = 7, grasptype = 'optimal0', graspnum = 1)
	# pgd.writeDict(pgd.val_grasp_data, 'all_grasp_data_dict.csv')
	# pgd.parseAllTransforms()
	# pgd.writeDict(pgd.all_transforms, 'all_transforms_dict.csv')
	pgd.parseAllTransforms()
	pgd.parseOutputData()


