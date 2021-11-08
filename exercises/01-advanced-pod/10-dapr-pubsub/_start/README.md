# Dapr pubsub exercise

## Step 1: Daprize your deployments

Make sure Dapr is running on your cluster: `dapr init -l --wait`

The two deployments in pub.yaml and sub.yaml do not use Dapr yet. Use annotations to set the following:
- app-id: unique app ids for each deployment
- app-port: app port if required
- ensure the Dapr sidecar is enabled (dapr.io/enabled)

----------

## Step 2: Create an Azure Service Bus Topic and Dapr component

Create the Azure Service Bus Topic with the portal or Azure CLI:

```bash
namespaceName=MyNameSpace$RANDOM
az servicebus namespace create --resource-group YOURRG --name $namespaceName --location westeurope
az servicebus topic create --resource-group YOURRG --namespace-name $namespaceName --name sampleTopic
```
Get the connection string:

```bash
az servicebus namespace authorization-rule keys list --resource-group YOURRG --namespace-name $namespaceName --name RootManageSharedAccessKey --query primaryConnectionString --output tsv
```

Update `pubsub-component.yaml` in the deploy folder with:
- type of component
- connection string

See https://docs.dapr.io/reference/components-reference/supported-pubsub/setup-azure-servicebus/ for more information.

----------

## Step 3: Update kustomization.yaml and apply kustomization to the cluster

Update kustomization.yaml according to the comments in the file. Apply with `kubectl apply -k .`

----------

## Step 4: Verify

Check the logs of the pub and sub pods to verify that the pub and sub components are running and that messages are being published and received.