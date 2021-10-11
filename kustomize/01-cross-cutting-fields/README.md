# Cross-cutting fields

Cross-cutting fields are fields that are common to all resources in the Kustomization file. You have already seen the `namespace` field, which is used to specify the namespace in which the resource will be created.

In the `kustomization.yaml` below, we have added other cross-cutting fields:

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
namespace: myns

namePrefix: dev-
nameSuffix: -geba

commonLabels:
  app: superapi
  version: v1
  env: dev

commonAnnotations:
  description: "This is a the best thing since sliced bread"
  owner: "Geert Baeke"
  created: "2021-11-01"

resources:
  - namespace.yaml
  - deployment.yaml
  - service.yaml
```

With `nameSuffix` and `namePrefix`, we can create a unique name for each resource. For example, you might want to add `dev-` as a prefix to all names in the generated output. Note that the namespace will not get the configures prefix or suffix.

With `commonLabels` and `commonAnnotations`, we can add labels and annotations to all resources. For example, you might want to add `app: superapi` and `version: v1` to all resources.

When you use bases with overlays, you can combine annotations and labels. For example, you might want to add `app: superapi` and `version: v1` to all resources in the base, but also add the `env: dev` label to all resources in the dev overlay. This will become clearer in the bases and overlays section.