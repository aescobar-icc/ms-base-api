# ms-base-api

This project is a base implementation of an api microservice.
works with Docker, Flask and Connexion (swagger/open api 3.0)

## 1.- Simple Run

### 1.1.- build and run

    docker-compose up --build

### 1.2.- Test echo api
```bash 
curl -X 'GET' \
'http://localhost:8080/test/api/v1/echo/hello%20api%21' \
-H 'accept: */*'
```

## 2.- How to extend
I will to use as example a simple math api.

### 2.1 Create the new service directory structure

```bash
export API_SRV_NAME=my_super_new_math_api
mkdir -p $API_SRV_NAME/{apis,services/{basic,}}
tree $API_SRV_NAME/
```

```bash
my_super_new_math_api/
├── apis
└── services
```

### 2.2 Create base files

create dockerfile that extends from base api
---
```bash
touch $API_SRV_NAME/dockerfile
```
add this content

```dockerfile
FROM aescobaricc/ms-base-api:0.0.1

```

create docker-compose.yaml
---

	touch $API_SRV_NAME/docker-compose.yaml

add this content
```yaml
version: '3.5'
networks:
  my_srv_net:
    name: my_srv_net
    ipam:
      config:
        - subnet: 172.20.1.0/24
services:
  my_super_new_math_api:
    image: my_org/my_super_new_math_api:0.0.1
    container_name: my_super_new_math_api
    restart: always
    build:
      context: .
      dockerfile: dockerfile
    env_file: .env
    volumes:
      - .:/api-run
    ports:
      - "8080:8000"
    networks:
      my_srv_net:
        ipv4_address: 172.20.1.2

```
create python implementation
---

```bash

export SRV_NAME=BasicOps
touch $API_SRV_NAME/services/basic/"${SRV_NAME}Facade.py"
touch $API_SRV_NAME/services/basic/"${SRV_NAME}Service.py"
```
add this content to facade file
```python
from services.basic.BasicOpsService import BasicOpsService
from lib.reflection.ApiEncoder import ApiEncoder

from flask import request,Response
import json

class BasicOpsFacade:

	@staticmethod
	def sum(val1,val2):
		res = BasicOpsService.sum(val1,val2)
		return Response(
			response=json.dumps(res,cls=ApiEncoder),
			status=200, 
			mimetype="application/json"
		)
```

add this content to service file
```python
class BasicOpsService:
	@staticmethod
	def sum(val1,val2):
		return val1+val2
```

create api implementation
---

```bash
touch $API_SRV_NAME/apis/"${SRV_NAME}.yaml"
```


add this content (to learn more about how to implement api 3.0 see https://swagger.io/specification/)

```yaml
openapi: "3.0.0"
info:
  title: Service Math Api
  version: "1.0.0"
  description: This service allow you perform basic math operations
  contact:
    name: yur name
    email: your mail
    url: your link
servers:
  - url: /math/api/v1

# Paths supported by the server application
paths:
  /sum/{val1}/{val2}:
    get:
      operationId: "services.basic.BasicOpsFacade.BasicOpsFacade.sum"
      tags:
      - "BASIC"
      summary: "math.sum"
      description: "math.sum"
      parameters:
        - name: val1
          in: path
          description: a numeric value
          required: true
          schema:
            type: float
        - name: val2
          in: path
          description: a numeric value
          required: true
          schema:
            type: float

      responses:
        200:
          description: "math sum Ok"
        400:
          description: "Error Format Data"
        500:
          description: "Internal server error"
```

### 2.3  Run your new api service


    cd $API_SRV_NAME
    docker-compose up --build

### 2.4.- Test sum api
```bash
VAL1=10
VAL2=15
curl -X 'GET' \
'http://localhost:8080/math/api/v1/sum/$VAL1/$VAL2' \
-H 'accept: */*'
```

## Author

👤 **Adan Escobar**

- Linkedin: [@aescobar](https://www.linkedin.com/in/aescobar-ing-civil-computacion/)
- Github: [@aescobar-icc](https://github.com/aescobar-icc)


