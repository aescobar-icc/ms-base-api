from datetime import datetime
from itertools import count
from unittest import result
from mongoengine import Document,EmbeddedDocument
from mongoengine.fields import (
	DateTimeField, ReferenceField, StringField,EmbeddedDocumentField
)
from mongoengine import signals

from lib.log.UtilLog import UtilLog
from lib.db.mongo.util import UtilMongoEngine
#------- Department Model -------------
class Department(Document):
	meta = {'collection': 'department'}
	name = StringField()

#-------     Role Model   -------------
class Role(Document):
	meta = {'collection': 'role'}
	name = StringField()

	@staticmethod
	def create_or_update(role_dict):
		if 'id' not in role_dict: #create
			print("Creating new Role:%s"%role_dict)
			role = Role(**role_dict) # Role(name = role_dict['name'])
			role.save()
		else:
			print("Updating  Role:%s "%(role_dict))
			Role.objects(id=role_dict['id']).update_one(**role_dict)
			role = Role.objects.get(id=role_dict['id'])
			signals.post_save.send(Role, document=role,created=True)
		return role
	
	def __str__(self): 
		return "[Role:%s]"%self.name
class RoleSummary(EmbeddedDocument):
	id = StringField()
	name = StringField()


#-------  Employee Model -------------
class Employee(Document):
	meta = {'collection': 'employee'}
	name = StringField()
	hired_on = DateTimeField(default=datetime.now)
	department = ReferenceField(Department)
	role = ReferenceField(Role)
	roleSummary = EmbeddedDocumentField(RoleSummary)

	@staticmethod
	def all_employees(params):
		# filter=None
		# if search:
		# 	filter = (
		# 		Q(name__icontains=search) |
		# 		Q(variant__icontains=search)
		# 	)
		# return UtilModel.page_filter(Product,skip,limit,filter)
		count=0
		#result = Employee.objects[skip:skip+limit]()
		#return {"items":result,"count":count,"page":skip/limit + 1,"page_count":limit}
		return UtilMongoEngine.list_paginable(Employee,params)

	@staticmethod
	def on_role_change(sender, document,created):
		UtilLog.debug("sender:%s, document:%s"%(sender,document))
		all_employes_ref_role = Employee.objects(role=document)
		print(all_employes_ref_role)
		for e in all_employes_ref_role:
			e.roleSummary = RoleSummary(**{"id":str(document.id),"name":document.name})
			e.save()
	
	def __str__(self): 
		return "name:%s"%self.name

#allow to know when a role changed in order to update Employee.role_summary
signals.post_save.connect(Employee.on_role_change,sender=Role)