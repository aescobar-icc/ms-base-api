import graphene as g
from lib.db.mongo.util import UtilMongoEngine
from lib.db.sql.util import UtilSQLAlchemy
import lib.db.graphene.types as t

class UtilGraphene:	
	@staticmethod
	def as_paginable(d: dict) -> t.PaginableType:
		#print(d)
		p = t.PaginableType()
		p.count 	 	= d.get('count',0)
		p.page 		 	= d.get('page',0)
		p.page_count 	= d.get('page_count',0)
		p.items 	 	= d.get('items',[])
		p.items_count	= d.get('items_count',0)
		p.offset		= d.get('offset',0)
		p.limit			= d.get('limit',0)
		p.has_next		= d.get('has_next',False)
		return p

	@staticmethod
	def paginable_mongo(model,**kwargs)-> t.PaginableType:
		return UtilGraphene.as_paginable(UtilMongoEngine.list_paginable(model,**kwargs))
		
	@staticmethod
	def paginable_sql(model,**kwargs)-> t.PaginableType:
		return UtilGraphene.as_paginable(UtilSQLAlchemy.list_paginable(model,kwargs))
	# @staticmethod
	# def graphene_page_filter(model,offset=0,page_count=50,**filter):
	# 	return UtilModel.graphene_paginable(UtilModel.page_filter(model,offset=0,page_count=50,**filter))