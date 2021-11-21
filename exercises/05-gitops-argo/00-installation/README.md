# Installing Argo CD

See https://argo-cd.readthedocs.io/en/stable/operator-manual/installation/

Non HA installation with full admin access & kustomize:

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

namespace: argocd
resources:
- https://raw.githubusercontent.com/argoproj/argo-cd/v2.0.4/manifests/install.yaml
```

Save the above file and install with `kubectl apply -k .`

You should see the following deployments in the `argocd` namespace:
- argocd-dex-server
- argocd-server
- argocd-redis-ha-haproxy
- argocd-repo-server




