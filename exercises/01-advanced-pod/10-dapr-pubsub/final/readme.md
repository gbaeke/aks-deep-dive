# Pubsub on Kubernetes exercise

## Running locally

### Subscriber

To run the subscriber:

`dapr run --app-id sub --app-port 3000 node app.js`

Notes:
- subscriber has endpoint for dapr to retrieve the pubsub topic
- subscriber has endpoint for dapr to receive messages picked up by the sidecar
- Dapr sidecar needs to know the port number to reach these endpoints
- Note that we use the `pubsub` component (default component name for pubsub on local Dapr; uses Redis)

### Publisher

To run the publisher:

`dapr run --app-id pub node app.js`

The Dapr sidecar does not need to communicate with your application. There is no need to specify the port number. The app calls into the Dapr sidecar to publish messages.

### PubSub backend on local machine

Backend is Redis Streams, automatically installed and configured during **dapr init**. The component is called `pubsub`.

## Deploying to Kubernetes

To deploy this application to Kubernetes, the following steps are required:
- install Dapr on the cluster: `dapr init -k --wait` or use the Helm chart
- create and push container images for the publisher and subscriber
- create a deployment for the publisher and subscriber and use Dapr annotations like:
    - dapr.io/app-id: name of your app
    - dapr.io/app-port: port number to reach the app, if required by dapr
    - dapr.io/enabled: set to true to inject the Dapr sidecar
- create a component of type `pubsub.azure.servicebus`

**Note:** there are two ways to inform a subscriber about the topic:
- respond to a request from the Dapr sidecar with JSON containing the topic name, pubsub name and route
- create a subscription that declares the topic name and pubsub name (see [subscription](deploy/subscription.yaml))

### Create and push container images

Create the pub image (from the pub folder):

```
docker build -t gbaeke/dapr-pub:1.0.0 .
docker push gbaeke/dapr-pub:1.0.0
```

Create the sub image (from the sub folder):

```
docker build -t gbaeke/dapr-sub:1.0.0 .
docker push gbaeke/dapr-sub:1.0.0
```

### Create Azure Service Bus instance

The following commands will work in Bash:

```bash
namespaceName=MyNameSpace$RANDOM
az servicebus namespace create --resource-group YOURRG --name $namespaceName --location westeurope
az servicebus topic create --resource-group YOURRG --namespace-name $namespaceName --name sampleTopic
az servicebus namespace authorization-rule keys list --resource-group YOURRG --namespace-name $namespaceName --name RootManageSharedAccessKey --query primaryConnectionString --output tsv
```

### Deploy the application with Kustomize

In the deploy folder, there are several resources:
- deployments for pub and sub: pub.yaml and sub.yaml
- pubsub-sb.yaml: the Azure Service Bus component with the connection string in a secret reference
- kustomization.yaml to deploy the above components

In kustomization.yaml, make the following changes:
- use `images:` to specify the images for the pub and sub deployments (or remove images: and update pub.yaml and sub.yaml)
- update the `secretGenerator` and change the connection string to the one from the Azure Service Bus instance

To deploy the application, from the deploy folder, run `kubectl apply -k .`

Open the Dapr dashboard with `dapr dashboard -k` and verify you see the applications and the pubsub component.

Check the logs of the publisher and subscribers with `kubectl logs <pod-name>`:
- you should see the publisher publish a message every 5 seconds with a 204 response
- you should see the subscribers receiving and logging the messages in a CloudEvent format 