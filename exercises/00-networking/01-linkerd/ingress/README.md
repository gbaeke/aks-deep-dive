# Ingress and Service Mesh

## Install an ingress controller

Linkerd does not come with an ingress controller. This gives you the freedom to use any ingess controller you like.

Let's install `nginx ingress`

```
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.0.4/deploy/static/provider/cloud/deploy.yaml
```

Or with Helm:

```
helm upgrade --install ingress-nginx ingress-nginx \
  --repo https://kubernetes.github.io/ingress-nginx \
  --namespace ingress-nginx --create-namespace
```

## Meshing the Ingress Controller

Add the following annotation to the Ingress Controller pods:

```yaml
annotations:
  linkerd.io/inject: enabled
```

In `ingress` resources, add the annotation below:

```yaml
metadata:
  name: <INGRESSNAME>
  namespace: <NAMESPACE>
  annotations:
    nginx.ingress.kubernetes.io/service-upstream: "true"
```

Normally, NGINX ingress controller uses a list of endpoints of the target service to route traffic to. It does not use the IP ove the service. With the `nginx.ingress.kubernetes.io/service-upstream: "true"` annotation, NGINX will use the Cluster IP and port of the target service.

To install a meshed NGINX Ingress Controller, add the annotations to a values.yaml file:

```yaml
controller:
  podAnnotations:
    linkerd.io/inject: enabled
```

Run the following command:

```
helm upgrade --install ingress-nginx ingress-nginx \
  --repo https://kubernetes.github.io/ingress-nginx \
  --namespace ingress-nginx --create-namespace \
  --values values.yaml
```

Deploy the Linkerd sample app from 01-linkerd/manifests. Also add `ingress.yaml` but modify it with the `nginx.ingress.kubernetes.io/service-upstream: "true"` annotation.

A result of adding `nginx.ingress.kubernetes.io/service-upstream: "true"` is that Linkerd can use its own load balancing algorithm based on latency. A drawback is that sticky sessions do not work. If you require sticky sessions, you should remove the annotation to allow NGINX to route traffic to endpoints of the service based on the stick session cookie.