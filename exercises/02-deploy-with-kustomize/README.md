# Kustomize exercise

In this exercise, we will deploy the pub/sub Dapr example with kustomize to two `environments` using the concept of bases and overlays. This also requires the Azure Service Bus instance, deployed earlier.

If you do not have an Azure Service Bus instance, use the following commands to provision one:

```
rg=MyRG$RANDOM
namespaceName=MyNameSpace$RANDOM
az group create --name $rg --location westeurope
az servicebus namespace create --resource-group $rg --name $namespaceName --location westeurope
az servicebus topic create --resource-group $rg --namespace-name $namespaceName --name sampleTopic
az servicebus namespace authorization-rule keys list --resource-group $rg --namespace-name $namespaceName --name RootManageSharedAccessKey --query primaryConnectionString --output tsv
```

⚠️ After the exercise, run `az group delete --name $rg`

## Create a Kustomization

We want to achieve the following:
- deploy to a dev environment using Redis as the pub/sub broker
- deploy to a prd environment using Azure Service Bus as the pub/sub broker

Steps (high-level):
- create a base folder for the base deployment (without a Component for a broker)
- create an overlays folder
  - inside the overlays folder, create a folder for the dev environment: use the base files and add the Component for Redis
    - deploy to a dev namespace
    - add a dev prefix
    - generate a secret for the Redis password
  - inside the overlays folder, create a folder for the prd environment: use the base files and add the Component for Azure Service Bus
    - deploy to a prd namespace
    - add a prd prefix
    - generate a secret for the Azure Service Bus connection string

Next:
- deploy the dev environment using kustomize (without Redis, pub/sub will not work but that is ok)
- deploy the prd environment using kustomize (with Azure Service Bus deployed and the correct connection string, pub/sub should work; check the logs of the pods)

⚠️ **IMPORTANT**: the following issues will arise:
- if you use a secretGenerator, by default it will generate a secret with a random name; that name needs to be updated in the Dapr Component but Kustomize does not know how to do that
  - **Solution**: use `configurations` in your `kustomization.yaml` file; see `kustomize-config.yaml`
- if you use a `namePrefix`, that changes the name of the `Component`; in this case, the component name is hardcoded in the code; one solution would be to supply the component name via an environment variable and use a `patch` to supply this value
  - in the `final/overlays/prd` you will find an example of retrieving the transformed component name and setting it in a variable; a patch then uses that variable to add an environment variable to the `publisher` pod; image tags 1.0.1 use the environment variable `PUBSUB_NAME`




