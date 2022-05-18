# Workload identity

## Enable OIDC issuer

```bash
CLUSTER=clu-pub
RG=rg-course

az aks update -n $CLUSTER -g $RG --enable-oidc-issuer
```

## Install the web hook

```bash
AZURE_TENANT_ID=$(az account show --query tenantId -o tsv)
 
helm repo add azure-workload-identity https://azure.github.io/azure-workload-identity/charts
 
helm repo update
 
helm install workload-identity-webhook azure-workload-identity/workload-identity-webhook \
   --namespace azure-workload-identity-system \
   --create-namespace \
   --set azureTenantID="${AZURE_TENANT_ID}"
```

## Install Azure AD Workload Identity

```bash
brew install Azure/azure-workload-identity/azwi
```

## Create an AAD application with azwi
```bash
APPLICATION_NAME=WorkloadDemo
azwi serviceaccount create phase app --aad-application-name $APPLICATION_NAME
```

This creates an Azure AD app and service principal. Get the application ID with:

```bash
APPLICATION_CLIENT_ID="$(az ad sp list --display-name $APPLICATION_NAME --query '[0].appId' -otsv)"
```

You can use the APPLIACTION_CLIENT_ID to grant access to Azure reources. For example:

```bash
az keyvault set-policy --name "${KEYVAULT_NAME}" \
  --secret-permissions get \
  --spn "${APPLICATION_CLIENT_ID}"
```

**Note: ** you can also create the Azure AD app via the portal or Azure CLI

## Create a Kubernetes service account

Your pod needs a service account. You can create the service account with `kubectl` but also `azwi`:

```bash
SERVICE_ACCOUNT_NAME=sademo
SERVICE_ACCOUNT_NAMESPACE=default

azwi serviceaccount create phase sa \
  --aad-application-name "$APPLICATION_NAME" \
  --service-account-namespace "$SERVICE_ACCOUNT_NAMESPACE" \
  --service-account-name "$SERVICE_ACCOUNT_NAME"
```

This results in a service account with the following YAML:


```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  annotations:
    azure.workload.identity/client-id: ${APPLICATION_CLIENT_ID}
  labels:
    azure.workload.identity/use: "true"
  name: ${SERVICE_ACCOUNT_NAME}
  namespace: ${SERVICE_ACCOUNT_NAMESPACE}
```

**Note:** the annotation is crucial here; the web hook we installed earlier acts on the presence of this annotation.

## Configure the AAD application

Now we need to enable federation on the AAD app. That can be done on the portal but also via `azwi`:

```bash
SERVICE_ACCOUNT_NAMESPACE=default
# use  az aks show -n CLUSTER -g RG | grep oidc
# go to issuerURL/.well-known/openid-configuration to see the open id config and link to signing keys
SERVICE_ACCOUNT_ISSUER="https://oidc.prod-aks.azure.com/a887b5f1-e986-4524-81b8-077d78c44955/"

azwi serviceaccount create phase federated-identity \
  --aad-application-name "$APPLICATION_NAME" \
  --service-account-namespace "$SERVICE_ACCOUNT_NAMESPACE" \
  --service-account-name "$SERVICE_ACCOUNT_NAME" \
  --service-account-issuer-url "${SERVICE_ACCOUNT_ISSUER}"
```

## Deploy a workload

We will deploy a pod that uses the Azure CLI and the service account created earlier:

```yaml
cat <<EOF | kubectl apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: azcli-deployment
  namespace: default
  labels:
    app: azcli
spec:
  replicas: 1
  selector:
    matchLabels:
      app: azcli
  template:
    metadata:
      labels:
        app: azcli
    spec:
      serviceAccount: sademo
      containers:
        - name: azcli
          image: mcr.microsoft.com/azure-cli:latest
          command:
            - "/bin/bash"
            - "-c"
            - "sleep infinity"
EOF
```

Get a shell to the pod. We will use `az login` and login with the identity of the AAD app:

```bash
az login --federated-token "$(cat $AZURE_FEDERATED_TOKEN_FILE)" \
--service-principal -u $AZURE_CLIENT_ID -t $AZURE_TENANT_ID
```

**Note:** ensure the AAD app service principal has access to the subscription (e.g., grant reader role etc...)

The environment variables above are automatically made available by the web hook we installed earlier.

If the AAD app has access to Azure resources, you can use `az` commands to verify.

The output of az login:


```
[
  {
    "cloudName": "AzureCloud",
    "homeTenantId": "TENANTID",
    "id": "SUBID",
    "isDefault": true,
    "managedByTenants": [],
    "name": "Microsoft Azure Sponsorship",
    "state": "Enabled",
    "tenantId": "TENANTID",
    "user": {
      "name": "ID OF AAD APP",
      "type": "servicePrincipal"
    }
  }
]
```