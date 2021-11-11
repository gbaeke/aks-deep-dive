import requests
import json

# run this app with: dapr run --app-id myapp --dapr-http-port 3500

# config
store_name = "statestore"
dapr_url = "http://localhost:3500/v1.0/state/{}".format(store_name)

# payload to save
payload = [
    { "key": "mykey", 
      "value": "myvalue3", 
      "options": 
        {
            "consistency": "strong"
        }
    }]

response = requests.post(dapr_url, json=payload)

# http response code of 204 means State saved; 500 means Failed to save state
print("Saving payload with mykey: ", response.status_code)

# read mykey; success code is 200
response = requests.get(dapr_url + "/mykey")
print("Reading mykey: ", response.text)
print("Status code ", response.status_code)

# read non-existing key; should result in 204
response = requests.get(dapr_url + "/nokey")
print("Reading nokey: ", response.status_code)

# delete mykey; 204 means success
response = requests.delete(dapr_url + "/mykey")
print("Delete mykey: ", response.status_code)

# delete non existing key; also results in 204
response = requests.delete(dapr_url + "/nokey")
print("Delete nokey: ", response.status_code)

# first-write

# first delete the key
response = requests.delete(dapr_url + "/firstkey")
print("Delete firstkey: ", response.status_code)

# payload to save
payload = [
    { "key": "firstkey", 
      "value": "somevalue", 
      "options": 
        {
            "consistency": "strong",
            "concurrency": "first-write"
        }
    }]

response = requests.post(dapr_url, json=payload)
print("Saving state with first-write: ", response.status_code)
print("All headers ", response.headers)

# read firstkey
response = requests.get(dapr_url + "/firstkey", headers={"concurrency": "first-write"})
print("Reading firstkey: ", response.text)
print("All headers ", response.headers)
print("ETag ", response.headers.get("Etag"))

# update key
newPayload = [
    { "key": "firstkey", 
      "value": "othervalue",
      "etag": response.headers.get("Etag"),
      "options": 
        {
            "consistency": "strong",
            "concurrency": "first-write"
        }
    }]

response = requests.post(dapr_url, json=newPayload, headers={"If-Match": response.headers.get("Etag")})
print("Update state with first-write: ", response.status_code)

# read firstkey again
response = requests.get(dapr_url + "/firstkey", headers={"concurrency": "first-write"})
print("Reading firstkey: ", response.text)
print("All headers ", response.headers)
print("ETag ", response.headers.get("Etag"))