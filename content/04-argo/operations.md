# Argo CD Operations

## Declarative setup

Besides configuring Argo CD with the CLI and the UI, and creating applications interactively, you can use a declarative approach. To configure Argo CD, see [Atomic Configuration](https://argo-cd.readthedocs.io/en/stable/operator-manual/declarative-setup/#atomic-configuration)

To create an application, you use the `Application` kind. For example:

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: argotest
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/gbaeke/argotest.git
    targetRevision: HEAD
    path: manifests
  destination:
    server: https://kubernetes.default.svc
```

The above is the same as running this command:

```
argocd app create argotest --repo https://github.com/gbaeke/argotest.git --path manifests --dest-server https://kubernetes.default.svc
```

There are many additional fields you can set. For example:
- Helm specific config: parameters, releaseName, valueFiles, values, etc...
- Kustomize specific config: Kustomize version, namePrefix, images to set
- directory settings such as recursion
- syncPolicy

See https://argo-cd.readthedocs.io/en/stable/operator-manual/application.yaml for an example.

⚠️ **Important:** you can use the `app of apps` approach; this means that you install an app that, in turn creates other apps; this is great for bootstrapping clusters; see https://github.com/argoproj/argocd-example-apps/tree/master/apps/templates for an example that uses a Helm chart to do so.

## Ingress

The [docs](https://argo-cd.readthedocs.io/en/stable/operator-manual/ingress/) have a good explanation of how to configure ingress. The challenge here is that the Argo CD API server exposes both HTTP and gRPC endpoints. Not all Ingress Controllers can easily handle this.

Traefik is an example of an Ingress Controller that can terminate both TCP and HTTP connections on the same port. That way, you do not require multiple hosts or paths. See https://argo-cd.readthedocs.io/en/stable/operator-manual/ingress/#ingressroute-crd for an example of a Traefik `IngressRoute` resource.

In our exercises, we simply use port-forwarding to talk to the API server.

## Authentication

By default, Argo CD has an `admin` user with a generated password. That is ok for initial configuration. In production, you should switch to either:
- local users
- SSO integration with Auth0, Microsoft, etc...

Local users can be created by adding them to the `argocd-cm` ConfigMap. By default, that ConfigMap is empty. Once you have local users, you can disable the admin user. The following data section in the ConfigMap  adds a local user and disables admin:

```yaml
data:                                                                                                                                  accounts.geba: apiKey, login
  accounts.geba.enabled: "true"
  admin.enabled: "false"
```

Changes to the ConfigMap are effective immediately. You will not be able to login with the admin user. To set the password of a user:

```
argocd account update-password --account geba
```

**Note:** rather unintuitively, the command will ask for the current password; that is the current password of the admin user; of course, the admin user should not be disabled yet 😉

After updating the password, you can login but there will not be much you can do. Argo CD uses another ConfigMap, `argocd-rbac-cm` to configure what users can do. Initially, that ConfigMap will be empty.

You can add the following data to the ConfigMap to create a new role and assign the role to user geba:

```yaml
data:
  policy.csv: |
    p, role:org-admin, applications, *, */*, allow
    p, role:org-admin, clusters, get, *, allow
    p, role:org-admin, repositories, get, *, allow
    p, role:org-admin, repositories, create, *, allow
    p, role:org-admin, repositories, update, *, allow
    p, role:org-admin, repositories, delete, *, allow
    g, geba, role:org-admin
  policy.default: role:''
```

User `geba` will now be able to use the UI and CLI to work with applications fully. He will not be able to modify several other settings such as clusters, GnuPG keys, projects, etc...

For more information, see https://argo-cd.readthedocs.io/en/stable/operator-manual/rbac/.

