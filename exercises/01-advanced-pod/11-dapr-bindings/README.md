# Dapr bindings exercise

In this example, we use Dapr on our machine with an Azure Blob Storage output binding.

## Create the storage account

```
rand=$RANDOM
az group create --name dapr-bindings-rg --location westeurope
az storage account create -n daprbinding$rand -g dapr-bindings-rg -l westeurope --sku Standard_LRS
# retrieve the storage account key
az storage account keys list -n daprbinding$rand -g dapr-bindings-rg
```

Update `components/azure-storage-component.yaml` with the storage account name and key.


## Run a Dapr sidecar

Run a Dapr sidecar without an actual application (from the 11-dapr-bindings directory):

```
dapr run -a outputsample -d ./components --dapr-http-port 3500
```

In another shell, run the following commands:

```
image=$(base64 sample.png -w 0)
curl -d '{ "operation": "create", "data": "'$image'", "metadata": { "blobName": "sample.png" } }' \
      http://localhost:3500/v1.0/bindings/blobby

```

**Note:** ensure $image is between "'...""

Now list the blobs:
```
az storage blob list --container-name container1 --account-name <STORAGEACCOUNT> --account-key <KEY>
```
