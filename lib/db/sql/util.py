from operator import or_,and_
from pydoc import resolve
import time
from sqlalchemy import func
from lib.db.sql.connection import SqlConnection

db = SqlConnection.getSqlAlchemy()

class UtilSQLAlchemy:
	logic_operators = {"and":and_,"or":or_}
	comparison_operators = {"eq":"__eq__", "lte":"__le__", "lt":"__lt__", "gte":"__ge__", "gt":"__gt__", "ne":"__ne__", "in":"in_", "nin":"not_in", "like":"like", "nlike":"not_like"}

	

	# {"$and":[ {"name":"test"}, {"or":[ {"status":"1"}, {"name":"2"} ]} ]}
	# sample: value = [{"$eq": {"id": 1}}, {"$eq": {"name": "test"}}]
	# sample: value = {}


	@staticmethod
	def is_native(value):
		return isinstance(value, (int, float, str, bool))
	@staticmethod
	def resolve_logic_oper(logic_func,model,value):
		print("---------------------------------------------------")
		print("resolve_logic_oper:",logic_func,model,value)
		_clauses = []
		_cols = []
		if isinstance(value,list):
			for elem in value:
				if not isinstance(elem,dict):
					raise Exception("Invalid %s:[..] operando:%s, must be dict"%(logic_func,elem))
				UtilSQLAlchemy.resolve_dict(str(logic_func),model,elem,_clauses,_cols)
				
		elif isinstance(value,dict):
			UtilSQLAlchemy.resolve_dict(str(logic_func),model,value,_clauses,_cols)
		else:
			raise Exception("Invalid %s:... operando:%s, must be list or dict"%(logic_func,value))
		print("_cols:",_cols)
		lc = len(_cols)
		if lc == 1:
			_clauses.append(_cols[0])
		elif lc > 1:
			_clauses.append(logic_func(*_cols))

		if len(_clauses) == 1:
			return _clauses[0]
		return logic_func(*_clauses)

	@staticmethod
	def resolve_operator(model,key,val):
		print("---------------------------------------------------")
		print("resolve_operator:",model,key,val)
		for op,comparator in UtilSQLAlchemy.comparison_operators.items():
			if op in val:
				col = getattr(model["cls"],key)
				exp = getattr(col,comparator)(val[op])
				return exp
		raise Exception("Invalid comparacion operator:%s"%val)
	@staticmethod
	def resolve_dict(oper_name,model,elem,_clauses,_cols):
		print("---------------------------------------------------")
		print("resolve_dict:",oper_name,model,elem,_clauses,_cols)
		for key,val in elem.items():
			if key in model["columns"]:
				if isinstance(val,list):
					col = getattr(model["cls"],key).in_(val)
				elif isinstance(val,dict):
					col = UtilSQLAlchemy.resolve_operator(model,key,val)
				else: #elif val is None or UtilSQLAlchemy.is_native(val):
					col = getattr(model["cls"],key).__eq__(val)
				_cols.append(col)
			elif key in UtilSQLAlchemy.logic_operators:
				logic_func = UtilSQLAlchemy.logic_operators[key]
				operation_group = UtilSQLAlchemy.resolve_logic_oper(logic_func,model,val).self_group()
				_clauses.append(operation_group)
			else:
				raise Exception("Invalid %s operando:%s, must be column name or logic operator"%(oper_name,key))

	# @staticmethod
	# def resolve_logic_old(query,model):
	# 	clauses = []
	# 	for key,value in query.items():
	# 		if key in model["columns"]:

	# 		elif key in UtilSQLAlchemy.logic_operators:
	# 			logic_func = UtilSQLAlchemy.logic_operators[key]
	# 			operation_group = UtilSQLAlchemy.resolve_logic_oper(logic_func,model,value)
	# 			clauses.append(operation_group)
	# 		else:
	# 			raise Exception("Unknown operator: %s"%key)
	# 	return clauses


	# @staticmethod
	# def resolve_logic_old(op):
	# 	clauses = []
	# 	model = {"cls":op["model"],"columns":op["columns"]}
	# 	for operation in op["operations"]:
	# 		oper = operation["operator"]
	# 		value = operation["value"]
	# 		if oper in UtilSQLAlchemy.logic_operators:
	# 			logic_func = UtilSQLAlchemy.logic_operators[oper]
	# 			operation_group = UtilSQLAlchemy.resolve_logic_oper(logic_func,model,value)
	# 			clauses.append(operation_group)
	# 		else:
	# 			raise Exception("Unknown operator: %s"%oper)
	# 	return clauses

	@staticmethod
	def validate_params(model,params):
		if not isinstance(params,dict) :
			raise Exception("params must be a dict")
		p = {
			"limit":50,"offset":0,"page":1,
			"query":{},
			"sort":{},
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
		if not isinstance(p['sort'],dict) :
			raise Exception("params['sort'] must be an dict")
		#check max items per page
		if p['limit'] > 100:
			p['limit'] = 100
		#page override offset
		if p['page'] > 0:
			p['offset'] = (p['page'] -1) * p['limit']
		#get valid columns
		model_col_names = {}
		columns = model.__dict__['__table__'].columns
		#print("table		",model.__dict__)
		import inspect
		memb = inspect.getmembers(model, lambda a:not(inspect.isroutine(a)))
		for name,obj in memb:
			if name is "customer":
				print("name:%s obj:"%(name),obj.__dict__)

		for col in columns:
			# print("----------------------------------------------------")
			# print("\ncol:%s"%col.__dict__)
			model_col_names[col.name] = 1
		#separate key/value filters and key in value filters
		# filter_by_query = {}
		# filter_in_query = []
		# filter_logic_query = []
		# for k,v in p['query'].items():
		# 	if k in model_col_names:
		# 		if isinstance(v,list):
		# 			f = getattr(model,k).in_(v)
		# 			filter_in_query.append(f)
		# 		else:
		# 			filter_by_query[k] = v
		# 	elif k in UtilSQLAlchemy.logic_operators:
		# 		filter_logic_query.append({"operator":k,"value":v})

		# p['query'] = filter_by_query
		# p['query_in'] = filter_in_query
		# p['query_logic'] = {
		# 	"operations": filter_logic_query,
		# 	"columns":model_col_names,
		# 	"model":model
		# }
		p["model"]= {"cls":model,"columns":model_col_names}

		#create sort by valid columns
		sort_by = []
		for k,v in p['sort'].items():
			if k in model_col_names:
				if v == "desc":
					s = getattr(model,k).desc()
					sort_by.append(s)
				else:
					s = getattr(model,k).asc()
					sort_by.append(s)
		p['sort']=sort_by
		
		return p

	@staticmethod
	def query(model,p={},validate=True,limits=True):
		if validate:
			p = UtilSQLAlchemy.validate_params(model,p)
		queryset = model.query
		# if 'query' in p :
		# 	queryset = queryset.filter_by(**p['query'])
		# if 'query_in' in p :
		# 	queryset = queryset.filter(*p['query_in'])
		# if 'query_logic' in p :
		# 	clauses = UtilSQLAlchemy.resolve_logic(p['query_logic'])
		# 	queryset = queryset.filter(*clauses)
		if 'query' in p :
			# clauses = UtilSQLAlchemy.resolve_logic(p['query'],p["model"])
			# queryset = queryset.filter(*clauses)
			queryset = queryset.filter( UtilSQLAlchemy.resolve_logic_oper(and_,p['model'],p['query']) )
		if 'sort' in p :
			queryset = queryset.order_by(*p['sort'])
		if limits:
			queryset = queryset.offset(p['offset']).limit(p['limit'])
		return queryset

	
	@staticmethod
	def list(model,p={}):
		""" return a list of objects according to the limit and offset, by default offset is 0 and limit is 100 """
		queryset = UtilSQLAlchemy.query(model,p)
		return queryset.all()

	
	@staticmethod
	def list_all(model,p={}):
		p = UtilSQLAlchemy.validate_params(model,p)
		queryset = UtilSQLAlchemy.query(model,p,False,False)
		count = queryset.count()
		offset=0
		limit=100
		while offset < count:
			query_chunk = queryset.offset(offset).limit(limit)
			offset += limit
			print("getting %s from %s"%(offset,count))
			for item in query_chunk:
				yield item
			time.sleep(0.5)

	
	@staticmethod
	def list_paginable(model,p={}):
		""" 
			return a dict with pagination info

			params:
				model: sqlalchemy model class

				params: dict with the following keys:
					limit:  int, max items per page
					offset: int, offset of the first item
					page:   int, page number
					query:  dict, filter by query
					sort: dict, sort by query

			return: dict with the following keys:
				items: list of objects
				items_count: int, total items returned
				offset: int, offset of the first item
				limit: int, max items per page
				page: int, page number
				pages_count: int, total pages for query
				has_next: bool, if there is a next page
				count: int, total items for query
		"""
		p = UtilSQLAlchemy.validate_params(model,p)
		queryset = UtilSQLAlchemy.query(model,p,False,False)
		count = queryset.count()
		queryset = queryset.offset(p['offset']).limit(p['limit'])
		#count = db.session.query(func.count(model.id)).scalar()
		max_page = int(count/p['limit']) + 1
		items = queryset.all()
		if p['page'] > max_page :
			p['page'] = max_page
		
		return { 
			"offset":p['offset'],
			"limit":p['limit'],
			"has_next":p['page'] < max_page,
			"page":p['page'],
			"page_count":max_page,
			"items":items,
			"items_count":len(items),
			"count":count,
		}