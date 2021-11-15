# Deployment

## Deployment with AKS Deploy Helper

Use Deploy Helper (https://azure.github.io/Aks-Construction/) to deploy AKS. Use the following settings:
- I want a managed environment
- Cluster with additional security controls
- Deploy tab
  - Set your resource group and cluster name
  - Verify your IP is in the **Current IP Address** text box
- Cluster details tab
  - Free cluster
  - Cost-optimized system pool type with min scale 1 and max scale 5
  - 4 vCPU, 14GB VMs - large enough cach to use ephemeral disks
  - Deploy across zones 1,2,3
  - Disable auto upgrades
  - AAD authentication
  - **Disable** Azure RBAC for K8S auth and specify group object ID of a group that will have admin role of the cluster
- Addon details
  - Select **No, I do not need a layer 7 proxy**

The above choices lead to the following deployment commands:

```
# Create Resource Group 
az group create -l WestEurope -n az-k8s-3cy8-rg 

# Deploy template with in-line parameters 
az deployment group create -g az-k8s-3cy8-rg  --template-uri https://github.com/Azure/Aks-Construction/releases/download/0.3.0-preview/main.json --parameters \
	resourceName=az-k8s-3cy8 \
	kubernetesVersion=1.20.9 \
	agentVMSize=Standard_DS3_v2 \
	agentCount=1 \
	agentCountMax=20 \
	osDiskType=Managed \
	custom_vnet=true \
	enable_aad=true \
	registries_sku=Premium \
	acrPushRolePrincipalId=$(az ad signed-in-user show --query objectId --out tsv) \
	omsagent=true \
	retentionInDays=30 \
	networkPolicy=calico \
	azurepolicy=audit \
	availabilityZones=[\"1\",\"2\",\"3\"] \
	authorizedIPRanges=[\"78.22.241.198/32\"] \
	azureKeyvaultSecretsProvider=true \
	createKV=true \
	kvOfficerRolePrincipalId=$(az ad signed-in-user show --query objectId --out tsv)
```

⚠️ Important:
- Check AAD integration after deployment: was the Object ID set?
- Check Azure Policy: was the audit policy set?

The answer to the above questions probably is **NO** 😉. Deploy Helper is a great tool for learning but it still needs some work. See https://github.com/Azure/Aks-Construction to participate.

⚠️ Before continuing, in the **Configuration** of the cluster, add the **AKS** group to the list of Admin Azure AD groups.

## Deploy sample workload

This workload uses an image in ACR: crazk8skjfsa6ufncm6ehkyi.azurecr.io/super:1.0.3

To import the image to your ACR, use:

```
az acr import \
  --name YOURACR \
  --source ghcr.io/gbaeke/super:1.0.3 \
  --image super:1.0.3
  --resource-group YOURRG
```

After import, update `deployment.yaml` in the `manifests` folder with your ACR name.