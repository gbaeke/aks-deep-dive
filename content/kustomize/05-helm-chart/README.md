# Helm charts

Kustomize can deploy Helm charts with the `helmCharts` field. The example below installs the go-template Helm chart from the `https://gbaeke.github.io/helm-chart` repository:

```yaml
namespace: mygoapp

resources:
  - namespace.yaml
  - debug-pod.yaml

helmCharts:
- name: go-template
  repo: https://gbaeke.github.io/helm-chart
  releaseName: mygoapp
  valuesInline:
    resources:
      limits:
        cpu: 200m
        memory: 64Mi
      requests:
        cpu: 100m
        memory: 32Mi


patches:
- patch: |-
    apiVersion: v1
    kind: Pod
    metadata:
      name: go-template-test-connection
    $patch: delete

```

Since we also want to install the Helm chart in a different namespace, we use the `namespace` field in combination with `namespace.yaml` in the resources field. The Helm chart is installed in the `mygoapp` namespace.

In the `helmCharts` field, the name of the Helm chart is specified in the `name` field (go-template). Helm works with releases. We use the `releaseName` field to specify the name of the release. The release name is used to identify the release in the `helm list` command if you were to install the chart with Helm. In this case, the Helm chart is installed with kustomize and there will be no Helm release. The `releaseName` is still used in an annotation added to the resources.

Helm charts can accept parameters to override values used in the Helm template. In this chart, values can be set for the pod resource requests and limits. Above, the values are changed from the default in `valuesInline`.

When you run `kustomize build`, you will notice several things:
- you need to enable the `helm` plugin with `--enable-helm`; `kustomize build --enable-helm` or `kubectl kustomize --enable-helm`
- the chart will be downloaded from the `https://gbaeke.github.io/helm-chart` repository in a `charts` folder; this allows Kustomize to run `helm template` to generate YAML from the Helm chart

Note that you need `helm` in your path in order to use this functionality.

The result of the `kustomize build` command is a Kubernetes YAML file that contains the Helm chart plus other resources. In this case:
- the namespace
- a service for go-template with the namespace added
- a deployment for go-template with the namespace added
- a Pod used as a Helm test for the deployment

**Note:** this Helm chart includes a test that checks that the deployment is running. Helm takes steps to ensure that the test is not run on a deployment that is not running. Kustomize, however, does not do this so it is likely that the test will fail. A Helm chart typically includes a field to turn off the test, which is preferrable with Kustomize. This Helm chart however, does not have this field. To remove the test pod entirely, a strategic merge patch is used with a `delete` directive:

```yaml
patches:
- patch: |-
    apiVersion: v1
    kind: Pod
    metadata:
      name: go-template-test-connection
    $patch: delete
```

The above YAML will ensure that the `go-template-test-connection` pod is removed from the output.