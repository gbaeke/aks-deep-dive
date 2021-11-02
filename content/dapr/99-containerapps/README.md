# Dapr with Azure Container Apps (preview)

## Install Container Apps extension

```
az extension add \
  --source https://workerappscliextension.blob.core.windows.net/azure-cli-extension/containerapp-0.2.0-py2.py3-none-any.whl
```

## Deploy Container Apps Environment

Create a resource group:

```
az group create --name rg-dapr --location westeurope
```

Create a Log Analytics workspace:

```
az monitor log-analytics workspace create \
  --resource-group rg-dapr \
  --workspace-name dapr-logs
```

Retrieve workspace client ID and key:

```
LOG_ANALYTICS_WORKSPACE_CLIENT_ID=`az monitor log-analytics workspace show --query customerId -g rg-dapr -n dapr-logs --out tsv`
LOG_ANALYTICS_WORKSPACE_CLIENT_SECRET=`az monitor log-analytics workspace get-shared-keys --query primarySharedKey -g rg-dapr -n dapr-logs --out tsv`
```

Create the Azure Container Apps environment:

```
az containerapp env create \
  --name dapr-ca \
  --resource-group rg-dapr \
  --logs-workspace-id $LOG_ANALYTICS_WORKSPACE_CLIENT_ID \
  --logs-workspace-key $LOG_ANALYTICS_WORKSPACE_CLIENT_SECRET \
  --location northeurope
```

## Create Azure Service Bus


```bash
namespaceName=MyNameSpace$RANDOM
az servicebus namespace create --resource-group rg-dapr --name $namespaceName --location northeurope
az servicebus topic create --resource-group rg-dapr --namespace-name $namespaceName --name sampleTopic
az servicebus namespace authorization-rule keys list --resource-group rg-dapr --namespace-name $namespaceName --name RootManageSharedAccessKey --query primaryConnectionString --output tsv
```

## Create a components.yaml file

```yaml
# components.yaml for Azure Service Bus
- name: pubsub
  type: pubsub.azure.servicebus
  version: v1
  metadata:
  - name: connectionString
    value: Endpoint=sb://dapr-pubsub.servicebus.windows.net/;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=YOUR_KEY
```

**Note:** we do not make use of secrets here, but you can use secrets to store your connection strings

## Create the publisher container app

```
az containerapp create \
  --name daprpub \
  --resource-group rg-dapr \
  --environment dapr-ca \
  --image gbaeke/dapr-pub:1.0.0 \
  --min-replicas 1 \
  --max-replicas 1 \
  --enable-dapr \
  --dapr-app-id daprpub \
  --dapr-components ./components.yaml
```

## Create the subscripter container app

```
az containerapp create \
  --name daprsub \
  --resource-group rg-dapr \
  --environment dapr-ca \
  --image gbaeke/dapr-sub:1.0.0 \
  --min-replicas 2 \
  --max-replicas 5 \
  --enable-dapr \
  --dapr-app-port 3000 \
  --dapr-app-id daprsub \
  --dapr-components ./components.yaml
```

## Look at the logs

```
az monitor log-analytics query \
  --workspace $LOG_ANALYTICS_WORKSPACE_CLIENT_ID \
  --analytics-query "ContainerAppConsoleLogs_CL | where ContainerAppName_s == 'daprsub' | project ContainerAppName_s, Log_s, TimeGenerated | take 5" \
  --out table
```
