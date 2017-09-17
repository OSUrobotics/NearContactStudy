import json
from pprint import pprint
import pdb
import copy
from collections import OrderedDict
import random, string
import numpy as np

multi_choice = [{u'PrimaryAttribute': u'QID1',
				u'SecondaryAttribute': u'Please choose the grasps that you think will work.', 
				u'TertiaryAttribute': None, u'Element': u'SQ', 
				u'SurveyID': u'SV_6uotxyaL1nZukqV', 
				u'Payload': 
					{u'QuestionType': u'MC', 
					u'QuestionID': u'QID1', 
					u'Validation': 
						{u'Settings': 
							{u'ForceResponseType': u'ON', 
							u'Type': u'None', 
							u'ForceResponse': u'ON'}
						}, 
					u'QuestionText': u'Please choose the grasps that you think will be able to pick the object up, move it a short distance, and place the object down.', 
					u'Language': [], 
					u'GradingData': [], 
					u'Selector': u'MACOL', 
					u'QuestionDescription': u'Grid Question', 
					u'DefaultChoices': False, 
					u'ChoiceOrder': [u'1', u'2', u'3'], 
					u'SubSelector': u'TX', 
					u'DataExportTag': u'Q1', 
					u'Choices': 
						{u'1': 
							{u'Display': u'${lm://Field/1}'}, 
						u'3': 
							{u'Display': u'Click to write Choice 3'}, 
						u'2': 
							{u'Display': u'${lm://Field/2}'}
							}, 
					u'Configuration': 
						{u'QuestionDescriptionOption': u'UseText', 
						 u'NumColumns': 3}
						 } 
					},
				]
blockelement = {
				u'BlockElements': [
					{u'QuestionID': u'QID2', 
					u'Type': u'Question'
					}
					], 
				u'Options': 
					{u'LoopingOptions': 
						{u'Randomization': u'All', 
						 u'Static': 
						 	{u'1': 
						 		{u'1': u'test1', 
					 			 u'3': u'test3', 
					 			 u'2': u'test2'}, 
				 			 u'2': 
				 			 	{u'1': u'', 
				 			 	 u'3': u'',
				 			 	 u'2': u''}
			 			 	 }
		 			 	}, 
	 			 	u'Looping': u'Static', 
	 			 	u'BlockLocking': False, 
	 			 	u'RandomizeQuestions': u'false'}, 
 			 	u'Type': u'Standard', 
 			 	u'Description': u'BlockName2', 
 			 	u'ID': u'BL_1RpmM9fdiVFjHJH'}

flowelement = {u'FlowID': u'FL_7', u'ID': u'BL_aYklnZspuEajiy9', u'Type': u'Standard'}

#append to data['SurveyElements'][1]['Payload']['Flow']
randomizerelement = {u'EvenPresentation': True,
  u'Flow': [{u'FlowID': u'FL_3',
             u'ID': u'BL_bxx3fud1MvZNI45',
             u'Type': u'Standard'},
            {u'FlowID': u'FL_4',
             u'ID': u'BL_eQL2SexjrwhwR5X',
             u'Type': u'Standard'}],
  u'FlowID': u'FL_5',
  u'SubSet': u'2',
  u'Type': u'BlockRandomizer'}


LM_temp = '${lm://Field/%s}'


