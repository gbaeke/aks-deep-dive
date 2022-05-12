# Publish a chart

## What is a chart repository?

Simply a HTTP server with `index.yaml` and packaged charts. You can simply use an Azure Storage Account:

```
RAND=$RANDOM
RG=rg-chart-storage
az group create --name $RG --location westeurope
az storage account create -n storage$RAND -g $RG -l westeurope --sku Standard_LRS --kind StorageV2
az storage blob service-properties update --account-name storage$RAND --static-website
```

In the storage account you might have a charts folder like: `https://storage23439.z6.web.core.windows.net/charts` (or just store them in the root folder).

Inside the charts folder:
- `index.yaml`
- `mychart-0.1.0.tgz`
- ...

You can generate the `index.yaml` file with the following command:

```
helm repo index
```

## Package a chart and creating an idex

To package a chart and create a .tgz, in the folder with the chart, run:

```
helm package .
```

The output is a file like `superapi-0.1.0.tgz`. Put that file in a folder and then run the `helm repo index` command in that folder.

Example index.yaml:

```yaml
apiVersion: v1
entries:
  superapi:
  - apiVersion: v2
    appVersion: 1.0.2
    created: "2021-11-19T14:42:47.204586891+01:00"
    description: A Helm chart for Kubernetes
    digest: a3e719f9591f5ab122f21f80fb21106a94d7252d8ee5da8f4a521bdb4df13847
    name: superapi
    type: application
    urls:
    - superapi-0.1.0.tgz
    version: 0.1.0
generated: "2021-11-19T14:42:47.202528842+01:00"
```

Now copy the index.yaml and .tgz to the storage account's `$web` container. You can use Storage Browser in the Azure Portal to drag and drop the files.

# Adding the repo to Helm

Use the `helm repo add` command to add the chart repository to Helm:

```
helm repo add demo https://storage23439.z6.web.core.windows.net/
```

Next, run `helm template demo/superapi` to verify it worked.