# Service Accounts

Create a service account called `sa-demo` in the `default` namespace.

```bash
kubectl create serviceaccount sa-demo --namespace=default
# or
kubectl create sa sa-demo --namespace=default
# or
kubectl create sa sa-demo --namespace=default --dry-run -o yaml | kubectl apply -f -
```

Look at the YAML of the service account:

```bash
kubectl get sa sa-demo -o yaml
```

Notice that the service account references a secret called `sa-demo-token-<hash>`.

## Investigate the secret

Look at the YAML of the secret:

```bash
kubectl get secret sa-demo-token-<hash> -o yaml
```

The secret contains three pieces of data:
- `token`: the token for the service account
- `ca.crt`: the CA certificate for the cluster
- `namespace`: the namespace of the service account

You can copy and paste the token in https://jwt.io to decode it. The token is base64 encoded. To extract the token from the secret, you can use the following command:

```bash
kubectl get secret sa-demo-token-<hash> -o jsonpath='{.data.token}' | base64 -d
```

The decoded payload in the token is a JSON object:

```json
{
  "iss": "kubernetes/serviceaccount",
  "kubernetes.io/serviceaccount/namespace": "default",
  "kubernetes.io/serviceaccount/secret.name": "sa-demo-token-d4htg",
  "kubernetes.io/serviceaccount/service-account.name": "sa-demo",
  "kubernetes.io/serviceaccount/service-account.uid": "0be00f04-964d-4a84-a62e-e262175c9e10",
  "sub": "system:serviceaccount:default:sa-demo"
}
```

## Use the token in a pod

Create an nginx deployment with `kubectl create`:
    
```bash
kubectl create deploy nginx --image=nginx
```

Patch the deployment to use a service account:

```bash
kubectl patch deploy nginx -p '{"spec":{"template":{"spec":{"serviceAccount":"sa-demo"}}}}'
```

Check the YAML of the deployment:

```bash
kubectl get deploy nginx -o yaml
```

The pod spec should contain the service account.

## Exec into the pod

Save the pod name used by the deployment in an environment variable and get a shell into the pod:

```bash
export POD_NAME=$(kubectl get pods -l "app=nginx" -o jsonpath="{.items[0].metadata.name}")
kubectl exec -it $POD_NAME -- sh
```

Inside the pod, use the following commands:

```bash
cd /var/run/secrets/kubernetes.io/serviceaccount
ls # you will see the secrets
cat token # you will see the token (base64 decoded)
cat ca.crt # you will see the CA certificate
cat namespace # you will see the namespace
```

Now use curl to authenticate to the Kubernetes API with the bearer token, use the ca.crt to trust the certificate and get a list of pods:

```bash
curl -H "Authorization: Bearer $(cat token)" --cacert ca.crt https://kubernetes/api/v1/namespaces/default/pods
```

⚠️ Instead of using the --cacert option, you can use --insecure to skip the certificate check.

## Grant access rights

Create a role to that can list pods (not in the pod shell, open another terminal):

```bash
kubectl create role pod-reader --verb=list --resource=pods
```

Create a role binding to the role and the service account:

```bash
kubectl create rolebinding pod-reader --role=pod-reader --serviceaccount=default:sa-demo
```




