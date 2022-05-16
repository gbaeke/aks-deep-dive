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
export GH_USER=gbaeke
export CLUSTER_NAME=clu-00
export GITHUB_TOKEN=token

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

## Use the Flux CLI

```bash
# check the Flux installation
flux check

# check flux resources such as git repos and kustomizations
flux get all

# get kustomizations
flux get kustomizations

# suspend a kustomization (stop the scheduled reconciliation)
flux suspend kustomization flux-system

# resume a kustomization (resume scheduled reconciliation)
flux resume kustomization flux-system

# reconcile a kustomization NOW
flux reconcile kustomization flux-system

# export a kustomization to YAML
flux export kustomization flux-system

# export a git repo to YAML
flux export source git flux-system
```

## Adding our own Kustomization

Clone the bootstrap repository to your local machine. E.g.:

```
git clone https://github.com/gbaeke/flux-bootstrap-demo.git && cd flux-bootstrap-demo
```

Create a folder called `apps` with `mkdir apps`

Copy deployment.yaml, service.yaml, namespace.yaml and kustomization.yaml in the folder of this README to the `apps` folder.

Commit the changes:

```bash
git add .
git commit -m apps .
git push
git status # should say nothing to commit
```

Now we have added files to the repository in the apps folder. We do not need a new source because bootstrap already created one.

We do need a `kustomization` to deploy this app to the cluster. To make this easy, we can export and modify the existing customization. You can of course start from scratch or use `flux create` for this.

In your repo, go to the directory of your cluster (`/clusters/<clustername>`) and run the following command:

```
flux export kustomization flux-system > app.yaml
```

Modify app.yaml:

  
```yaml
apiVersion: kustomize.toolkit.fluxcd.io/v1beta2
kind: Kustomization
metadata:
  labels:
    kustomize.toolkit.fluxcd.io/name: flux-system
    kustomize.toolkit.fluxcd.io/namespace: flux-system
  name: app
  namespace: flux-system
spec:
  interval: 1m0s
  path: ./apps
  prune: true
  sourceRef:
    kind: GitRepository
    name: flux-system
```

Use git to push the changes to main.

Flux will try to deploy the app by reconciling the kustomization. There should be an error because `kustomization.yaml` in the `apps` folder references a file that is not in the folder (`ingress.yaml`). Fix this removing `ingress.yaml` from the resources list. Ensure you commit and push the change.

You can verify the error (and the fix) with `flux get kustomizations`. The `app` kustomization should now be reconciled.

On the cluster, there should be a `flux-app` namespace with the deployment and service. You can remove the deployment but it will appear again in a minute. Or run `flux reconcile kustomization app`. The interval is set to 1m so you will need to be fast. 😉

## Deploy a Helm chart

Let's install `Redis` on our cluster with the chart from BitNami. We need two things:

- a source for the chart
- a Helm release

To add the source, create `/clusters/<YOUR CLUSTER NAME>/bitnami-helm-source.yaml` and add the following:

```yaml
apiVersion: source.toolkit.fluxcd.io/v1beta1
kind: HelmRepository
metadata:
  name: bitnami
  namespace: flux-system
spec:
  interval: 30m
  url: https://charts.bitnami.com/bitnami
```

This adds the Bitnami chart repository to the cluster. The index of the repository is updated every 30 minutes and cached locally by Flux. This is somewhat similar to `helm repo add`.

Use `flux get sources helm` to see the new source. Give it some time.

No add a Helm release. Create `/clusters/<YOUR CLUSTER NAME>/redis-helm-release.yaml` and add the following:

```yaml
apiVersion: helm.toolkit.fluxcd.io/v2beta1
kind: HelmRelease
metadata:
  name: redis
  namespace: flux-system
spec:
  targetNamespace: redis
  releaseName: redis
  chart:
    spec:
      chart: redis
      sourceRef:
        kind: HelmRepository
        name: bitnami
        namespace: flux-system
      version: "11.3.4"
  interval: 10m0s
  install:
    remediation:
      retries: 3
  values:
    usePassword: false
    cluster:
      enabled: false
    master:
      persistence:
        enabled: false
```

⚠️ **Important:** we add the HelmRelease to our cluster folder. This works because there is a kustomization that uses that folder to apply all objects it finds in it.

Be sure to commit the file to git. You can run `flux reconcile` on both the git source and the `flux-system` kustomization.

Did the installation succeed? It shouldn't because the namespace `redis` does not exist. Flux will not create that namespace. What is the solution here?
