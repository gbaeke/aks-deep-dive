# Kustomize - Getting Started

## What is kustomize?

Kustomize can be used to build Kubernetes YAML files from a collection of templates. It is a declarative, composable, and extensible way to build Kubernetes YAML files.

The idea behind it is quite simple:
- you take a collection of templates and combine them into a single YAML file
- while you combine them into a single YAML file, you can modify the templates in any way you want
- modifications include:
    - adding labels to the resources
    - adding annotations to the resources
    - setting the namespace
    - changing the name of the resources with prefixes and suffixes
    - generating ConfigMaps from files, envs and literals
    - generating Secrets from files, envs and literals
    - modifying the replica count of Deployments
    - modifying the image of Deployments
    - applying patches to the resources via the `patches` field using either a strategic merge or a JSON merge patch
    - applying patches to the resources via the `patchesJson6902` field using a JSON merge patch
    - applying patches to the resources via the `patchesStrategicMerge` field using a strategic merge patch

Details about the above modifications can be found here: https://kubectl.docs.kubernetes.io/references/kustomize/kustomization/

## Example

In the folder of this REAMDME file, there are several YAML files. We want to use some of these YAML files and ensure that they get deployed to a namespace called `loadgen`.

These are the YAML files we want to apply:
- namespace.yaml
- deployment.yaml
- service.yaml
- hpa.yaml
- debug-pod.yaml

We do not want to apply these YAML files:
- loadgen.yaml 
- virtual-node-deployment.yaml

We can achieve our goal by creating the following `kustomization.yaml`:

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
namespace: loadgen

resources:
  - namespace.yaml
  - deployment.yaml
  - service.yaml
  - hpa.yaml
  - debug-pod.yaml
```

Note that the original YAML files will not be modified. The original files do not include a namespace. So we have added it to the `kustomization.yaml` file. Here is the original `service.yaml` without a namespace:

```yaml
kind: Service
apiVersion: v1
metadata:
  name:  go-template-load
spec:
  selector:
    app:  go-template-load
  type:  ClusterIP
  ports:
  - name:  http
    port:  80
    targetPort:  8080
```

The only thing we need to do is to run `kustomize build` in the folder containing the `kustomization.yaml` file. The kustomize tool can be installed with package managers such as Brew and Chocolatey. For more information, see https://kubectl.docs.kubernetes.io/installation/kustomize/.

You can also use Kustomize directly from `kubectl` because it has Kustomize built-in. Depending on your version of `kubectl`, the version of `kustomize` will be different.

Depending on your tool of choice, you can run either of the following commands in the folder containing the `kustomization.yaml` file:
- `kustomize build`
- `kubectl kustomize`

The result of running either of the above commands, will be a larger YAML file with all the resources in the resources list with the namespace set to `loadgen`. Check the snippet below:

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: loadgen
---
apiVersion: v1
kind: Service
metadata:
  name: go-template-load
  namespace: loadgen
spec:
  ports:
  - name: http
    port: 80
    targetPort: 8080
  selector:
    app: go-template-load
  type: ClusterIP
---
apiVersion: apps/v1
kind: Deployment
...
```

Note that the Service in the output contains the namespace in the metadata.

Running the above commands did not do anything to your cluster. You still need to apply the output with either of the following commands:
- kustomize build | kubectl apply -f -
- kubectl apply -k .

To remove the resources from the cluster, you can run one of the following commands:
- kustomize build | kubectl delete -f -
- kubectl delete -k .

