import json
from pprint import pprint
import pdb
import copy
from collections import OrderedDict
import random, string


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
							u'ForceResponse': u'OFF'}
						}, 
					u'QuestionText': u'Please choose the grasps that you think will work.', 
					u'Language': [], 
					u'GradingData': [], 
					u'Selector': u'MACOL', 
					u'QuestionDescription': u'Please choose the grasps that you think will work.', 
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
						 u'NumColumns': 2}
						 } 
					},
				# # next element in list
				# {u'SecondaryAttribute': u'Please choose the grasps that you think will work.',
				# u'TertiaryAttribute': None, 
				# u'Element': u'SQ', 
				# u'SurveyID': u'SV_6uotxyaL1nZukqV', 
				# u'Payload': 
				# 	{u'QuestionType': u'MC', 
				# 	 u'QuestionID': u'QID2', 
				# 	 u'Validation': 
				# 	 	{u'Settings': 
				# 	 		{u'ForceResponseType': u'ON', 
				# 	 		 u'Type': u'None', 
				# 	 		 u'ForceResponse': u'OFF'}
				#  		 }, 
		 	# 	 	u'QuestionText': u'Please choose the grasps that you think will work.', 
		 	# 	 	u'Language': [], 
		 	# 	 	u'GradingData': [], 
		 	# 	 	u'Selector': u'MACOL', 
		 	# 	 	u'QuestionDescription': u'Please choose the grasps that you think will work.', 
		 	# 	 	u'DefaultChoices': False, 
		 	# 	 	u'ChoiceOrder': [u'1', u'2', u'3'], 
		 	# 	 	u'SubSelector': u'TX', 
		 	# 	 	u'DataExportTag': u'Q2', 
		 	# 	 	u'Choices': 
		 	# 	 		{u'1': 
		 	# 	 			{u'Display': u'${lm://Field/1}'}, 
	 		#  			u'3': 
	 		#  				{u'Display': u'Click to write Choice 3'}, 
 		 # 				u'2': {u'Display': u'${lm://Field/2}'}
	 		# 		}, 
	 		# 		u'Configuration': 
	 		# 			{u'QuestionDescriptionOption': u'UseText', 
	 		# 			u'NumColumns': 2}, 
 			# 		u'QuestionText_Unsafe': u'Please choose the grasps that you think will work.'
 			# 		}, 
				# u'PrimaryAttribute': u'QID2'}
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


class TestSurveyParser(object):
	def __init__(self):
		i = 1


	def loadJSON(self, FN = 'TestBoundryRefinement.qsf'):
		with open(FN, 'r') as survey_file:
			self.survey_in = json.load(survey_file)
			# self.survey_in = json.load(survey_file, object_pairs_hook=OrderedDict)

	def writeJSON(self, FN, json_dict): # writes a dictionary in JSON format to file
		with open(FN, 'w') as out_file:
			json.dump(json_dict, out_file)

	def changeSurveyName(self, json_dict): #changes survey name
		json_dict['SurveyEntry']['SurveyName'] += '-Auto'

	def getSurveyBL(self, json_dict): #returns the section of the survey that holds the loop and merge stuff
		return json_dict['SurveyElements'][0]

	def getSurveySQ(self, json_dict): # returns individual questions (blocks?) for survey
		total_length = len(json_dict['SurveyElements'])
		num_qs = total_length - 7
		self.SQ = [json_dict['SurveyElements'][i] for i in range(total_length-num_qs, total_length)]
		return self.SQ

	def createMultiChoiceQuest(self, num_opts = 3, opts = None, QID = 1): #creates a multichoice question in qualtrics format
		new_quest = copy.deepcopy(multi_choice[0])
		new_block = copy.deepcopy(blockelement)
		#insert choices
		new_quest['Payload']['Choices']  = OrderedDict()
		new_quest['Payload']['ChoiceOrder'] = []
		for i in range(0, num_opts): #these should be loop merge values
			new_quest['Payload']['Choices'][str(i+1)] = OrderedDict({'Display'.encode('ascii', 'ignore'): opts[i].encode('ascii', 'ignore')})

		# change choice order
		new_quest['Payload']['ChoiceOrder'] = ['%s'.encode('ascii', 'ignore') %(i+1) for i in range(0, num_opts)]

		# change QID
		QID_str = 'QID%s'.encode('ascii', 'ignore') %QID
		new_quest['PrimaryAttribute'] = QID_str
		new_quest['Payload']['QuestionID'] = QID_str

		#change QID in block
		new_block['BlockElements'][0]['QuestionID'] = QID_str

		#change choices in block
		new_block['Options']['LoopingOptions']['Static'] = {'1':OrderedDict()}
		for i in range(0, num_opts):
			new_block['Options']['LoopingOptions']['Static']['1']['%s'.encode('ascii', 'ignore') %(i+1)] = opts[i].encode('ascii', 'ignore')

		#change block name
		new_block['Description'] = 'BlockName-Auto'.encode('ascii', 'ignore')

		#change blockID
		new_block['ID'] = self.genID()

		# add to flow
		new_flow = copy.deepcopy(flowelement)
		new_flow['ID'] = new_block['ID'] #update ID



		return new_quest, new_block, new_flow

	def addQuestion(self, quest, block, flow, json_dict): #adds question to a qsf file
		json_dict['SurveyElements'].append(quest)
		block_key = max([int(i) for i in json_dict['SurveyElements'][0]['Payload'].keys()] )
		json_dict['SurveyElements'][0]['Payload'][str(block_key)] = block
		flow['FlowID'] = self.getNextFlow(json_dict)

		pdb.set_trace()
		json_dict['SurveyElements'][1]['Payload']['Flow'].append(flow)
		pdb.set_trace()

	def genID(self):
		new_ID = 'BL_' + ''.join(random.choice(string.ascii_uppercase + string.digits + string.ascii_lowercase) for _ in range(15))
		return new_ID

	def getNextFlow(self, json_dict): #get next available flow ID
		flow_ids_taken = []
		for f in json_dict['SurveyElements'][1]['Payload']['Flow']:
			flow_ids_taken.append(int(f['FlowID'].strip('FL_')))
		next_id = max(flow_ids_taken) + 1
		return 'FL_%s' %(next_id)




	# def QIDgenerator(self):


if __name__ == '__main__':
	TSP = TestSurveyParser()
	# TSP.loadJSON('TestBoundryRefinement-1quest.qsf')
	TSP.loadJSON('SimplerSurvery.qsf')
	# TSP.writeJSON('WriteTest.qsf', TSP.survey_in)
	# print(TSP.getSurveySQ(TSP.survey_in))
	# pprint(multi_choice)
	quest, block, flow = TSP.createMultiChoiceQuest(num_opts = 5, opts = ['option%s' %i for i in range(1,6)], QID = 13)
	TSP.addQuestion(quest, block, flow, TSP.survey_in)

	pdb.set_trace()
	TSP.changeSurveyName(TSP.survey_in)
	TSP.writeJSON('WriteTest.qsf', TSP.survey_in)


