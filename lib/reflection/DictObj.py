
class DictObj:
	def __init__(self, **entries):

		self.__dict__.update(entries)
		for key in self.__dict__:
			if isinstance(self.__dict__[key],dict):
				self.__dict__[key] = DictObj(**self.__dict__[key])
			elif isinstance(self.__dict__[key],list):
				self.__dict__[key] = DictObj.parseArray(self.__dict__[key])
		#self.__dict__['class_name']='util.lib.reflecton.DictObj'
	def to_dict(self):
		d = {}
		for key in self.__dict__:
			if isinstance(self.__dict__[key],DictObj):
				d[key] = self.__dict__[key].to_dict()
			elif isinstance(self.__dict__[key],list):
				d[key] = DictObj.parseBackArray(self.__dict__[key])
			else:
				d[key] = self.__dict__[key]
		return d
	def __str__(self):
		return "%s"%self.__dict__
	def __repr__(self):
		return self.__str__()
	def __iter__(self):
		return self.__dict__.__iter__()
	@staticmethod
	def parseArray(array):
		res = []
		for item in array:
			if isinstance(item,dict):
				res.append( DictObj(**item) )
			elif isinstance(item,list):
				res.append( DictObj.parseArray(item) )
			else:
				res.append(item)

		return res
	@staticmethod
	def parseBackArray(array):
		res = []
		for item in array:
			if isinstance(item,DictObj):
				res.append( item.to_dict() )
			elif isinstance(item,list):
				res.append( DictObj.parseBackArray(item) )
			else:
				res.append(item)

		return res