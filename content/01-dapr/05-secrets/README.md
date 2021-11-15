# Dapr and secrets

Dapr works with multiple secret stores to retrieve sensitive information such as connection strings, keys and tokens.

You will need the following:
- a supported secret store; some examples are:
  - Azure Key Vault
  - AWS Secrets Manager
  - Hashicorp Vault
  - Kubernetes Secrets
  - ...

⚠️ Important: only Azure Key Vault and Kubernetes Secrets have the **Stable** status at the time of this writing (October 2021)

## Secrets on a local machine

On your local machine, you can use a local file to store secrets. Create a file with JSON content like this:

```json
{
  "secret1": "value1",
  "secret2": "value2"
}
```

Next, create a component that uses the secrets file:

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: my-secrets
spec:
  type: secretstores.local.file
  version: v1
  metadata:
  - name: secretsFile
    value: <PATH TO SECRETS FILE>/mysecrets.json
  - name: nestedSeparator
    value: ":"
```

Via a `sidecar` component, you can retrieve the secrets from the file with `curl http://localhost:3500/v1.0/secrets/my-secrets/secret1`

## Using Azure Key Vault

To set up Azure Key Vault as a secret store, you will need a component:

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
    value: "[your_keyvault_name]"
  - name: azureTenantId
    value: "[your_tenant_id]"
  - name: azureClientId
    value: "[your_client_id]"
  - name: azureClientSecret
    value : "[your_client_secret]"
```

This component uses a service principal to authenticate with Azure Key Vault. You should not have the `azureClientSecret` in clear text. Instead, use a Kubernetes secret:

```
kubectl create secret generic [your_k8s_secret_name] --from-literal=[your_k8s_secret_key]=[your_client_secret]
```

In the component YAML, you can then reference the secret:

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
    value: "[your_keyvault_name]"
  - name: azureTenantId
    value: "[your_tenant_id]"
  - name: azureClientId
    value: "[your_client_id]"
  - name: azureClientSecret
    secretKeyRef:
      name: "[your_k8s_secret_name]"
      key: "[your_k8s_secret_key]"
auth:
  secretStore: kubernetes
```

Above, the `vaultName`, `azureTenantId` and `azureCLientId` are still in clear text. The `azureClientSecret` is retrieved from the Kubernetes secret you created earlier. 

Although this is easy to do, you still need to setup the service principal and store its credentials in a Kubernetes secret upfront.

### Azure Key Vault and managed identities

Instead of creating a service principal and storing the SP's secret, you can use managed identity:
- AKS needs to be installed with AAD pod identity enabled
- in the Dapr component for Key Vault, you only need to specify the Key Vault name

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
    value: "[your_keyvault_name]"
```

In the pod that runs your app and the Dapr sidecar, bind an identity that has access to Key Vault:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: mydaprdemoapp
  labels:
    aadpodidbinding: $POD_IDENTITY_NAME
```