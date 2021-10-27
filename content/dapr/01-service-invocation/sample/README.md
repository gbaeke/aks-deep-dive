# Using the Python service invocation sample

`dapr run --app-id myapp --dapr-http-port 3500 --app-port 5000 python3 service.py`
(requires Python 3 installed with flask)

In another terminal, run the following command to invoke the service:

`curl http://localhost:3500/v1.0/invoke/myapp/method/add -X POST`

or 

`curl -H 'dapr-app-id: myapp' 'http://localhost:3500/add' -X POST`

or

`curl 'http://dapr-app-id:myapp@localhost:3500/add' -X POST`