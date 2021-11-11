# Argo CD Image Updater

⚠️ Image updater is under active development. Use in non-critical environments at your own risk. Time of writing: November 2021.

## What does it do?

Image updater scans image repositories for new versions of container images. It then modifies your Argo CD application in a fully automated way.

## How does it work?

You annotate your Argo CD `application` with a list of images that should be updated, together with a version constraint. For example:

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  annotations:
    argocd-image-updater.argoproj.io/image-list: gcr.io/heptio-images/ks-guestbook-demo:^0.1
    argocd-image-updater.argoproj.io/write-back-method: argocd|git
  name: guestbook
  namespace: argocd
spec:
  destination:
    namespace: guestbook
    server: https://kubernetes.default.svc
  project: default
  source:
    path: helm-guestbook
    repoURL: https://github.com/argocd-example-apps/argocd-example-apps
    targetRevision: HEAD
```

The application should use Helm or Kustomize.

The list of images is , separated. More information about images and versioning here: https://argocd-image-updater.readthedocs.io/en/stable/configuration/images/

Argo CD has two ways to make changes to your application:
- Imperative: uses the Argo CD API
- Declarative: pushes the changes to git (requires access to git repo)

You choose the write-back method per application. The default is `argocd` because it requires no further configuration. That method does not make changes to git. Instead, it modifies the application resource of Argo CD to use kustomize or Helm to override the image it reads from git. E.g., for kustomize:

```yaml
source:
  repoURL: 'https://github.com/gbaeke/argo-demo'
  path: course/overlays/prod
  targetRevision: HEAD
  kustomize:
    images:
      - 'ghcr.io/gbaeke/super:1.0.3'
destination:
  server: 'https://kubernetes.default.svc'
```

To use the git write-back method:
- use Argo CD 2.0 and above
- use the following annotation: `argocd-image-updater.argoproj.io/write-back-method: git`
- specify git credentials: `argocd-image-updater.argoproj.io/write-back-method: git:secret:argocd-image-updater/git-creds`
    - argocd-image-updater is the namespace
    - git-creds is the secret name
    - the secret can be created with `kubectl -n argocd-image-updater create secret generic git-creds --from-literal=username=someuser --from-literal=password=somepassword` where somepassword can be a GitHub PAT token
- specify branch: `argocd-image-updater.argoproj.io/git-branch: main`
- if you use Kustomize you can set `argocd-image-updater.argoproj.io/write-back-target: kustomization`; this will let Image Updater update the image as if you ran `kustomize edit set image`
    - you can also set the update path with `argocd-image-updater.argoproj.io/write-back-target: "kustomization:../../base"`


## Container Registries

Argo CD supports Docker Hub Registry, GitHub Container Registry and more. See https://argocd-image-updater.readthedocs.io/en/stable/configuration/registries/.


## Let's get started

⚠️ You can actually run image updater from your workstation with the `argocd-image-updater test <image_name>` command; get it from GitHub: https://github.com/argoproj-labs/argocd-image-updater/releases

For example, `argocd-image-updater test ghcr.io/gbaeke/super` returns:

```
INFO[0000] getting image                                 image_name=gbaeke/super registry=ghcr.io
INFO[0000] Fetching available tags and metadata from registry  image_name=gbaeke/super
INFO[0000] Found 7 tags in registry                      image_name=gbaeke/super
DEBU[0000] could not parse input tag latest as semver: Invalid Semantic Version
DEBU[0000] could not parse input tag sha-c27073d as semver: Invalid Semantic Version
DEBU[0000] could not parse input tag sha-7fb5168 as semver: Invalid Semantic Version
DEBU[0000] could not parse input tag sha-7ce9477 as semver: Invalid Semantic Version
DEBU[0000] found 3 from 3 tags eligible for consideration  image=ghcr.io/gbaeke/super
INFO[0000] latest image according to constraint is ghcr.io/gbaeke/super:1.0.2
```

Installing on Kubernetes:

```
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj-labs/argocd-image-updater/stable/manifests/install.yaml
```

This installs the updater in the `argocd` namespace.

Create a local user, e.g., image-updater in the Argo CD ConfigMap:

```yaml
data:
  # ...
  accounts.image-updater: apiKey
```

Generate a token for the user: `argocd account generate-token --account image-updater --id image-updater` and keep the token for later use.

Grant RBAC permissions to image-updater (in Argo CD RBAC ConfigMap)

```
p, role:image-updater, applications, get, */*, allow
p, role:image-updater, applications, update, */*, allow
g, image-updater, role:image-updater
```

Put the token in the `argocd-image-updater-secret`:

```
export ARGOCD_TOKEN=<token>
kubectl create secret generic argocd-image-updater-secret \
  --from-literal argocd.token=$ARGOCD_TOKEN --dry-run -o yaml | kubectl apply -n argocd -f -
```

After updating the secret, kill the updater pod so it can be restarted to pick up the new token.

Submit the following manifest (remove the demoapp and prd-superapi namespace first):

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: demoapp
  namespace: argocd
  annotations:
    argocd-image-updater.argoproj.io/image-list: ghcr.io/gbaeke/super
    argocd-image-updater.argoproj.io/write-back-method: argocd
spec:
  destination:
    server: https://kubernetes.default.svc
  project: default
  source:
    path: course/overlays/prod
    repoURL: https://github.com/gbaeke/argo-demo
    targetRevision: HEAD
```

Now sync the app.

In the logs of image updater:

```
msg="Starting image update cycle, considering 1 annotated application(s) for update"
msg="Processing results: applications=1 images_considered=1 images_skipped=0 images_updated=0 errors=0"
```

If a new image version appears in the repo, it should update using the Argo CD method.

**Note:** I do this by adding a new release to the application repo of super-api. That will trigger GitHub Actions to push a new image with the tag used in the release.

After giving it some time, the logs should say:

```
Setting new image to ghcr.io/gbaeke/super:1.0.3" alias= application=demoapp image_name=gbaeke/super
Successfully updated image 'ghcr.io/gbaeke/super:1.0.2' to 'ghcr.io/gbaeke/super:1.0.3
Processing results: applications=1 images_considered=1 images_skipped=0 images_updated=1 errors=0
```

The application is now out of sync. The live version uses 1.0.2 and the desired version is 1.0.3. You can verify that with the APP DIFF option.

You can use the SYNC option to fix that.

Note that the image you use is not in the git repo. It is set in the Application resource as follows:

```yaml
source:
  repoURL: 'https://github.com/gbaeke/argo-demo'
  path: course/overlays/prod
  targetRevision: HEAD
  kustomize:
    images:
      - 'ghcr.io/gbaeke/super:1.0.3'
destination:
  server: 'https://kubernetes.default.svc'
```