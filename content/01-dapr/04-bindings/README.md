# Bindings

What can you do?
- respond to events from external systems --> **input bindings**
- interface with external systems -> **output bindings**

## Input Bindings

Input (and output) bindings are here: https://docs.dapr.io/reference/components-reference/supported-bindings/

Some examples of input bindings:
- Kafka
- Kubernetes events
- MQTT
- Twitter
- GCP Cloud Pub/Sub
- Azure Storage Queue
- ...

⚠️ **Important**: most of these bindings are in an **Alpha** state

Using an input binding is as simple as:
- create a component for the input binding (e.g. Kafka)
  - the component will have a `name` in its `metadata`; you code needs an endpoint with the same name to reveive the event
  - you can override the endpoint in the `spec` of the component ⬇️

```yaml
name: mybinding
spec:
  type: binding.rabbitmq
  metadata:
  - name: route
    value: /onevent

```


- listen for incoming events in your code: method = `POST` and endpoint is `name` of the component
- when you receive an event, return a `200 OK` to indicate success; return a response different from `200 OK` to indicate failure

## Output Bindings

Here are some examples of output bindings:
- HTTP: HTTP calls
- InfluxDB: write to InfluxDB (written by yours truly)
- MySQL
- PostgreSQL
- SMTP
- Twilio
- Twitter
- AWS S3
- GCP Storage Bucket
- Azure CosmosDB
- Azure SignalR
- ...


Using an output binding is as simple as:
- create a component for the output binding (e.g. Kafka)
- send an event using the `POST` method to the sidecar in the following way:

```
curl -X POST -H 'Content-Type: application/json' http://localhost:3500/v1.0/bindings/myevent -d '{ "data": { "message": "Hi!" }, "operation": "create" }'
```

