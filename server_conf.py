bind = '0.0.0.0:8000'
workers = 4
worker_class = 'eventlet'
worker_connections = 1000
keepalive = 5
timeout=120
accesslog = '-'
errorlog  = '-'