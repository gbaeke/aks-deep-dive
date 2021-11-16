# Dapr secrets exercise

## AAD Pod Identity

This exercise uses AAD Pod Identity to allow the Dapr sidecar to access Key Vault with a user-assigned identity. The identity is assigned to the pod that runs your app and the side car. The app in this case is just a container that allows use to use curl with the sidecar.

This requires the following:
- cluster with AAD Pod Identity enabled
- Key Vault installed
- Dapr installed with an Azure Key Vault component that only contains the name of the Key Vault (security principal not required because we will use pod identity)
- An Azure managed identity that can read secrets in the Key Vault
- A pod identity at the K8S level that uses the Azure managed identity
- A pod configured to use the pod identity when an application requests a token from Azure AD

To enabled AAD Pod Identity via the add-on, do the following:

```
az feature register --name EnablePodIdentityPreview --namespace Microsoft.ContainerService
az extension add --name aks-preview
```

**Note:** registration can take several minutes; if you already have the `aks-preview` extension, update the extension with `az extension add --name aks-preview`

⚠️ Use `az feature show --name EnablePodIdentityPreview --namespace Microsoft.ContainerService` to check the status of registration. After registration, run `az provider register -n Microsoft.ContainerService`

Create a cluster with pod identity enabled:

```
az group create --name rg-aks-pi --location westeurope
az aks create -g rg-aks-pi -n aks-pi --enable-pod-identity --network-plugin azure --node-count 1
```

If you have an existing cluster:

```
az aks update -g YOURRG -n YOURCLU --enable-pod-identity
```

When you run the update command, you will see the following in the output:

```json
"podIdentityProfile": {
    "allowNetworkPluginKubenet": null,
    "enabled": true,
    "userAssignedIdentities": null,
    "userAssignedIdentityExceptions": null
  }
```

## Install Dapr

Ensure Dapr is installed. If not:

```
dapr init -k
dapr status -k
```

Proceed when `dapr status` reports `True` for all components.

## Create an Azure identity

Use the following command to create an Azure identity and save the client ID and resource ID:

```
az identity create --resource-group rg-aks-pi --name appid
export IDENTITY_CLIENT_ID="$(az identity show -g rg-aks-pi -n appid --query clientId -otsv)"
export IDENTITY_RESOURCE_ID="$(az identity show -g rg-aks-pi -n appid --query id -otsv)"
```

The first command results in a managed identity `appid`. It will be a user assigned managed identity. The client ID and resource ID can also be retrieved from the Azure portal. The client ID can be used to grant permissions to resources. It is not needed to create the pod identity below:


## Create a pod identity

Where the Azure identity is created in Azure, the pod identity is created in Kubernetes:

```
az aks pod-identity add --resource-group <RG> --cluster-name <CLUSTER> --namespace <K8S-NAMESPACE>  --name <PODIDNAME> --identity-resource-id ${IDENTITY_RESOURCE_ID}
```

The above command will result in:
- a resource of kind `AzureIdentity` in the default namespace.
- the spec of the resource contains the clientID and resourceID of the Azure identity
- the managed identity of the `AKS cluster` is granted the `Managed Identity Operator` role over the managed identity (appid in this example)
- the AKS resource is updated with the identity ⬇️

```json
"podIdentityProfile": {
    "allowNetworkPluginKubenet": null,
    "enabled": true,
    "userAssignedIdentities": [
      {
        "bindingSelector": null,
        "identity": {
          "clientId": "428d8b6a-8019-412b-87c5-e482f4050350",
          "objectId": "030b2807-7818-487a-bf1f-c2afe2844f7e",
          "resourceId": "/subscriptions/d1d3dadc-bc2a-4495-b8dd-70443d1c70d1/resourcegroups/az-k8s-7d9e-rg/providers/Microsoft.ManagedIdentity/userAssignedIdentities/appid"
        },
        "name": "appid",
        "namespace": "default",
        "provisioningInfo": null,
        "provisioningState": "Assigned"
      }
    ],
    "userAssignedIdentityExceptions": null
  }
```

## Use the identity in a pod

Use the following label in your pod:

```yaml
labels:
    aadpodidbinding: appid
```

## Create a secret

Create a key vault and a secret. Ensure that the Azure Identity created earlier can read the secret.

## Create a Dapr component for Key Vault

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: azurekeyvault
  namespace: default
spec:
  type: secretstores.azure.keyvault
  version: v1
  metadata:
  - name: vaultName
    value: "kv-azk8s7d9e"
```

Use `kubectl apply -f` to submit the component to the cluster.

## Retrieve the secret from the application pod

Use `pod.yaml` in manifests. It will add the Dapr sidecar to the pod. Obtain a shell to the `debug` container and issue the following command:

```
curl http://localhost:3500/v1.0/secrets/azurekeyvault/mysecret
```

The response should be like below:

```json
{"mysecret":"verysecret"}
```

## Troubleshooting

The user you are using might not have the role of `dapr-operator-admin`. Assign that role to your user. This will be required when you use AAD to logon instead of a certificate. To avoid having to run the below command, use `az aks get-credentials` with the `--admin` flag.

