from operator import or_,and_
import time
import  sqlalchemy
from sqlalchemy.orm.attributes import InstrumentedAttribute

from sqlalchemy.inspection import inspect

from lib.log.UtilLog import UtilLog
from lib.db.sql.connection import SqlConnection

db = SqlConnection.getSqlAlchemy()


#customer:{name:{like:ad}}
class RelationshipInspector:
	model=None
	rel=None
	key=None
	primaryjoin=None
	def __init__(self,rel):
		self.model=rel.mapper.class_
		self.rel=rel
		self.key=rel.key
		self.primaryjoin=rel.primaryjoin
	
	def print_info(self):
		UtilLog.warning(self.rel.primaryjoin)
		UtilLog.warning(self.rel.direction.name)
		UtilLog.warning(self.rel.remote_side)
		UtilLog.warning(self.rel._reverse_property)
		#dir(relation)
class ModelInspector:
	logic_operators = {"and":and_,"or":or_}
	comparison_operators = {"eq":"__eq__", "lte":"__le__", "lt":"__lt__", "gte":"__ge__", "gt":"__gt__", "ne":"__ne__", "in":"in_", "nin":"not_in", "like":"like", "nlike":"not_like"}
	model=None
	columns={}
	relationships={}

	def __init__(self,model):
		self.model=model
		imodel = inspect(model)
		for c in imodel.columns:
			self.columns[c.key] = c

		for r in imodel.relationships:
			self.relationships[r.key] = RelationshipInspector(r)

	def is_column(self,name:str) -> bool:
		res = name in self.columns
		UtilLog.debug("%s is column: %s"%(name,res))
		return res

	def is_rel(self,name:str) -> bool:
		res = name in self.relationships
		UtilLog.debug("%s is rel: %s"%(name,res))
		return res

	def get_column(self,col_name:str):
		if col_name in self.columns:
			return	self.columns[col_name]
		raise Exception("Column %s not found"%col_name)

	def get_rel(self,name:str):
		if name in self.relationships:
			return	self.relationships[name]
		raise Exception("Relation %s not found"%name)

	def get_column_comparator(self,col_name:str,comp_name:str):
		if comp_name in self.comparison_operators:
			col		= self.get_column(col_name)
			comp	= self.comparison_operators[comp_name]
			return getattr(col,comp)
		raise Exception("Comparator %s not found"%comp_name)

	def get_expression(self,col_name:str,comp_name:str,value:any):
		"""
		usage: ispector.get_expression("name","eq","John")

		returns representation: Model.name == "John"

		"""
		comp	= self.get_column_comparator(col_name,comp_name)
		exp		= comp(value)

		return exp

	def __str__(self) -> str:
		return "ModelInspector(%s)"%self.model.__name__


class UtilSQLAlchemy:

	

	# {"$and":[ {"name":"test"}, {"or":[ {"status":"1"}, {"name":"2"} ]} ]}
	# sample: value = [{"$eq": {"id": 1}}, {"$eq": {"name": "test"}}]
	# sample: value = {}


	@staticmethod
	def is_native(value):
		return isinstance(value, (int, float, str, bool))
	@staticmethod
	def resolve_logic_oper(logic_func,model_insp,value):
		print("---------------------------------------------------")
		print("resolve_logic_oper:",logic_func,model_insp,value)
		_clauses = []
		#_cols = []
		if isinstance(value,list): #for example: logic_func=and   value=[ {"name":"test"}, {"or":[ {"status":"1"}, {"name":"2"} ]} ]}
			for elem in value:
				if not isinstance(elem,dict):
					raise Exception("[resolve_logic_oper] Invalid %s:[..] operando:%s, must be dict"%(logic_func,elem))
				#UtilSQLAlchemy.resolve_dict(str(logic_func),model_insp,elem,_clauses,_cols)
				UtilSQLAlchemy.resolve_dict(str(logic_func),model_insp,elem,_clauses)
				
		elif isinstance(value,dict): # for example: logic_func=and   value={"name":"test","or":[{"status":"1"},{"name":"2"}]}
			#UtilSQLAlchemy.resolve_dict(str(logic_func),model_insp,value,_clauses,_cols)
			UtilSQLAlchemy.resolve_dict(str(logic_func),model_insp,value,_clauses)
		else:
			raise Exception("[resolve_logic_oper] Invalid %s:... operando:%s, must be list or dict"%(logic_func,value))
		# print("_cols:",_cols)
		# lc = len(_cols)
		# if lc == 1:
		# 	_clauses.append(_cols[0])
		# elif lc > 1:
		# 	_clauses.append(logic_func(*_cols))
		UtilLog.warning("_clauses:%s"%_clauses)
		if len(_clauses) == 1:
			return _clauses[0]
		return logic_func(*_clauses)

	@staticmethod
	def resolve_operator(model_insp,col_name,val):
		print("---------------------------------------------------")
		print("resolve_operator:",model_insp,col_name,val)
		for comp_name,comparator in ModelInspector.comparison_operators.items():
			if comp_name in val:
				# col = getattr(model["cls"],col_name)
				# exp = getattr(col,comparator)(val[comp_name])
				# return exp
				return model_insp.get_expression(col_name,comp_name,val[comp_name])
		raise Exception("[resolve_operator] Invalid comparacion operator:%s"%val)
	@staticmethod
	def resolve_dict(oper_name,model_insp,elem,_clauses):
	#def resolve_dict(oper_name,model_insp,elem,_clauses,_cols):
		print("---------------------------------------------------")
		print("resolve_dict:",oper_name,model_insp,elem,_clauses)
		for key,val in elem.items():
			if model_insp.is_column(key):
				if isinstance(val,list):
					#col = getattr(model_insp["cls"],key).in_(val)
					col = model_insp.get_expression(key,"in",val)
				elif isinstance(val,dict):
					col = UtilSQLAlchemy.resolve_operator(model_insp,key,val)
				else: #elif val is None or UtilSQLAlchemy.is_native(val):
					#col = getattr(model_insp["cls"],key).__eq__(val)
					col = model_insp.get_expression(key,"eq",val)
				#_cols.append(col)
				_clauses.append(col)
			elif model_insp.is_rel(key):
				rel = model_insp.get_rel(key)
				rel_insp = ModelInspector(rel.model)
				_clauses.append(rel.primaryjoin)
				UtilSQLAlchemy.resolve_dict("rel",rel_insp,val,_clauses)
			elif key in ModelInspector.logic_operators:
				logic_func = ModelInspector.logic_operators[key]
				operation_group = UtilSQLAlchemy.resolve_logic_oper(logic_func,model_insp,val).self_group()
				_clauses.append(operation_group)
			else:
				msg ="[resolve_dict] Invalid key:%s, must be column, relationships or logic operator"%key
				UtilLog.error(msg)
				raise Exception(msg)

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
		
			
		model_insp = ModelInspector(model)
		#p["model_insp"]= model_insp

		#create sort by valid columns
		sort_by = []
		for k,v in p['sort'].items():
			if model_insp.is_column(k):
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
		if 'query' in p :
			#queryset = queryset.filter( UtilSQLAlchemy.resolve_logic_oper(and_,p['model_insp'],p['query']) )
			queryset = queryset.filter( UtilSQLAlchemy.resolve_logic_oper(and_,ModelInspector(model),p['query']) )
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