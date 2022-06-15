from sqlalchemy import func
from lib.db.sql.connection import SqlConnection

db = SqlConnection.getSqlAlchemy()

class UtilSQLAlchemy:
	@staticmethod
	def validate_params(params):
		if not isinstance(params,dict) :
			raise Exception("params must be a dict")

		p = {
			"limit":50,"offset":0,"page":1,
			"query":{},
			#"sort":[],
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
		
		return p

	@staticmethod
	def list(model,p={},validate=True):
		if validate:
			p = UtilSQLAlchemy.validate_params(p)
		
		queryset = model.query
		if 'query' in p :
			queryset = queryset.filter_by(**p['query'])
		
		queryset = model.query.offset(p['offset']).limit(p['limit'])

		# if 'exclude' in p:
		# 	queryset = queryset.exclude(*p['exclude'])
		# if 'only' in p:
		# 	queryset = queryset.only(*p['only'])
		# if 'sort' in p:
		# 	queryset = queryset.sort(*p['sort'])
		return queryset
	
	@staticmethod
	def list_paginable(model,p={}):
		p = UtilSQLAlchemy.validate_params(p)
		queryset = UtilSQLAlchemy.list(model,p,False)
		count = db.session.query(func.count(model.id)).scalar()
		max_page = int(count/p['limit']) + 1
		if p['page'] > max_page :
			p['page'] = max_page
		return { 
			"offset":p['offset'],
			"limit":p['limit'],
			"has_next":p['page'] < max_page,
			"page":p['page'],
			"page_count":max_page,
			"items":queryset.all(),
			"items_count":count,
		}
