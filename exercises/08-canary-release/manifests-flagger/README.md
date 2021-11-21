# Canary with Flagger

## Install Flagger for with Linkerd

```
helm repo add flagger https://flagger.app
kubectl apply -f https://raw.githubusercontent.com/fluxcd/flagger/main/artifacts/flagger/crd.yaml
helm upgrade -i flagger flagger/flagger \
--namespace=linkerd \
--set crd.create=false \
--set meshProvider=linkerd \
--set metricsServer=http://prometheus.linkerd-viz:9090
```

## Bootstrap

We will use the `podinfo` deployment as an example. Run these commands:

```
kubectl create ns test
kubectl annotate namespace test linkerd.io/inject=enabled
```

The above creates a test namespace and makes sure all pods in the namespace get the linkerd proxy.

Install the load testing service:

```
kubectl apply -k https://github.com/fluxcd/flagger/kustomize/tester?ref=main
```

The above installs the following in namespace `test`:
- deployment: deployment for ghcr.io/fluxcd/flagger-loadtester:0.18.0
- service: service `flagger-loadtester` on port 80

Now run:

```
kubectl apply -k https://github.com/fluxcd/flagger//kustomize/podinfo?ref=main
```

The above creates the following in namespace test:
- deployment: deployment for podinfo
- hpa: horizontal pod autoscaler for podinfo to scale between 2 and 4 pods based on CPU usage

Now we can create a `Canary` resource. It is important to note that `flagger` does not use a replacement for a `deployment`. It works with regular deployments or DaemonSets. Here is the canary resource:

```yaml
apiVersion: flagger.app/v1beta1
kind: Canary
metadata:
  name: podinfo
  namespace: test
spec:
  # deployment reference
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: podinfo
  # HPA reference (optional)
  autoscalerRef:
    apiVersion: autoscaling/v2beta2
    kind: HorizontalPodAutoscaler
    name: podinfo
  # the maximum time in seconds for the canary deployment
  # to make progress before it is rollback (default 600s)
  progressDeadlineSeconds: 60
  service:
    # ClusterIP port number
    port: 9898
    # container port number or name (optional)
    targetPort: 9898
  analysis:
    # schedule interval (default 60s)
    interval: 30s
    # max number of failed metric checks before rollback
    threshold: 5
    # max traffic percentage routed to canary
    # percentage (0-100)
    maxWeight: 50
    # canary increment step
    # percentage (0-100)
    stepWeight: 5
    # Linkerd Prometheus checks
    metrics:
    - name: request-success-rate
      # minimum req success rate (non 5xx responses)
      # percentage (0-100)
      thresholdRange:
        min: 99
      interval: 1m
    - name: request-duration
      # maximum req duration P99
      # milliseconds
      thresholdRange:
        max: 500
      interval: 30s
    # testing (optional)
    webhooks:
      - name: acceptance-test
        type: pre-rollout
        url: http://flagger-loadtester.test/
        timeout: 30s
        metadata:
          type: bash
          cmd: "curl -sd 'test' http://podinfo-canary.test:9898/token | grep token"
      - name: load-test
        type: rollout
        url: http://flagger-loadtester.test/
        metadata:
          cmd: "hey -z 2m -q 10 -c 2 http://podinfo-canary.test:9898/"
```

Remarks:
- the manifest references the `deployment` and the `hpa` (hpa is not required)
  - ⚠️ when you use an HPA for your deployment, do add the hpa section because Flagger will create a new deployment and hpa with a -primary suffix
- progressDeadlineSeconds is set to 60s: if canary does not make progress in that time, it is rolled back
- service: flagger will create services for you
- analysis:
    - every 30s
    - max number of failed metrics = 5 (otherwise rollback)
    - max traffic to canary = 50%
    - increase weight by 5%
    - use Linkerd metrics --> these are baked in to Flagger; no need to create queries
        - request-success-rate is used here and should be minimum 99% over 1 minute
        - request-duration is used as well
- optional test with a webhook

Apply the canary yaml:

```
kubectl apply -f podinfo-canary.yaml
```

When you apply the above manifest, nothing in particular happens. When you describe the `Canary` you will see some events:
- all metrics providers are available
- initialization done podinfo.test (test is the namespace)

In the deployment, podinfo uses the following image: `stefanprodan/podinfo:3.1.0`. We will change this later to 3.1.1. Before that, check the services that Flagger created:
- podinfo: selector `app=podinfo-primary` (with active pods)
- podinfo-canary: selector `app=podinfo` (but there are no such pods)
- podinfo-primary: selector `app=podinfo-primary` (same as podinfo service)

Note that flagger also manipulates the deployment:
- podinfo deployment: as in deployment spec but is scaled to 0
- podinfo-primary: created by podinfo; the pods of this deployment are routed to by the `podinfo` and `podinfi-primary` services

When we update the image of the deployment, we will see several changes. Let's first change the image to 3.1.1:

```
kubectl -n test set image deployment/podinfo podinfod=stefanprodan/podinfo:3.1.1
```

Flagger will detect this change and do several things:
- scales up the podinfo deployment (was 0 before)
- runs the pre-rollout test before routing traffic to the canary (there is no sense in progressing if this test fails; the service `podinfo-canary.test` is used
- starts routing traffic to the canary by manipulating the TrafficSplit object it creates; Flagger was configured to 5% increments up to 50%
- Flagger sets the weights and uses the configured analyis to decide to go higher
- When you describe the `Canary` you will see the following events:
    - Starting canary analysis for podinfo.test
    - Pre-rollout check acceptance-test passed
    - Advance podinfo.test canary weight 5
    - Advance podinfo.test canary weight 10
    - ...
    - Promotion completed!

When promotion is completed, the pods of podinfo-primary use the 3.1.1 image.

Monitor canaries with:

```
watch kubectl get canaries --all-namespaces
```


