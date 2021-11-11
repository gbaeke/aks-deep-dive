# Argo CD from a user perspective

## Tooling

Argo CD supports many ways to define Kubernetes manifests. We will focus on:
- YAML manifests
- Helm charts
- Kustomize apps

When you are just playing around, you can use a local manifests folder: `argocd app sync APPNAME --local /path/to/dir`

## Helm

To deploy a Helm chart, you can easily do so from the UI or CLI. Below is an example of an Application manifest for a Helm chart:

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: helmapp
  namespace: argocd
spec:
  destination:
    namespace: redis-tst
    server: https://kubernetes.default.svc
  project: default
  source:
    chart: redis
    helm:
      parameters:
      - name: auth.enabled
        value: "false"
    repoURL: https://charts.bitnami.com/bitnami
    targetRevision: 15.5.4
```

Above, we use the `bitnami` Helm repo and install the Helm chart. We override one parameter. An easy way to generate these YAML manifests is to create the application in the UI with manual sync. This creates an application resource in the argocd namespace that you can inspect.

We did not set a releaseName for the Helm chart. By default, the Helm release name is equal to the Application name.

When you override settings with paramaters, you can access the Argo CD build environment. The build environment has several environment variables that you can use:
- ARGOCD_APP_NAME
- ARGOCD_APP_NAMESPACE
- ARGOCD_APP_SOURCE_REPO_URL
- KUBE_VERSION
- ...


See https://argo-cd.readthedocs.io/en/stable/user-guide/build-environment/. Note that these cannot be used with Kustomize because it does not support environment variables at runtime. With Helm, just do something like:

```yaml
spec:
  source:
    helm:
      parameters:
      - name: someparam
        value: $ARGOCD_APP_NAME
```

## Projects

By default, Argo CD has a `default` project. Every application is associated with a project so if you do not create projects, all applications will belong to default.

A project is used to:
- restrict what can be deployed (from trusted git repos only)
- restrict where apps can be deployed (destination clusters and namespaces)
- restrict what kind of objects can be deployed (only certain kinds of objects like Deployments, ReplicaSets, Services, etc)

The default project (Kind=AppProject) is configured as follows:

```yaml
spec:
  clusterResourceWhitelist:
  - group: '*'
    kind: '*'
  destinations:
  - namespace: '*'
    server: '*'
  sourceRepos:
  - '*'
```

From the above it is clear that there are no restrictions on what can be deployed and where. Projects can be created in YAML (as above) or via the CLI and UI. For example:

```
argocd proj create myproject -d https://kubernetes.default.svc,mynamespace -s https://github.com/argoproj/argocd-example-apps.git
```

The above command creates a project named `myproject` and sets the destination to `https://kubernetes.default.svc` and `mynamespace`. It also sets the source repo to that can be used to deploy apps.

See https://argo-cd.readthedocs.io/en/stable/user-guide/projects/ for more information. 

**Note:** configuring projects, oidc integration and RBAC is beyond the scope of this tutorial

## Working with private repositories

Often, you will want to deploy apps from a private repository. Argo CD supports several authentication methods:
- HTTP username and password: example => `argocd repo add https://github.com/argoproj/argocd-example-apps --username <username> --password <password>`; this is rarely used
- Access token: often used with GitHub and GitLab; you first generate the token and then use the token as password; the username can be anything; for GitHub, generate a PAT => https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token
- SSH private key
- GitHub App Credential: example => `argocd repo add https://github.com/argoproj/argocd-example-apps.git --github-app-id 1 --github-app-installation-id 2 --github-app-private-key-path test.private-key.pem`

**Tip:** use credential templates; see https://argo-cd.readthedocs.io/en/stable/user-guide/private-repositories/#credential-templates

## Automated sync policy

Argo CD can automaically sync an app (in other words, apply the changes) when it detects differences between desired state in git and actual state. From the CLI:

```
argocd app set APPNAME --sync-policy automated
```

You can also do this from the manifest:

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: argotest
  namespace: argocd
spec:
  syncPolicy:
    automated: {}
  project: default
  source:
    repoURL: https://github.com/gbaeke/argotest.git
    targetRevision: HEAD
    path: manifests
  destination:
    server: https://kubernetes.default.svc
```

Automated sync only happens when the application is in state `OutOfSync`. Applications that are `Synced` or in error state, are not automatically synced. 

With automated sync, you cannot use rollbacks at the Argo CD level. Use git reverts instead.

Automated sync does not delete resources. If you want to delete resources, run a manual sync with the prune option. Alternatively, you can enable pruning with automatic sync via `argocd app set <APPNAME> --auto-prune`

Or set pruning in YAML:

```yaml
spec:
  syncPolicy:
    automated:
      prune: true
```

With automated sync, changes you make to the git repositories are automatically applied to the cluster. However, when you make changes to the cluster, you need to manually sync the app or turn on self healing: `argocd app set <APPNAME> --self-heal`

In YAML:

```yaml
spec:
  syncPolicy:
    automated:
      selfHeal: true
```

