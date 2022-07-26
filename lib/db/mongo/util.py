import inspect
from datetime import datetime
from unittest import result
from lib.log.UtilLog import UtilLog


from json import JSONEncoder
import types
from bson import ObjectId
from mongoengine.queryset import QuerySet
from mongoengine import *


class ModelEncoder(JSONEncoder):
	def default(self,obj):
		
		if isinstance(obj, datetime):
			return str(obj).replace(' ','T')+'Z'
		if isinstance(obj, ObjectId):
			return str(obj)
		if isinstance(obj, QuerySet) or isinstance(obj, types.GeneratorType):
			arr = []
			for ob in obj:
				#del ob['_id']
				arr.append(ob)
			return arr
		if isinstance(obj, Document) or isinstance(obj, EmbeddedDocument):
			return obj.to_mongo()

		return JSONEncoder.default(self, obj)
class UtilMongoEngine:
	@staticmethod
	def validate_params(params):
		if not isinstance(params,dict) :
			raise Exception("params must be a dict")

		p = {
			"limit":50,"offset":0,"page":1,
			"query":{},
			#"sort":[],
			"pipeline":[]
		}
		p.update(params)

		#UtilLog.warning("params:%s\np:%s"%(params,p))

		if not isinstance(p['limit'],int) :
			raise Exception("params['limit'] must be an int")
		if not isinstance(p['offset'],int) :
			raise Exception("params['offset'] must be an int")
		if not isinstance(p['page'],int) :
			raise Exception("params['page'] must be an int")
		if not isinstance(p['query'],dict) :
			raise Exception("params['query'] must be an dict")


		#check max items per page
		if p['limit'] > 100:
			p['limit'] = 100
		#page override offset
		if p['page'] > 0:
			p['offset'] = (p['page'] -1) * p['limit']

		query = {}
		for k in p['query']:
			if "." in k:
				kk = k.replace(".","__")
				#p['query'][kk] = p['query'][k]
				#del p['query'][k]
				query[kk] = p['query'][k]
			else:
				query[k]=p['query'][k]
		p['query'] = query
		
		return p
	
	@staticmethod
	def list(model,p={},validate=True):
		if validate:
			p = UtilMongoEngine.validate_params(p)
		if 'pipeline' in p and len(p['pipeline']) > 0:
			#UtilLog.debug(p['pipeline'])
			return list( model.objects().aggregate(p['pipeline']) )
		else:
			queryset = model.objects[p['offset']:p['offset']+p['limit']]

			if 'query_raw' in p :
				queryset = queryset(__raw__= p['query_raw'])
			else:
				queryset = queryset(**p['query'])

			if 'exclude' in p:
				queryset = queryset.exclude(*p['exclude'])
			if 'only' in p:
				queryset = queryset.only(*p['only'])
			if 'sort' in p:
				queryset = queryset.sort(*p['sort'])

			return queryset
	@staticmethod
	def list_paginable(model,p={}):
		p = UtilMongoEngine.validate_params(p)
		items = UtilMongoEngine.list(model,p,False)
		if 'query_raw' in p :
			count = model.objects(__raw__= p['query_raw']).count()
		else:
			count = model.objects(**p['query']).count()
		max_page = int(count/p['limit']) + 1
		if p['page'] > max_page :
			p['page'] = max_page
		return { 
			"offset":p['offset'],
			"limit":p['limit'],
			"page":p['page'],
			"page_count":max_page,
			"items":items,
			"items_count":count,
		}
	@staticmethod
	def signal_caller(signal_name,model,instance,**kwargs):
		print("[debug] trying to call signal_caller:%s.%s "%(model.__name__,signal_name))
		if hasattr(model, signal_name) :
			signal = getattr(model, signal_name)
			if inspect.isfunction(signal):
				signal(model,instance,**kwargs)
			else:
				UtilLog.warning("signal:%s.%s is not a function"%(model.__name__,signal_name))
		else:
			print("[debug] signal_caller:%s.%s not found"%(model.__name__,signal_name))
	@staticmethod
	def create_or_update(model,**kwargs):
			
		if 'id' not in kwargs: #create
			print("Creating new %s:%s"%(model.__name__,kwargs))
			m = model(**kwargs) # Role(name = role_dict['name'])
			#UtilMongoEngine.signal_caller('pre_save',model,m)
			m.save()
		else:
			print("Updating  %s:%s"%(model.__name__,kwargs))
			m = model.objects.get(id=kwargs['id'])
			UtilMongoEngine.update_with_kwargs(m,**kwargs)
			#UtilMongoEngine.signal_caller('pre_save',model,m)
			m.save()
			# print("Updating  %s:%s"%(model.__name__,kwargs))
			# model.objects(id=kwargs['id']).update_one(**kwargs)
			# m = model.objects.get(id=kwargs['id'])
			#signals.post_save.send(Role, document=role,created=True)
		return m

	@staticmethod
	def update_with_kwargs(instance,**kwargs):
		ModelClass = instance.__class__
		fields = ModelClass.__dict__['_fields']
		for name in fields:
			if name in kwargs:
				if type(fields[name]).__name__ == 'ReferenceField': #and isinstance(instance[name],str):
					print(fields[name].__dict__)
					if isinstance(kwargs[name],str):
						reference_type = fields[name].__dict__['document_type_obj']
						print("[debug] getting reference:%s"%(kwargs[name]))
						kwargs[name] = reference_type.objects.get(id=kwargs[name])  # get ref from id
				instance[name] = kwargs[name]
		if 'id' in kwargs:
			if "update_at" in fields:
				instance["update_at"] = datetime.now()
		else:
			if "create_at" in fields:
				instance["create_at"] = datetime.now()

	@staticmethod
	def adapt_kwargs(ModelClass,obj):
		new_kwargs = {}
		fields = ModelClass.__dict__['_fields']
		for name in fields:
			if name in obj:
				new_kwargs[name] = obj[name]
		if 'id' in obj:
			if "update_at" in fields:
				obj["update_at"] = datetime.now()
		else:
			if "create_at" in fields:
				obj["create_at"] = datetime.now()
		return new_kwargs
	@staticmethod
	def create_init(ModelClass):
		"""Create dynamically a construnctor for mongoengine Model that allows 
		initializate a class from any dict that has more than attrs that defined by model

			Parameters:
			ModelClass (class): the model class that you want to initialize

			Returns:
			void:Returning nothing
		"""

		def __init__(self, *args, **kwargs):
			super(ModelClass, self).__init__(*args, **(UtilMongoEngine.adapt_kwargs(ModelClass,kwargs)))
		ModelClass.__init__ = __init__

	@staticmethod
	def to_dict(instance):
		if instance is None:
			return None
		val = instance.to_mongo().to_dict()
		if '_id' in val:
			val['id'] = str(val['_id'])
			del val['_id']
		return val
	