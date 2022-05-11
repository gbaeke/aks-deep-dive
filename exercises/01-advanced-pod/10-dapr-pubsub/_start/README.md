# Dapr pubsub exercise

## Step 1: Daprize your deployments

Make sure Dapr is running on your cluster: `dapr init -k --wait`

The two deployments in _start/deploy/pub.yaml and _start/deploy/sub.yaml do not use Dapr yet. Use annotations to set the following:
- app-id: unique app ids for each deployment
- app-port: app port if required; in this case deploy/sub.yaml has an endpoint that Dapr calls to deliver a message so Dapr needs to know the port (e.g. 3000)
- ensure the Dapr sidecar is enabled (dapr.io/enabled)

Example:

```yaml
annotations:
    dapr.io/enabled: "true"
    dapr.io/app-id: "nodesub"
    dapr.io/app-port: "3000"
```

**TIP**: if you are not sure, look in final/deploy/pub.yaml and final/deploy/sub.yaml

----------

## Step 2: Create an Azure Service Bus Topic and Dapr component

Create the Azure Service Bus Topic with the portal or Azure CLI:

```bash
RG=rg-dapr-pubsub
az group create -n $RG -l westeurope
namespaceName=MyNameSpace$RANDOM
az servicebus namespace create --resource-group $RG --name $namespaceName --location westeurope
az servicebus topic create --resource-group $RG --namespace-name $namespaceName --name sampleTopic
```

Get the connection string with:

```bash
az servicebus namespace authorization-rule keys list --resource-group $RG --namespace-name $namespaceName --name RootManageSharedAccessKey --query primaryConnectionString --output tsv
```

Update `pubsub-component.yaml` in the _start/deploy folder with:
- type of component
- connection string

See https://docs.dapr.io/reference/components-reference/supported-pubsub/setup-azure-servicebus/ for more information.

**TIP**: If you are not sure, look in final/deploy/pubsub-sb.yaml; that example references a Kubernetes secret; you can enter the Service Bus connection string directly in `pubsub-component.yaml`.

----------

## Step 3: Apply kustomization to the cluster

From the _start/deploy folder, run `kubectl apply -k .` That should deploy:
- the Dapr component for Azure Service Bus
- the publisher pod
- the subscriber pod

----------

## Step 4: Verify

Check the logs of the pub and sub pods to verify that the pub and sub components are running and that messages are being published and received. Use k9s to make that easy.


----------

## Step 5: Switch the message broker (optional)

If you are feeling adventurous 😉, you can switch the message broker to Redis. First install Redis with Helm:

```
helm repo add azure-marketplace https://marketplace.azurecr.io/helm/v1/repo
helm install redis azure-marketplace/redis
```

The above commands install Redis in the default namespace.

Follow the instructions displayed at the end of the installation to retrieve the Redis password. The DNS name for the Redis master will be `redis-master.default.svc.cluster.local` (port 6379).

You will need the DNS name and password in the Dapr Redis component.

If you swap the Azure Service Bus component for the Redis component, delete the Azure Service Bus component and then create the Redis component with the same name. The code uses the component name to interact with the message broker. If you give the Redis component a name different from `pubsub`, set the environment variable `PUBSUB_NAME` to the new name.