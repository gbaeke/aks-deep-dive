# Canary

## Install Argo Rollouts

```bash
kubectl create namespace argo-rollouts
kubectl apply -n argo-rollouts -f https://github.com/argoproj/argo-rollouts/releases/latest/download/install.yaml
```

Install the `kubectl` plugin:

```bash
brew install argoproj/tap/kubectl-argo-rollouts
```
The plugin allows you to interact with Argo Rollouts with the `kubectl argo rollouts` command.

💡 Tip: if you do not use brew, do a manual install: https://argoproj.github.io/argo-rollouts/installation/#manual 

## Optional: install kubeview

Run the following commands:

```bash
git clone https://github.com/benc-uk/kubeview.git
cd kubeview/charts
helm install kubeview ./kubeview
```

## Deploy a rollout

⚠️ IMPORTANT: Argo Rollouts uses custom resource definitions; you need to make Kustomize aware of them by including a configuration as described here: https://argoproj.github.io/argo-rollouts/features/kustomize/

To deploy our sample rollout, run the following command from the `manifests` folder:

```bash
kubectl apply -k .
```

The above command creates the following resources:
- Rollout: rollout with a strategy set to `canary`
    - Rollout uses a ReplicaSet similary to a regular Kubernetes deployment
- Service: one service (contrasted with multiple services for Blue/Green)

In the Argo Rollouts UI, you will see Revision 1 as stable and receiving 100% of traffic. All steps are completed (6/6). This is expected as it is our initial rollout.

## Update the rollout

Modify the ConfigMap generator to update the WELCOME message and run `kubectl apply -k .` again.

The following happens (check the UI):
- Revision 1 is still marked as stable
- Revision 2 has been added as `canary`
- Traffic is sent to **all pods** in both the stable and canary; the number of pods of each ReplicaSet determine the traffic split based on round robin; the initial weight we set (10%) will be approximated. With a low number of pods, the canary will receive more traffic.
- The rollout is paused

To proceed with the rollout, you need to click `PROMOTE`. This will perform the remaining steps automatically because we set new weights and proceed after a few seconds until we reach the end. At the end of the rollout, the canary will receive 100% of traffic and be marked `stable`. During these steps, you will see the number of pods in both revisions change.

The end state is:
- Revision 1 is scaled down
- Revision 2 has two pods and is marked as stable

If you want to know more about canary deployments with SMI traffic split, click [this link](manifests-smi/README.md)

