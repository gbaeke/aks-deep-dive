# Container Apps in your Virtual Network

**IMPORTANT:** VNET integration might not be allowed for managed environments in all regions; in North Europe it does not work; the commands below are deemed to be correct but not tested

## Create resource group and Log Analytics workspace

Set your subscription ID:

```
SUBSCRIPTION_ID=<your-subscription-id>
```

Create a resource group:

```
az group create --name rg-cavnet --location northeurope
```

Create a Log Analytics workspace:

```
az monitor log-analytics workspace create \
  --resource-group rg-cavnet \
  --workspace-name cavnet-logs
```

Retrieve workspace client ID and key:

```
LOG_ANALYTICS_WORKSPACE_CLIENT_ID=`az monitor log-analytics workspace show --query customerId -g rg-cavnet -n cavnet-logs --out tsv`
LOG_ANALYTICS_WORKSPACE_CLIENT_SECRET=`az monitor log-analytics workspace get-shared-keys --query primarySharedKey -g rg-cavnet -n cavnet-logs --out tsv`
```

## Create a VNET

```
az network vnet create -g rg-cavnet -n cavnet -l northeurope --address-prefix 10.0.0.0/16 --subnet-name default --subnet-prefix 10.0.0.0/24
az network vnet subnet create --name cacontrol -g rg-cavnet --vnet-name cavnet --address-prefix 10.0.1.0/24
```

Get the VNET and subnet resource id:

```
VNET_RESOURCE_ID=`az network vnet show -g rg-cavnet -n cavnet --query "id" -o tsv | tr -d '[:space:]'`
SUBNET_RESOURCE_ID=`az network vnet show -g rg-cavnet -n cavnet --query "subnets[0].id" -o tsv | tr -d '[:space:]'`
SUBNET_CACONTROL_RESOURCE_ID=`az network vnet subnet show -g rg-cavnet --vnet-name cavnet --name cacontrol --query "id" -o tsv | tr -d '[:space:]'`
```

## Allow Microsoft.Web to access the VNET

Note that the service principles you "create" are existing service principals in the Microsoft tenant. This allows the Container App environment to use the virtual network and subnet.

```
az ad sp create --id a94933b8-d06a-4ee9-9240-fc5ff4584f8d
az ad sp create --id bcad2cc5-28f9-4de2-8351-1ba20e241bd4
az role assignment create --assignee a94933b8-d06a-4ee9-9240-fc5ff4584f8d --scope "/subscriptions/$SUBSCRIPTION_ID" --role "Network Contributor"
az role assignment create --assignee bcad2cc5-28f9-4de2-8351-1ba20e241bd4 --scope $SUBNET_RESOURCE_ID --role "Network Contributor"
az role assignment create --assignee bcad2cc5-28f9-4de2-8351-1ba20e241bd4 --scope $SUBNET_CACONTROL_RESOURCE_ID --role "Network Contributor"
```

## Create Container Apps environment

```
az containerapp env create -n caenv -g rg-cavnet \
    --logs-workspace-id $LOG_ANALYTICS_WORKSPACE_CLIENT_ID \
    --logs-workspace-key $LOG_ANALYTICS_WORKSPACE_CLIENT_SECRET \
    --location "northeurope" --app-subnet-resource-id $SUBNET_RESOURCE_ID \
    --controlplane-subnet-resource-id $SUBNET_CACONTROL_RESOURCE_ID
```