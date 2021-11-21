# Creating a Helm chart

## Exercise

Create a Helm chart that installs `ghcr.io/gbaeke/super:1.0.2` and add the following:
- ConfigMap with the contents of a `config.toml` file. Contents of the file is shown below:

```
WELCOME=Hello from Helm chart!
LOG=TRUE
```

- The ConfigMap content should be /config.toml in the `superapi` containers
- Service with a type that is configurable in values.yaml or a parameter (80 --> 8080 on the pods)
- Ingress only if enabled (nginx)
- Configurable replicas and resource limits
- Pods should have the linkerd sidecar

## High level steps

### Create a chart from a template

- Create an empty folder and make it current
- Use `helm create <chartname>`; this will create a folder with name `<chartname>`
- Modify `Chart.yaml` and update the following fields:
    - description
    - chart version (or leave as is)
    - appVersion (version of the application e.g., 1.0.2)
- In templates, remove what is not needed:
    - hpa.yaml: we will not need HPA
    - serviceaccount.yaml: we will not create a new service account
- Update values.yaml
    - set default and remove what is not needed
- Update deployment.yaml
    - modify port
    - remove what is not needed
- Remove the tests folder
- Modify NOTES.txt as you see fit
- **Optional:** add a chart dependency for nginx and use values.yaml to create a PodDisruptionBudget for the Nginx deployment
- **Optional:** add a post install hook that does not get deleted after the hook is run

To check the result of your chart:

```
helm template .
```

Because this is not an actual release, you will see RELEASE-NAME as a placeholder.

Perform a dry-run:

```
helm install superapi . --dry-run
```

Instead of RELEASE-NAME, you will see `superapi`. The beginning of the output includes:

```
NAME: superapi
LAST DEPLOYED: Fri Nov 19 12:59:05 2021
NAMESPACE: default
STATUS: pending-install
REVISION: 1
TEST SUITE: None
HOOKS:
MANIFEST:
```

Near the end, the `notes.txt` is rendered:

```
NOTES:
1. Get the application URL by running these commands:
  http://chart-example.local/
```

Deploy your chart to the default namespace. Check that nginx is installed as well. Is there a PodDisruptionBudget?