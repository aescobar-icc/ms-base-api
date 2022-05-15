
import graphene as g
from lib.db.mongo.util import UtilMongoEngine

class PaginableType(g.ObjectType):
	items_count	= g.Int()
	page 		= g.Int()
	page_count	= g.Int()

class UtilGraphene:	
	@staticmethod
	def as_paginable(d: dict) -> PaginableType:
		print(d)
		p = PaginableType()
		p.page 		 = d.get('page',0)
		p.page_count = d.get('page_count',0)
		p.items 	 = d.get('items',None)
		p.items_count= d.get('items_count',0)
		return p

	@staticmethod
	def paginable_mongo(model,**kwargs)-> PaginableType:
		return UtilGraphene.as_paginable(UtilMongoEngine.list_paginable(model,**kwargs))
	# @staticmethod
	# def graphene_page_filter(model,offset=0,page_count=50,**filter):
	# 	return UtilModel.graphene_paginable(UtilModel.page_filter(model,offset=0,page_count=50,**filter))
