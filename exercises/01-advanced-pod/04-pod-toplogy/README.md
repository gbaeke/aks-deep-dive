# Pod topology

The main topic here is `topologySpreadConstraints`, a way to specify how pods should be spread across topologies. A topology is a set of nodes that are grouped together for the purpose of scheduling, identified by a label on the node.

But first, let's look at other ways to schedule pods.

## nodeSelector

Simply add `nodeSelector` to the pod spec and specify the label on the node you want to schedule the pod on.

See `nodeSelector.yaml`

You can use any label. In a lot of cases, the well-know labels are used. See https://kubernetes.io/docs/reference/labels-annotations-taints/.

## Node affinity

In concept, node affinity is similar to nodeSelector. However, there are two types of node affinity:
- `preferred`: scheduler will try to enforce affinity but will not guarantee it
- `required`: the pod needs to be scheduled on a node that matches the node affinity; this is similar to how nodeSelector works

See 'node-ffinity.yaml' which also uses `matchExpressions`

Notes:
- if you use `nodeSelector` AND `node affinity` then both must be satisfied
- if you use multiple `matchExpressions` then all of them must be satisfied
- if you use multiple `nodeSelector` terms, pods are scheduled when one of them can be satisfied

The pod will **NOT** be removed when you modify the labels of the node.

## Inter-pod affinity and anti-affinity

Schedule pods (or not) based on labels of pods that are **already running** on the node.

See example `pod-anti.yaml` that tries to schedule three pods. The pods should not run in the same topology, which in this case is the node. In the example, three pods are created. If there are only two nodes, one of the pods will stay pending with the following event:

```
1 node(s) had taint {virtual-kubelet.io/provider: azure}, that the pod didn't tolerate, 2 node(s) didn't match pod affinity/anti-affinity, 2 node(s) didn't match pod anti-affinity rules.
```

Note that the message will vary depending on the cluster. This cluster also uses virtual nodes with that node having a taint. The pod does not tolerate that taint so it cannot be scheduled.
