from unittest import result
from lib.log.UtilLog import UtilLog

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
	def create_or_update(model,**kwargs):
		if 'id' not in kwargs: #create
			print("Creating new %s:%s"%(model.__name__,kwargs))
			m = model(**kwargs) # Role(name = role_dict['name'])
			m.save()
		else:
			print("Updating  %s:%s"%(model.__name__,kwargs))
			model.objects(id=kwargs['id']).update_one(**kwargs)
			m = model.objects.get(id=kwargs['id'])
			#signals.post_save.send(Role, document=role,created=True)
		return m


	