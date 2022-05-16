# Flux bootstrap any cluster with GitHub

## Prerequisites

- flux cli installed (`brew install flux` or `curl -s https://fluxcd.io/install.sh | sudo bash` )
- gh (github) cli installed and authenticated with `gh auth login`
- kubectl

## Create a private repository

⚠️ **Optional:** Flux can create the repository for you during `flux bootstrap`

Use `gh repo create` to create a private repository. Just follow the instructions and do not clone the repo when asked.


## Ensure you have a working kubeconfig to a cluster

Run `kubectl version` or `kubectl cluster-info` to see you are connected to the cluster.

⚠️ If you have Docker installed, you can easily spin up a new `k3s` cluster with `k3d`

## Get your GitHub token

Go to https://github.com/settings/tokens and create a token with full repo privileges.

Copy the token somewhere. You will be asked to paste it during bootstrap. Alternatively, use `export GITHUB_TOKEN=<token>` and you will not be asked.

## Bootstrap a cluster

Run the following command:

```
export GH_USER=<your GitHub username>
export CLUSTER_NAME=<your cluster name>
export GITHUB_TOKEN=<token>

flux bootstrap github \
  --owner=$GH_USER \
  --repository=flux-bootstrap-demo \
  --path=clusters/$CLUSTER_NAME \
  --personal
```

The above command installs Flux on your cluster but also creates a folder `clusters/testclu/flux-system` in the repo. The flux-system folder contains a kustomization.yaml that installs:
- gotk-components.yaml: installs Flux (gotk=GitOps Toolkit)
- gotk-sync.yaml: creates a source that points to the repo + a kustomization that points to the flux-system folder itself

In the repo settings, you will find a deploy key added by Flux. The deploy key is a public key. Flux has the private key to authenticate to the repo over SSH.

## Terraform

See [Terraform README](exercises/06-flux-bootstrap/terraform/README.md)