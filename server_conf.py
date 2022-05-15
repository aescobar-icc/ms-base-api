bind = '0.0.0.0:8000'
workers = 4
worker_class = 'eventlet'
worker_connections = 1000
keepalive = 5
timeout=120
accesslog = '-'
errorlog  = '-'

# srv = ServicePermission(name="base-api")
# module = srv.register_module("")
# srv.add_permision(name='employees.create',description="allow create an employe")
# srv.add_permision(name='employees.read',description="allow list one/all employees")
# srv.add_permision(name='employees.update',description="allow edit an employe")
# srv.add_permision(name='employees.delete',description="allow edit an employe")

# permission = {
# 	"service" : "base-api",
# 	"module"  : "employes",
# 	"permissions":[
# 		srv.add_permision(name='employees.create',description="allow create an employe")
# 		srv.add_permision(name='employees.read',description="allow list one/all employees")
# 		srv.add_permision(name='employees.update',description="allow edit an employe")
# 		srv.add_permision(name='employees.delete',description="allow edit an employe")
# 	]
# }


# module: m1
# permissions:{
# 	"employees.create":{"description":"xxx",srv:"base-api"}
# }

