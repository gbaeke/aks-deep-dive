# Publish and subscribe

## Intro

⚠️ Full API reference: https://docs.dapr.io/reference/api/pubsub_api/

- communication via messages
- producer/publisher sends messages to a topic
    - no knowledge of the receiving application
- consumer/subscriber subscribes to a topic
    - receives messages without knowledge of the producer
- input channel & output channel
    - input channel: used by publisher
    - output channel: used by subscriber
- requires a message broker
    - message broker: a service that routes messages between applications

Publish and subscribe in Dapr:
- **at least-once guarantees**: Dapr delivers a message at least once to every subscriber
  - a message is successfully delivered to a subscriber when the subscriber responds with a non-error response
- consumer groups handled automatically by Dapr
  - **competing consumers pattern**: when instances of the same application are subscribed to the same topic, Dapr ensures that only one instance of the application receives a message
- messages use the **CloudEvents 1.0** specification
  - CloudEvent wrapping can be turned off but that disables support for tracing and other features that depend on CloudEvents
- Dapr applications can subscribe to topics in two ways (without difference in features):
  - Declarative: subscriptions defined in a manifest
  - Programmatic: subscriptions defined in code
- Dapr has a feature called **topic scoping** to define the topics applications can publish and subscribe to; see https://docs.dapr.io/developing-applications/building-blocks/pubsub/pubsub-scopes/
- Dapr can set a timeout message (TTL) on a per-message basis
  - see https://docs.dapr.io/developing-applications/building-blocks/pubsub/pubsub-message-ttl/

## How to

### Setup a pub/sub component

Decide on the message broker (e.g., Azure Service Bus, Redis, etc...) and create a component; example for redis below ⬇️

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: pubsub
  namespace: default
spec:
  type: pubsub.redis
  version: v1
  metadata:
  - name: redisHost
    value: localhost:6379
  - name: redisPassword
    value: ""
```

And here is an example for Azure Service Bus ⬇️

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: pubsub
spec:
  type: pubsub.azure.servicebus
  version: v1
  metadata:
  - name: connectionString
    value: <CONNSTR HERE>
```

⚠️ Full list of brokers: https://docs.dapr.io/reference/components-reference/supported-pubsub/

### Subscribe to topics

As mentioned above, two ways:
- Declarative: subscriptions defined in a manifest
- Programmatic: subscriptions defined in code

The declarative way is to define subscriptions in a manifest. What else? 😉

```yaml
apiVersion: dapr.io/v1alpha1
kind: Subscription
metadata:
  name: sb-sub
spec:
  topic: sampletopic
  route: /sampler
  pubsubname: pubsub
scopes:
- nodesub
```

Above, the following is done:
- subscription to a topic called `sampletopic`
- Dapr calls a method in your code called `/sampler` with the CloudEvents message in the JSON body
- the name of the pubsub component we use is `pubsub` (e.g., see samples above; you can have multiple pubsub components with different names)
- an application with Dapr app id `nodesub` subscribes to the topic `sampletopic`

A programmatic subscription does not require a manifest. In your code, you need to have an endpoint called `dapr/subscribe`. Dapr will try to call this endpoint and expect a JSON response:

- pubsubname: the name of the pubsub component we use (e.g., see samples above; you can have multiple pubsub components with different names)
- topic: the name of the topic to subscribe to
- route: the name of the method to call when a message is received

For example:

```json
{
  "pubsubname": "pubsub",
  "topic": "sampletopic",
  "route": "/sampler"
}
```

**Note:**
- at the time of writing, there is a preview feature that allows you to subscribe to messages on different handlers, depending on the message's content; see https://docs.dapr.io/developing-applications/building-blocks/pubsub/howto-route-messages/

### Publish to topic

Your application should send a request to the Dapr sidecar like demonstrated with curl below:

```
curl -X POST http://localhost:3500/v1.0/publish/pubsub/deathStarStatus \
    -H "Content-Type: application/json" -d '{"status": "completed"}'
```

Note that you do not use CloudEvents here. Dapr will wrap the message in a CloudEvent and send it to the topic. Your content will be in the `data` field.

The consumer of the message should return `200 OK` to indicate proper receipt.

