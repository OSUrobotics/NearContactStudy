from NearContactStudy import ShapeSTLGeneratorPython
from NearContactStudy import SurveyResultsParser, BuildPolytope
from NearContactStudy import BASE_PATH, HAND_PARAM
from NearContactStudy import HandCenteredCSV
from NearContactStudy import ShapeImageManipulator
import pdb
import numpy as np
import csv
from pprint import pprint
import matplotlib.pyplot as plt
import os



'''
# class RefinementSurveyResultsAnalyzer(object):
# 	def __init__(self):
START_URL = '<img src="http://people.oregonstate.edu/~kotharia/RefinementSurvey/GeneratedImagesReduced/Grasps/'
END_URL = '" style="width: 285px; height: 200px;" />'

SRP = SurveyResultsParser()
results_dict = SRP.loadResults('RefinementSurveyFilled.csv', map_csv = BASE_PATH + '/NearContact20Survey/QualtricsGeneration/Near Contact 2.0 - Refinement/Mapper.csv')
#replace keys with something more readable
for k1,v1 in results_dict.iteritems():
	if k1 == 'ResponseID':
		i = 1
	else:
		for k2,v2 in v1.iteritems():
			scenario = None
			if k2 == 'None':
				scenario = k2
			else:
				scenario = k2.replace(START_URL,'').replace(END_URL,'')
			results_dict[k1][scenario] = results_dict[k1].pop(k2) # replaces key

			results_dict[k1][scenario] = np.array([0 if x == '' else int(x) for x in results_dict[k1][scenario]])

for k1,v1 in results_dict.iteritems():
	if not isinstance(v1, dict):
		continue
	for k2,v2 in v1.iteritems():
		if 'img' in k2:
			scenario = k2.replace(START_URL,'').replace(END_URL,'')
			results_dict[k1][scenario] = results_dict[k1].pop(k2) # replaces key
			results_dict[k1][scenario] = np.array([0 if x == '' else int(x) for x in results_dict[k1][scenario]])


## printed results to file individually ##
for iw, worker in enumerate(results_dict['ResponseID']):
	with open(worker + '.csv', 'wb') as csvfile:
		writer = csv.writer(csvfile)
		for k1,v1 in results_dict.iteritems():
			if not isinstance(v1, dict):
				continue
			for k2,v2 in v1.iteritems():
				row = [k2]
				row.append(v2[iw])
				writer.writerow(row)

# printed all results in file
with open('AllResults.csv', 'wb') as csvfile:
	writer = csv.writer(csvfile)
	headers = ['WorkerID']
	headers.extend(results_dict['ResponseID'])
	writer.writerow(headers)
	for k1, v1 in results_dict.iteritems():
		if not isinstance(v1, dict):
			continue
		for k2,v2 in v1.iteritems():
			row = [k2]
			row.extend(v2)
			writer.writerow(row)

# printed statistics of results
with open('AnalyzedResults.csv', 'wb') as csvfile:
	writer = csv.writer(csvfile)
	headers = ['Shape', 'height', 'width', 'extent', 'obj_or', 'grasp', 'approach', 'hand_or', 'Yes Count', 'Total Count']
	writer.writerow(headers)
	for k1, v1 in results_dict.iteritems():
		if not isinstance(v1, dict):
			continue
		for k2,v2 in v1.iteritems():
			if k2 == 'None':
				continue # i don't really know what value none has for analysis
			row = k2.split('_')
			row[-1] = row[-1].replace('.png', '')
			for i in range(1,4): #convert to floats
				try:
					row[i] = row[i][1:]
					row[i] = row[i].replace('D','.')
					row[i] = float(row[i])
				except:
					pprint(row)
			row.extend([sum(v2), len(v2)])
			writer.writerow(row)

'''
#load analyzed stats and plot points
Confidence_limit = 0.75
total_count = 16
with open('AnalyzedResults.csv', 'rb') as csvfile:
	reader = csv.reader(csvfile)
	headers = next(reader)
	good_list = []
	bad_list = []
	for row in reader:
		dims = np.array(row[1:4]).astype(float)
		if int(row[-2]) < Confidence_limit*total_count:
			bad_list.append(dims)
		else:
			good_list.append(dims)
