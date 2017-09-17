from ShapeImageGeneratorTest import ShapeImageGenerator
import os
curdir = os.path.dirname(os.path.realpath(__file__))

import copy


class ObjectOnlyCSV(object):
	def __init__(self):
		self.SIG = ShapeImageGenerator()

	def objectsOnlyCSV(self):
		L = list()
		headers = ['Joint Angles', 'Hand Matrix', 'Model', 'Model Matrix', 'Camera Transform','Image Save Name', 'Image Size']
		fn = curdir + '/ImageGeneratorParametersObjectsOnly.csv'
		self.SIG.loadSTLFileList()
		CameraTransform = ['%s, %s, %s' %(80, -2.355, -.449)]

		for model in self.SIG.STLFileList: #capturing images of all objects
			D = dict.fromkeys(headers)
			D['Camera Transform'] = CameraTransform[0]
			D['Model'] = model.split('/')[-1].strip('.stl')
			D['Model Matrix'] = np.eye(4)
			D['Image Save Name'] = '%s/%s_nohand' %('GeneratedImages/ObjectsOnly', D['Model'])
			L.append(copy.deepcopy(D))


		with open(fn, 'wb') as file:
			writer = csv.DictWriter(file, headers)
			writer.writeheader()
			for l in L:
				writer.writerow(l)
		print("Successfully wrote to CSV file")
