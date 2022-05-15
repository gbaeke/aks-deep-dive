# GitOps with Flux 2 on AKS

## Enabling GitOps on AKS

⚠️ The course subscription will have the AKS extension feature already enabled.

Flux v2 is installed as a cluster extension. The extension name is `microsoft.flux`. 

To enable extensions for AKS cluster, register the feature:

```
az feature register --namespace Microsoft.ContainerService --name AKS-ExtensionManager
```

⚠️ This only installs the extension manager, not Flux. Flux is just one of the extensions you can install with extension manager.

Registering the feature takes a while. Check the features of Microsoft.ContainerService with:

```
az feature list --namespace Microsoft.ContainerService -o table
```

👉 Ensure you use Azure CLI 2.15 or later:

```
az version

{
  "azure-cli": "2.32.0",
  "azure-cli-core": ...
{
```

👉 Ensure the following providers are registered:

```
az provider register --namespace Microsoft.Kubernetes
az provider register --namespace Microsoft.ContainerService
az provider register --namespace Microsoft.KubernetesConfiguration
```

## Azure CLI extensions

👉 Ensure you have the following CLI extensions installed:

```
az extension add -n k8s-configuration --upgrade
az extension add -n k8s-extension --upgrade
```

👉 Check your extensions:

```
az extension list -o table
```

Install the Flux extension (1.1.2 at the time of writing May 2022) and verify:


```
az k8s-extension create -g <RG> -c <CLU> -n flux --extension-type microsoft.flux -t managedClusters

az k8s-extension list -g <RG> -c <CLU> -t managedClusters -o table
```

⚠️ If you do not install the extension, it will be automatically installed when you create the first configuration.

## Use the portal to check if GitOps is enabled

On your AKS cluster in the portal, there should be a link **GitOps (preview)**. If the **Create** button is enabled, you are good to go.

Although you can create a GitOps configuration from the portal, we will use the Azure CLI.

## Use the Azure CLI to create a GitOps configuration

We can use a sample git repository to illustrate the features: https://github.com/Azure/gitops-flux2-kustomize-helm-mt

Let's look at the following command:

```
az k8s-configuration flux create -g lab-user-00-rg -c clu-00  -n cluster-config \
 --namespace cluster-config -t managedClusters --scope cluster \
 -u https://github.com/Azure/gitops-flux2-kustomize-helm-mt --branch main  \
 --kustomization name=infra path=./infrastructure prune=true \
 --kustomization name=apps path=./apps/staging prune=true dependsOn=["infra"]
```

The command does the following:
- create a flux configuration called `cluster-config` in a namespace called `cluster-config`. Flux Kustomizations, sources etc... will be stored there.
- config created on cluster `clu-00` in resource group `lab-user-00-rg`
- the cluster type is `managedClusters` as opposed to `connectedClusters` for Azure Arc-enabled Kubernetes
- the scope of the configuration is `cluster` as opposed to `namespace`
- the git repository is configured via -u and is `https://github.com/Azure/gitops-flux2-kustomize-helm-mt`; the branch is `main`
- two `kustomizations` are created: `infra` and `apps`
    - infra: uses the ./infrastructure directory as the base directory for the kustomization; this customization configures `sources`, `redis` and `nginx`
    - apps: uses the ./apps/staging directory as the base directory for the kustomization; this kustomization depends on `infra` to be succesfully applied; it installs the `podinfo` application with the `staging` overlay

The command might take a while because it might have to install Flux v2 first. The result of the command is JSON output. See fluxoutput.md

## What was added to the cluster?

Flux v2 will be installed on the cluster via the `microsoft.flux` extension:

- a `flux-system` namespace will be created
- it contains Flux v2 operators such as the `kustomize controller` and the `helm controller`

In the namespace `cluster-config` you will find several objects:

- a resource of kind `FluxConfig` that instructs Flux to create one or more kustomizations (in this case 2); when you `describe` this resource, you might find success and error information. Note: there is an error for the Nginx Helm chart
- two resources of kind `kustomization`: `infra` and `apps`
- a resource of kind `GitRepository` that contains the git repository referenced by the kustomizations

## Using the portal to check the Flux configurations

Although you can use the Flux cli, the portal makes it easier to check the status of the kustomizations. If your cluster already contained Nginx Ingress Controller with the ingress class `nginx`, there should be an error:

- the Flux configuration `cluster-config` should be Non-compliant
- in you click on `configuration objects` nginx should be Non-compliant
- if you click Nginx, you should see the error that points in the direction of IngressClass (although it is not clear the class already exists)


## Using the GitOps extension in VS Code

Weaveworks, the creators of Flux, have created a GitOps extension. It supports standard Flux v2 installations on any cluster. In addition, it specifically supports AKS FluxConfigurations.

⚠️ For now, install the VS Code extension via a .vsix file from the GitHub releases page: https://github.com/weaveworks/vscode-gitops-tools/releases

The plugin shows:
- status of the controllers
- list of sources
- list of workloads (Kustomizations and HelmReleases)
- status of workloads (e.g., nginx that is not compliant, click to see error details)

By right-clicking you can use suspend, resume, etc...

You can also easily create a FluxConfiguration from the plugin:
- in the repository, go to content/03-kustomize/01-cross-cutting-fields and **right-click** to create a Kustomization
  - give the Kustomization a name
  - you will be prompted to add the repo as a source

This will actually run:

```bash
az k8s-configuration flux create --name gbaeke-aks-deep-dive-main --url "https://github.com/gbaeke/aks-deep-dive.git" --branch "main" --kustomization name="demo" path="content/03-kustomize/01-cross-cutting-fields" --cluster-name clu-00 --cluster-type managedClusters --resource-group lab-user-00-rg --subscription cb0b66f7-22e3-4114-9c4a-c7f52cf80791
```

In the portal, a new FluxConfiguration should be created. If you click on it, and check the Kustomizations, the **demo** kustomization should be visible
