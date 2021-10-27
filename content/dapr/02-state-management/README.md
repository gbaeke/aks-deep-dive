# State Management

State management allows your application to store data as key-value pairs in supported state stores. 

Some of the state stores are listed below:
- Redis
- Azure Cosmos DB
- Hashicorp Consul
- MongoDB
- Memcached
- ... and many more (see [state stores](https://docs.dapr.io/reference/components-reference/supported-state-stores/))

To save state, you simply do a HTTP POST to the Dapr sidecar using a URL like `http://localhost:3500/v1.0/state/myStateStore` with a JSON body like this:

```json
[{
  "key": "myKey",
  "value": "myValue"
}]
```

myStateStore is the name of a component that uses one of the supported state stores.

To get state, you simply do a HTTP GET to the Dapr sidecar using a URL like `http://localhost:3500/v1.0/state/myStateStore/myKey`.

## State store behaviour

By default, applications should assume a data store is **eventually consistent** and uses the **last-write-wins** concurrency pattern. You can attach metadata to state operations to control the behaviour of the data store.

Instead of **last-write-wins**, you can use optimistic concurrency control (OCC) with ETags. This effectively means that you can only update the state if the ETag matches the current ETag and that you switch to **first-write-wins** if the ETag doesn't match. The Etag is typically set by the data store when you write the state. To update the state, you first obtain the ETag and then use the ETag in the update.

You can also set a consistency option and switch to **strong consistency**. Dapr will wait until all replicas are updated. The exact behaviour depends on the state store implementation.

The following example shows how to use an etag and set strong consistency and first-write-wins with curl:

```bash
curl -X POST http://localhost:3500/v1.0/state/starwars \
  -H "Content-Type: application/json" \
  -d '[
        {
          "key": "weapon",
          "value": "DeathStar",
          "etag": "xxxxx",
          "options": {
            "concurrency": "first-write",
            "consistency": "strong"
          }
        }
      ]'
```

### Bulk operations

There are two bulk operations:
- bulk
- multi

Bulk operations simply have multiple key/value pairs as payload. Dapr will execute all operations in the payload in the order they are specified. Multi operations are similar to bulk operations but they can be used to execute multiple operations in parallel and are transactional.

```json
[
    {
        "key": "weapon",
        "value": "DeathStar",
        "etag": "1234"
    },
    {
        "key": "planet",
        "value": {
        "name": "Tatooine"
        }
    }
]
```

Multi operations have multiple operations as payload:

```json
{
    "operations": [
        {
        "operation": "upsert",
        "request": {
            "key": "key1",
            "value": "myData"
        }
        },
        {
        "operation": "delete",
        "request": {
            "key": "key2"
        }
        }
    ],
    "metadata": {
        "partitionKey": "planet"
    }
}
```

Not all state stores support multi-item transactions. The following do (not the full list):

- Redis
- Azure Cosmos DB
- MongoDB