
import graphene as g

class PaginableType(g.ObjectType):
	count		= g.Int()
	page 		= g.Int()
	page_count	= g.Int()

class UtilGraphene:	
	@staticmethod
	def as_paginable(d: dict) -> PaginableType:
		print(d)
		p = PaginableType()
		p.count		 = d.get('count',0)
		p.page 		 = d.get('page',0)
		p.page_count = d.get('page_count',0)
		p.items 	 = d.get('items',None)
		return p

	# @staticmethod
	# def graphene_page_filter(model,offset=0,page_count=50,**filter):
	# 	return UtilModel.graphene_paginable(UtilModel.page_filter(model,offset=0,page_count=50,**filter))
