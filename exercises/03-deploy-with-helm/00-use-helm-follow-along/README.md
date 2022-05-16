# Helm initial follow along

## Adding the super-api repository

There is a super-api repository on the web. Go to https://gbaeke.github.io/helm-chart/ to check.

Add the repo and verify it was added:

```bash
helm repo add super-api https://gbaeke.github.io/helm-chart/

helm repo list
```

Search **your** repositories for the super-api chart:

```bash
helm search repo super-api

NAME                    CHART VERSION   APP VERSION     DESCRIPTION
super-api/super-api     1.0.0           1.0.3           A Helm chart for super-api
```

The above result shows the following:
- there is a chart called super-api/super-api where the first part is the repo and the second part is the chart name.
- the chart version is 1.0.0: you control the chart version in a file called `chart.yaml`
- the app version is 1.0.3: this should be the version of super-api that the chart deploys by default

## Install super-api on your cluster

Install the chart in a a namespace called `super-api`:

```bash
helm upgrade --install super-api super-api/super-api --namespace super-api --create-namespace
```

⚠️ Although we install the chart, we use the upgrade command with the --install flag. If you install the chart the first time, it will just install it instead of upgrading it.

Chech that the chart is installed:

```bash
helm list --namespace super-api

NAME            NAMESPACE       REVISION        UPDATED                                         STATUS          CHART           APP VERSION
super-api       super-api       1               2022-05-12 15:33:52.936173842 +0200 CEST        deployed        super-api-1.0.0 1.0.3
```

Helm list shows a list of all the charts that are installed in the namespace. Use `--all-namespaces` to see all the charts in all the namespaces.

Check the pods:

```bash
kubectl get pods --namespace super-api

NAME                      READY   STATUS    RESTARTS   AGE
super-api-d4d77bd-mb7t8   1/1     Running   0          2m25s
```

# Upgrade the chart

Let's install version 1.0.7 of the super-api application.

```bash
helm upgrade --install super-api super-api/super-api --namespace super-api --set image.tag=1.0.7
```

Instead of `--set` you can use a values file:

```bash
helm upgrade --install super-api super-api/super-api --namespace super-api --values myvalues.yaml
```

## Get information about the release

Use `helm get` to get information about the release:

```bash
helm get all super-api -n super-api
helm get manifest super-api -n super-api
helm get values super-api -n super-api
helm get values super-api -n super-api --revision 1
```

The first three commands obtain information about the last release. The fourth command gets the values of the first release. Because we did not provide extra values, it returns **null**.

To see revisions, just run `helm history super-api -n super-api`.

The revision information is stored in secrets of type `helm.sh/release.v1`

## Roll back to a previous release

To roll back to the first release:

```bash
helm rollback super-api 1 -n super-api 
```

If you run `helm history super-api -n super-api` you will see the following:

```
REVISION        UPDATED                         STATUS          CHART           APP VERSION     DESCRIPTION
1               Thu May 12 15:33:52 2022        superseded      super-api-1.0.0 1.0.3           Install complete
2               Thu May 12 15:40:15 2022        superseded      super-api-1.0.0 1.0.3           Upgrade complete
3               Thu May 12 17:27:00 2022        deployed        super-api-1.0.0 1.0.3           Rollback to 1
```

## Other useful commands

```

# download the chart as a .tgz file
helm pull super-api/super-api 

# use --untar with either helm to also extract the chart
helm pull super-api/super-api --untar

# run helm lint on the extracted chart
helm lint super-api

```
