# Service Mesh with OSM

**Note:** in exercises, you can find 00-service-mesh which contains a step-by-step exercise to get started with Linkerd; this document discusses OSM

## Capabilities

OSM, like Linkerd and Istio, is a service mesh with the following capabilities:
- integrated in AKS via an add-on (fully supported and managed)
- service-to-service encryption via mTLS
- automatic sidecar injection; the sidecar uses **Envoy** while Linkerd uses their own proxy, written in Rust
- traffic shifting
- fine-grained access control policies
- observability with Prometheus, Grafana and Jaeger but you have to install all those bits yourself (Linkerd provides the viz add-on); for OSM see https://docs.microsoft.com/en-us/azure/aks/open-service-mesh-open-source-observability; or use Azure Monitor and App Insights, see https://docs.microsoft.com/en-us/azure/aks/open-service-mesh-azure-monitor


## Installation

Open Service Mesh (OSM) can be installed on AKS as an add-on. For a new cluster:

```
az aks create -n osm-cluster -g rg-aks --node-osdisk-type Ephemeral --node-osdisk-size 30 --network-plugin azure --enable-managed-identity -a open-service-mesh --node-count 2
```

**Sidenote:** ephemeral OS is not required for OSM; AKS will actually default to ephemeral OS if possible; OS disk must fit in the VM cache; the automatic use of ephemeral OS depends entirely if the default OS disk size fits in the cache; it does not on Standard_DS2_v2 but it does on Standard_D8s_v3 (for example); of course, you can adjust the OS disk size to fit in the cache; the command above does that

**Note:** run `az feature register --namespace "Microsoft.ContainerService" --name "AKS-OpenServiceMesh"` if you get an error; use `az feature list -o table --query "[?contains(name, 'Microsoft.ContainerService/AKS-OpenServiceMesh')].{Name:name,State:properties.state}"` to check registration status (can take a while)

On an existing cluster, run:

```
az aks enable-addons --addons open-service-mesh -g <my-osm-aks-cluster-rg> -n <my-osm-aks-cluster-name>
```

## Validate the installation

Please check https://docs.microsoft.com/en-us/azure/aks/open-service-mesh-deploy-addon-az-cli#validate-the-aks-osm-add-on-installation

## OSM Configuration

OSM uses a ConfigMap for configuration. To view the ConfigMap, run `kubectl get meshconfig osm-mesh-config -n kube-system -o yaml`

You will notice that `enablePermissiveTrafficPolicyMode` is **true**. In that mode, traffic policy enforcement is bypassed. You can turn this off with `kubectl patch meshconfig osm-mesh-config -n kube-system -p '{"spec":{"traffic":{"enablePermissiveTrafficPolicyMode":false}}}' --type=merge`. When you turn it off, you need to create policies to allow traffic to and from the mesh.

## Install client

Be sure to set the correct version in OSM_VERSION below. You can run the command below to get the osm-controller version:

```
kubectl get deployment -n kube-system osm-controller -o=jsonpath='{$.spec.template.spec.containers[:1].image}'
```

In my case, that resulted in version 0.9.2 which we use below:

```
# Specify the OSM version that will be leveraged throughout these instructions
OSM_VERSION=v0.9.2

curl -sL "https://github.com/openservicemesh/osm/releases/download/$OSM_VERSION/osm-$OSM_VERSION-linux-amd64.tar.gz" | tar -vxzf -
```

Next, run:

```
sudo mv ./linux-amd64/osm /usr/local/bin/osm
sudo chmod +x /usr/local/bin/osm
```

You can now use the `osm` command to configure and manage the mesh. You should not, however, use `osm install` as that will interfere with the add-on. Run `osm version` to verify that the correct version is installed.

Why would you want to use osm CLI? One reason is to manage namespaces. By adding a namespace, you ensure injection of the OSM sidecar. Run the following commands:

```
kubectl create namespace osm-test
osm namespace add osm-test
```

This results in `Namespace [osm-test] successfully added to mesh [osm]`

If you check the YAML of the namespace, you will see a `metadata` section with a `annotations` section. The `annotations` section contains a `openservicemesh.io/sidecar-injection` key with a value of `enabled`.


## Install an application

We can now install an application in the namespace we added to the mesh. In the `manifests` folder, run `k apply -k .`

List the pods in the namespace, each pod will contain 2 containers: the envoy proxy and the application. In READY, you should see 2/2:

```
NAME                        READY   STATUS    
debug                       2/2     Running
super-api-6db6c4448-sjc4z   2/2     Running
```

## Turning off permissive mode

Because permissive mode is on by default, the `debug` pod can talk to the `super-api` pod. You can verify this by getting a shell to the debug pod and executing `curl http://super-api-svc`.

Check permissive mode is on with:

```
kubectl get meshconfig osm-mesh-config -n kube-system -o jsonpath='{.spec.traffic.enablePermissiveTrafficPolicyMode}{"\n"}'
```


Let's turn it off:

```
kubectl patch meshconfig osm-mesh-config -n kube-system -p '{"spec":{"traffic":{"enablePermissiveTrafficPolicyMode":false}}}' --type=merge
```

If you now use the same curl command, you will get an empty reply. Let's fix this by adding a route group:

```yaml
apiVersion: specs.smi-spec.io/v1alpha4
kind: HTTPRouteGroup
metadata:
  name: superapi-routes
spec:
  matches:
  - name: all
    pathRegex: ".*"
    methods:
    - GET
```

This route group allows GET on all paths. We can now use this route group in a `TrafficTarget`:

```yaml
kind: TrafficTarget
apiVersion: access.smi-spec.io/v1alpha3
metadata:
  name: debug-access-superapi
  namespace: osm-test
spec:
  destination:
    kind: ServiceAccount
    name: super-api
    namespace: osm-test
  rules:
  - kind: HTTPRouteGroup
    name: superapi-routes
    matches:
    - all
  sources:
  - kind: ServiceAccount
    name: debug
    namespace: osm-test
```

Note that service accounts are used. The service accounts were deployed with kustomize and each pod uses its dedicated service account. Above, it is clear we allow acces from `debug` to `super-api` on all paths defined in the route group `superapi-routes`.

For more information about the traffic specs, see https://github.com/servicemeshinterface/smi-spec/tree/main/apis/traffic-specs.