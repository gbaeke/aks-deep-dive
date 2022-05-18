# Secret store CSI driver

Enable the secret store CSI driver with `az aks enable-addons`:

```bash
RG=rg-course
CLUSTER=clu-pub

az aks enable-addons --addons=azure-keyvault-secrets-provider --name=$CLUSTER --resource-group=$RG
```

If you enabled the provider during installation, you will get a message that states it is already installed.

# Creating a Key Vault and a secret

⚠️ Important: run all commands in this document from the same shell; the variables are reused

Use the following commands to create an Azure Key Vault and a secret:

```bash
KV=geba$RANDOM
RG=rg-course
SECRET=demosecret
VALUE=demovalue
CLUSTER=clu-pub

# create the key vault and turn on Azure RBAC; we will grant a managed identity access to
# this key vault below
az keyvault create --name $KV --resource-group $RG --location westeurope --enable-rbac-authorization true

# get the subscription id
SUBSCRIPTION_ID=$(az account show --query id -o tsv)

# get your user object id
USER_OBJECT_ID=$(az ad signed-in-user show --query objectId -o tsv)

# grant yourself access to key vault
az role assignment create --assignee-object-id $USER_OBJECT_ID --role "Key Vault Administrator" --scope /subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RG/providers/Microsoft.KeyVault/vaults/$KV

# add a secret to the key vault
az keyvault secret set --vault-name $KV --name $SECRET --value $VALUE
```

Grant the managed identity called `azurekeyvaultsecretsprovider-<CLUSTER>` access to Key Vault.


```bash

# get the managed identity id
IDENTITY_ID=$(az identity show -g MC\_$RG\_$CLUSTER\_westeurope --name azurekeyvaultsecretsprovider-$CLUSTER --query principalId -o tsv)

# assign the role
az role assignment create --assignee-object-id $IDENTITY_ID --role "Key Vault Administrator" --scope /subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RG/providers/Microsoft.KeyVault/vaults/$KV
```

## Create a SecretProviderClass in the default namespace

⚠️ In what follows, you need to change three values in secretproviderclass.yaml:
- userAssignedIdentityID
- tenantID
- keyvaultName

👉 Set `keyvaultName` to the value of $KV.

👉 You will need the clientId of the managed identity that you granted access to Key Vault. Use the following command to get the clientId:

```bash
az aks show -g $RG -n $CLUSTER --query addonProfiles.azureKeyvaultSecretsProvider.identity.clientId -o tsv
```
    
Use the output of the above command as the value of `userAssignedIdentityID` in secretproviderclass.yaml.

👉 Obtain your tenant ID with `az account show --query tenantId -o tsv`. Use the output of the command as the value of `tenantID` in secretproviderclass.yaml.

Now apply the secretproviderclass.yaml file to the Kubernetes API:

```bash
kubectl apply -f secretproviderclass.yaml
```

If the three values are not set properly, secrets will not be mounted and you will need to describe the pod and get events to find out what went wrong.

## Create pods that mount the secret as a volume

Use `kubectl apply -f secretpod.yaml` to create a pod that mounts the secret. The pod might be stuck in the ContainerCreating status for a while. If it is stuck, describe the pod and check events.

The volume is mounted in the pod.spec with:

```yaml
volumes:
- name:  secret-store
    csi:
        driver: secrets-store.csi.k8s.io
        readOnly: true
        volumeAttributes:
            secretProviderClass: "demo-secret"
```

You choose the name of the volume (here `secret-store`) and set the secretProviderClass to use with the code above.

In the container spec, you then mount the volume to a path:

```yaml
volumeMounts:
    - name:  secret-store
      mountPath:  "mnt/secret-store"
      readOnly: true
```

Above, in `name` you reference the volume name. The secrets in the secretProviderClass will be mounted as files under `/mnt/secret-store`. You choose the mount path.

Use k9s or kubectl to check the following:
- there should be a secret called `demosecret`. The secret is only created when it is referenced and removed when it is not. E.g., if you delete the deployment, the secret will be deleted as well.
- get a shell into the pod and go to `/mnt/secret-store`. Use the `ls` command to see the file and `cat` the file.