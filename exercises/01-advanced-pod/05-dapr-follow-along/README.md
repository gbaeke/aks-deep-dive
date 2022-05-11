# Follow Along

## If you have an older version installed

```bash
dapr uninstall --all
wget -q https://raw.githubusercontent.com/dapr/cli/master/install/install.sh -O - | /bin/bash
dapr init
```

Check the dapr version with `dapr --version`. Example output:

```
CLI version: 1.7.1
Runtime version: 1.7.2
```

## Check Docker container

Run `docker ps` to check running containers. Dapr initialization should be running has added the following containers:
- redis
- zipkin
- placement

## Run a Dapr sidecar

You can run a Dapr 'sidecar' without an application:

```
dapr run --app-id app --dapr-http-port 3000
```

## Default components

During initialization, Dapr will install the following components:
- pubsub
- statestore

You can find the definition of these components in `$HOME/.dapr/components`. Both components use the redis container.

## Working with state via the sidecar

Use the state API to save state with the `statestore` component. The API in an HTTP API so we can use curl:

```
curl -X POST -H "Content-Type: application/json" -d '[{ "key": "course", "value": "deepdive"}]' http://localhost:3000/v1.0/state/statestore
```

Let's retrieve the state with another API call:

```
curl http://localhost:3000/v1.0/state/statestore/course 
```

## Check how the state is stored in Redis

Run the following commands to check the state in Redis:

```
docker exec -it dapr_redis redis-cli
keys *
hgetall "app||course"
```

## Delete the state

```
curl -v -X DELETE -H "Content-Type: application/json" http://localhost:3000/v1.0/state/statestore/course
```
