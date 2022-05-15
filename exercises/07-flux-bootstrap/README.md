# Flux bootstrap any cluster with GitHub

## Prerequisites

- flux cli installed
- gh (github) cli installed and authenticated with `gh auth login`
- kubectl

## Create a private repository

Use `gh repo create` to create a private repository. Just follow the instructions and do not clone the repo when asked.

Flux can also create the repo for you although it is best to control the creation of the repo.


## Ensure you have a working kubeconfig to a cluster

Run `kubectl version` or `kubectl cluster-info` to see you are connected to the cluster.

⚠️ If you have Docker installed, you can easily spin up a new `k3s` cluster with `k3d`

## Get your GitHub token

Go to https://github.com/settings/tokens and create a token with full repo and admin privileges.

Copy the token somewhere. You will be asked to paste it during bootstrap. Alternatively, use `export GITHUB_TOKEN=<token>` and you will not be asked.

## Bootstrap a cluster

Run the following command:

```
flux bootstrap github \
  --owner=gbaeke \
  --repository=flux-bootstrap-demo \
  --path=clusters/testclu \
  --personal
```

The above command installs Flux on your cluster but also creates a folder `clustere/testclu/flux-system` in the repo. The flux-system folder contains a kustomization.yaml that installs:
- gotk-components.yaml: installs Flux (gotk=GitOps Toolkit)
- gotk-sync.yaml: creates a source that points to the repo + a kustomization that points to the flux-system folder itself

In the repo settings, you will find a deploy key added by Flux. The deploy key is a public key. Flux has the private key to authenticate to the repo over SSH.