# Argo CD Exercise

Steps in this exercise:
- create a git repo with the application to deploy and copy files
- create a new application in Argo CD and view its details
- make a change in the git repo; this will trigger a blue-green deployment (the app you will uses, uses Argo Rollouts with blue-green)


## Create a git repository

Using your own GitHub account, create an empty git repository. Copy the files from `exercises/04-blue-green-release/manifests` into the `manifests` folder in the repository.

⚠️ **IMPORTANT:** this exercise requires the installation of Argo Rollouts.

Update `kustomization.yaml` as you see fit. You can update the WELCOME message to v1 for instance.

## Create an application in Argo CD

Use the repo created above as the source and set the appropriate folder.

You can use the `argocd` CLI if you want. Hint:

```
argocd app create APPNAME --repo REPO --path PATH --dest-server DEST --dest-namespace NS
```

When you use the CLI as above, the app uses manual sync. You can use the CLI to sync:

```
argocd app sync APPNAME
```

Because this app uses Argo Rollouts, you can use the Argo Rollouts UI as well:

```
kubectl argo rollouts dashboard -n NS
```

In the Argo CD UI, you can click the `three dots` on the `rollout` object. It will reveal options such as `promote` and `resume`. On the rollout itself, you can also see the revision number.

## Make a change in the git repo

In `kustomization.yaml`, make a change to the `WELCOME` literal, in the `configMapGenerator`. E.g., `Hello from v2!` and commit this change.

Use the refresh option in the Argo CD UI. The app should be out of sync. In the UI, you see yellow icons that indicate what will change. One of the objects that will change is the rollout object.

Use the `APP DIFF` button to see the differences.

Synchronize the app.

The rollout will show that it is at `rev:2` but the revision is not active yet. Click the three dots on the rollout. There is a `resume` option to resume the paused rollout. Use that option to make revision 2 fully active. The replicaSet of revision 1 will be scaled down.

⚠️ **IMPORTANT:** the app will not be fully synced unless you synch with pruning to remove the old configmap; when you do so, that will prevent you from doing an blue-green rollback because it will want to use that configmap