class SurveyParser(object):
	def __init__(self):
		i = 1


	def loadJSON(self, FN = 'TestBoundryRefinement.qsf'):
		with open(FN, 'r') as survey_file:
			self.survey_in = json.load(survey_file)
			# self.survey_in = json.load(survey_file, object_pairs_hook=OrderedDict)

	def writeJSON(self, FN, json_dict): # writes a dictionary in JSON format to file
		with open(FN, 'w') as out_file:
			json.dump(json_dict, out_file)

	def changeSurveyName(self, json_dict, name = None): #changes survey name
		if name == None:
			json_dict['SurveyEntry']['SurveyName'] += '-Auto'
		else:
			json_dict['SurveyEntry']['SurveyName'] = name

	def getSurveyBL(self, json_dict): #returns the section of the survey that holds the loop and merge stuff
		return json_dict['SurveyElements'][0]

	def getSurveySQ(self, json_dict): # returns individual questions (blocks?) for survey
		total_length = len(json_dict['SurveyElements'])
		num_qs = total_length - 7
		self.SQ = [json_dict['SurveyElements'][i] for i in range(total_length-num_qs, total_length)]
		return self.SQ

	def createMultiChoiceQuest(self, num_opts = 3, opts = None): #creates a multichoice question in qualtrics format
		new_quest = copy.deepcopy(multi_choice[0])
		new_block = copy.deepcopy(blockelement)
		new_flow = copy.deepcopy(flowelement)

		#insert choices
		new_quest['Payload']['Choices']  = dict()
		new_quest['Payload']['ChoiceOrder'] = []
		for i in range(0, num_opts): #these should be loop merge values
			new_quest['Payload']['Choices'][str(i+1)] = dict({'Display'.encode('ascii', 'ignore'): (LM_temp %str(i+1)).encode('ascii', 'ignore')})
		# change choice order -- this could be changed so that images appear in a grid with None as the last one out, also ensure they are in the originally planned grid layout
		new_quest['Payload']['ChoiceOrder'] = ['%s'.encode('ascii', 'ignore') %(i+1) for i in range(0, num_opts+1)]

		#change choices in block
		new_block['Options']['LoopingOptions']['Static'] = {'1':dict()}
		for i in range(0, num_opts):
			new_block['Options']['LoopingOptions']['Static']['1']['%s'.encode('ascii', 'ignore') %(i+1)] = opts[i].encode('ascii', 'ignore')

		#change block name
		new_block['Description'] = 'BlockName-Auto'.encode('ascii', 'ignore')

		#change blockID
		new_block['ID'] = self.genID()

		# add to flow
		new_flow['ID'] = new_block['ID'] #update ID

		return new_quest, new_block, new_flow

	def addQuestion(self, quest, block, flow, json_dict, randomizer = False, export_ID = None): #adds question to a qsf file
		#update QIDs
		QID = self.getNextQID(self.survey_in)
		QID_str = 'QID%s'.encode('ascii', 'ignore') %QID
		quest['PrimaryAttribute'] = QID_str
		quest['Payload']['QuestionID'] = QID_str
		#change QID in block
		block['BlockElements'][0]['QuestionID'] = QID_str

		#update export ID
		if export_ID is None:
			export_ID = 'Q%s' %QID
		quest['Payload']['DataExportTag'] = export_ID

		json_dict['SurveyElements'].append(quest)
		num_blocks = len(self.survey_in['SurveyElements'][0]['Payload'])
		# block_key = max([int(i) for i in json_dict['SurveyElements'][0]['Payload'][0].keys()] )
		try: #sometimes two blocks appears (maybe because of trashcan?) -- only adds it after the last block
			json_dict['SurveyElements'][0]['Payload'].append(block)
		except:
			keys = json_dict['SurveyElements'][0]['Payload'].keys()
			keys_int = np.array(keys).astype('int')
			block_key = max(keys_int)
			json_dict['SurveyElements'][0]['Payload'][str(block_key + 1)] = json_dict['SurveyElements'][0]['Payload'][str(block_key)]  #moving the comment box til the very end
			json_dict['SurveyElements'][0]['Payload'][str(block_key)] = block

		# json_dict['SurveyElements'][0]['Payload'][str(block_key)] = block
		flow['FlowID'] = self.getNextFlow(json_dict)
		r_loc = 4 #randomizer location in list
		if randomizer:
			try:
				json_dict['SurveyElements'][1]['Payload']['Flow'][r_loc]['Flow'].append(flow)
			except: #first time the block doesn't even exist!
				randomizer_flow_ID = self.getNextFlow(json_dict)
				randomizerelement['FlowID'] = randomizer_flow_ID
				json_dict['SurveyElements'][1]['Payload']['Flow'][r_loc] = copy.deepcopy(randomizerelement)
				json_dict['SurveyElements'][1]['Payload']['Flow'][r_loc]['Flow'] = [flow]
		else:
			json_dict['SurveyElements'][1]['Payload']['Flow'].append(flow)
		return QID_str, export_ID

	def genID(self):
		new_ID = 'BL_' + ''.join(random.choice(string.ascii_uppercase + string.digits + string.ascii_lowercase) for _ in range(15))
		return new_ID

	def getNextFlow(self, json_dict): #get next available flow ID
		flow_ids_taken = []
		for f in json_dict['SurveyElements'][1]['Payload']['Flow']:
			if 'Flow' in f.keys(): #if there are blocks within blocks, then this searches them also
				flow_IDs = self.recursiveGetNextFlow(f)
				flow_ids_taken.extend(flow_IDs[:])
			flow_ids_taken.append(int(f['FlowID'].strip('FL_')))
		next_id = max(flow_ids_taken) + 1
		return 'FL_%s' %(next_id)

	def recursiveGetNextFlow(self, flow_dict): #recursively finds flow IDs
		flow_IDs = []
		for f in flow_dict['Flow']:
			if 'Flow' in f.keys():
				flow_IDs.append(self.recursiveGetNextFlow(f))
			flow_IDs.append(int(f['FlowID'].strip('FL_')))
		return flow_IDs

	def setQCountToBeAsked(self, q_count, json_dict): #changes the number of questions that should be asked in each loop
		json_dict['SurveyElements'][1]['Payload']['Flow'][0]['SubSet'] = str(q_count)


	def getNextQID(self, json_dict): #get next available QID
		max_count = 0
		if isinstance(json_dict['SurveyElements'][0]['Payload'], dict): #if there are additional layers
			for k,v in json_dict['SurveyElements'][0]['Payload'].iteritems():
				for i in v['BlockElements']:
					next_QID = int(i['QuestionID'].strip('QID'))
					max_count = max(max_count, next_QID)
		else:
			for i in json_dict['SurveyElements'][0]['Payload']:
				try:
					next_QID = int(i['BlockElements'][0]['QuestionID'].strip('QID'))
					max_count = max(max_count, next_QID)
				except:
					pass
		return max_count+1

	def loadBaseSurvey(self, fn):
		self.loadJSON(fn)

if __name__ == '__main__':
	TSP = SurveyParser()
	# TSP.loadJSON('TestBoundryRefinement-1quest.qsf')
	# TSP.loadJSON('TestBoundryRefinement.qsf')
	# TSP.loadJSON('2Quest.qsf')
	TSP.loadJSON('RandomFlow.qsf')
	# TSP.writeJSON('WriteTest.qsf', TSP.survey_in)
	# print(TSP.getSurveySQ(TSP.survey_in))
	# pprint(multi_choice)
	TSP.changeSurveyName(TSP.survey_in)
	for i1 in range(5):
		quest, block, flow = TSP.createMultiChoiceQuest(num_opts = 5, opts = ['option%s' %i for i in range(1,6)])
		TSP.addQuestion(quest, block, flow, TSP.survey_in, randomizer = True)

	TSP.writeJSON('WriteTest.qsf', TSP.survey_in)