bad_list = np.array(bad_list)/HAND_PARAM
good_list = np.array(good_list)/HAND_PARAM

#### plot points
fig = plt.figure(figsize = (15, 10))
ax = fig.add_subplot(111, projection='3d')
ax.scatter(good_list[:,0], good_list[:,1], good_list[:,2], c='green')
ax.scatter(bad_list[:,0], bad_list[:,1], bad_list[:,2], c='red')
BP = BuildPolytope()
BP.formatPlot(ax)
hull = BP.fitConvexHull(good_list)
BP.drawPlanesFromHull(good_list, hull, ax, color = np.array([0.5, 0.5, 0.5]))
avg_pts = BP.getAvgPointsOnHull(good_list, hull)
pprint(avg_pts[::3])
ax.figure.subplots_adjust(top=1, bottom=0, left=0, right=1)
ax.set_title('%.0f%% Confidence' %(Confidence_limit*100), fontsize = 40)
ax.tick_params(axis='x', labelsize=30)
ax.tick_params(axis='y', labelsize=30)
ax.tick_params(axis='z', labelsize=30)
ax.set_xlabel('width', fontsize=40)
# ax.xaxis.labelpad = 100
ax.set_ylabel('height', fontsize=40)
ax.set_zlabel('extent', fontsize=40)
plt.tight_layout()
ax.figure.savefig('%s_RefinementPoints.png' %Confidence_limit)
# ax.figure.savefig('%s_RefinementPoints.png' %Confidence_limit, bbox_inches='tight', pad_inches=0)
pdb.set_trace()

# ax.legend(['High Preference', 'Low Preference', 'Refined Surface', 'Original Surface'])

# import matplotlib.patches as mpatches
# dummy_patches = mpatches.Patch(color = 'green', label = 'High Preference')
# ax.legend(dummy_patches)
# plt.show()


##### Load data and create questions for next survey #####
Confidence_limit = 0.75
total_count = 16
with open('AnalyzedResults.csv', 'rb') as csvfile:
	reader = csv.reader(csvfile)
	headers = next(reader)
	good_list = []
	bad_list = []
	for row in reader:
		dims = np.array(row[1:4]).astype(float)
		if int(row[-2]) < Confidence_limit*total_count:
			bad_list.append(dims)
		else:
			good_list.append(dims)
bad_list = np.array(bad_list)/HAND_PARAM
good_list = np.array(good_list)/HAND_PARAM

BP = BuildPolytope()
hull = BP.fitConvexHull(good_list)
center_pt = np.mean([hull.points[i] for i in hull.vertices], axis = 0)
variation = np.array([[-0.02318219,  0.00311785, -0.0220723 ],
					[-0.00228904,  0.01373779,  0.00194441],
					[ 0.0172397 , -0.02085008,  0.00817173]])
# variation = (0.5 - np.random.rand(3,3))/20 #should be no more than 0.05 (1.5 cm)
nms = [eqs for eqs in np.unique(hull.equations, axis = 0)]
vectors = variation
yes_pts = []
spacing_range = [0, 0.1, 0.2]
for iv,v in enumerate(vectors):
	for delta in spacing_range:
		yes_pts.append(v*(1+delta) + center_pt)
yes_pts = np.array(yes_pts)

border_pts = []
# for v in vectors:
# 	for nm in nms:
# 		t = -(np.dot(center_pt,nm[0:3])+nm[3]) / np.dot(v,nm[0:3])
# 		if abs(t) < 10:
# 			border_pts.append(v * t + center_pt)
spacing = [3,9,4]
spacing_range = [0, 0.1, 0.2]
for iv,v in enumerate(vectors):
	for delta in spacing_range:
		border_pts.append(v*(spacing[iv] + delta) + center_pt)
border_pts = np.array(border_pts)

no_pts = []
spacing_range = [2, 3, 4]
for iv,v in enumerate(vectors):
	for delta in spacing_range:
		no_pts.append(v*(spacing[iv] + delta) + center_pt)
no_pts = np.array(no_pts)

fig = plt.figure(figsize = (15, 10))
ax = fig.add_subplot(111, projection='3d')
BP.drawPlanesFromHull(good_list, hull, ax, color = np.array([0.5, 0.5, 0.5]))
ax.scatter(center_pt[0], center_pt[1], center_pt[2], c = 'red')
ax.scatter(yes_pts[:,0], yes_pts[:,1], yes_pts[:,2], c = 'blue')
ax.scatter(border_pts[:,0], border_pts[:,1], border_pts[:,2], c = 'green')
ax.scatter(no_pts[:,0], no_pts[:,1], no_pts[:,2], c = 'black')
plt.show()
pdb.set_trace()

# ######  Create new shapes ######
# STL = ShapeSTLGeneratorPython()
# HC = HandCenteredCSV(True)
# for points in np.vstack((yes_pts, border_pts, no_pts)):
# 	# pdb.set_trace()
# 	stl_name = '%s_h%0.3f_w%0.3f_e%0.3f' %('cube', points[0].round(3), points[1].round(3), points[2].round(3))
# 	stl_name = stl_name.replace('.', 'D')
# 	stl_name += '.stl'
# 	pprint(stl_name)
# 	points *= HAND_PARAM/100.0
# 	STL.ShapeSTLGenerator('cube', float(30.0), os.path.join(os.path.realpath('.'),stl_name), float(points[0]), float(points[1]), float(points[2]), float(10.0))
# 	os.rename(stl_name, os.path.join(os.path.realpath('STLs'), stl_name))
# 	for cv in ['0', '1']:
# 		D = HC.HandT('equidistant', stl_name, points[0], points[1], points[2], 'h', 'side', 'up',cv)
# 		D['Joint Angles'] = np.array(D['Joint Angles'].split(',')).astype('float') #change from string to array
# 		D['Image Save Name'] = D['Image Save Name'].replace('.stl', '')
# 		D['Image Save Name'] = os.path.join('Images/Original', D['Image Save Name']) + '.png'
# 		HC.SIG.createImageFromParameters(D, obj_path = './STLs/')

# # ##### Turn images into survey images
# SIM = ShapeImageManipulator()
# SIM.cropAllImages('Images/Original/', 'Images/Cropped/')
# SIM.combineMultipleImages('Images/Cropped', 'Images/Combined')
# SIM.addBorderToMultipleImages('Images/Combined', 'Images/Borders', 3)
# SIM.reduceSizeAllImages('Images/Borders', 'Images/Reduced', size = (285, 200))
# SIM.uploadMultipleImages('Images/Reduced')


###### Generate Questions ######
img_base_url = 'http://people.oregonstate.edu/~kotharia/RefinementSurvey/Reduced/'
img_temp = '<img src="%s" style="width: %spx; height: %spx;" />' #imgurl, width of image, height of image
x = []
for i in range(0,len(yes_pts),3):
	e = i + 3
	x.append(np.array([yes_pts[i:e], border_pts[i:e], no_pts[i:e]]).reshape(-1,3))

with open('AllQuestions.csv', 'wb') as csvfile:
	writer = csv.writer(csvfile)
	for i,ps in enumerate(x):
		row = ['QID_%s' %i]
		for p in ps:
			h, w, e = p[:]
			P = '%s_h%.3f_w%.3f_e%.3f_%s_%s_%s_%s' %('cube', h, w, e, 'h', 'equidistant', 'side', 'up')
			P = P.replace('.', 'D')
			P += '.png'
			img_url = img_base_url + P
			img_block = img_temp %(img_url, 285, 200)
			row.append(img_block)
		writer.writerow(row)
pdb.set_trace()