# Create a chart follow along

## Create a chart manually

We do not use `helm create` but manually create the necessary files.

- Create an empty folder `mychart` and make it current
- Create a `templates` folder (do not make it current)
- Create a file called `Chart.yaml` with the following contents:

```yaml
apiVersion: v2
name: superapi
description: A Helm chart to install superapi

# optional
kubeVersion: ">=1.20"

type: application
version: 1.0.0
# best practice to quote appVersion; helm create does this automatically
appVersion: "1.0.7"
```

- Create a file called `values.yaml` with the following contents:

```yaml
replicaCount: 1

image:
  repository: ghcr.io/gbaeke/super
  pullPolicy: IfNotPresent
  tag: ""
```

⚠️ a values.yaml file is optional.

## Add templates

Add `deployment.yaml` and `service.yaml` to the `templates` folder. You can find the files in the folder of this README.

From the `mychart` folder, run `helm template .`. The output is a YAML file comprised of the deployment and the service. However, we are not taking advantage of Helm's templating functionality.

## Retrieve the image name and tag from values

In `deployment.yaml` replace the value of `image:` with `"{{.Values.image.repository }}:{{ .Values.image.tag | default .Chart.AppVersion }}"`. This does the following:

- retrieve the value of `image.repository` from the `values.yaml` file
- retrieve the value of `image.tag` from the `values.yaml` file but if it is not set, use the value of `Chart.AppVersion` from the `Chart.yaml` file
- the repository and tag are concatenated with a colon

⚠️ You do not need to have those values in values.yaml. In that case, you need to supply the values at deployment time with `--set` or `--values`.

Run `helm template .` again. The image should be set based on the values in values.yaml.

## Add resource limits & requests via parameters

In values.yaml, add the following:

```yaml
resources:
  limits:
    cpu: "20m"
    memory: "55M"
```

In `templates/deployment.yaml`, remove the everything under resources and add a template so that it looks like below:

```yaml
- image:  "{{.Values.image.repository }}:{{ .Values.image.tag | default .Chart.AppVersion }}"
    imagePullPolicy: Always
    name:  superapi
    resources: 
        {{- toYaml .Values.resources | nindent 12 }}          
    livenessProbe: ...
```	

Adding a block of YAML is very common. The data in the . (dot) object is not yaml so it needs to be converted with the `toYaml` function. The are other `to` funtions like `toJson`. The `-` after `{{` tells Helm to remove all whitespace. The toYaml function converts the entire contents of `.Values.resources` to YAML and then indents it by 12 spaces. It starts with a newline.

If you use `indent` instead of `nindent`, you will get an error when you run `helm template .`. Use the `--debug` parameter to see the output.

If you do not want to add resources, just add {} after `resources:` in `values.yaml` and add line comments to the values below `resources:`.

## Add a ConfigMap

Add `configmap.yaml` to the `templates` folder.

Add the following to values.yaml:

```yaml
config:
  enabled: true
  welcome: "Welcome to Super API v2"
```

We want to enable or disable the ConfigMap entirely and set the welcome message. An environment variable in the container of the deployment uses the ConfigMap value.

In `templates/configmap.yaml` make the following changes:

```yaml
{{- if .Values.config.enabled -}}
kind: ConfigMap
apiVersion: v1
metadata:
  name: superapi-config
  namespace: default
data:
  welcome: {{ .Values.config.welcome | upper | quote }} # Welcome message
{{- end -}}
```

Helm supports `if` statements. The ConfigMap will only be part of Helm's YAML output if the `enabled` value is true. The value of the `welcome` key is set to the value of the `welcome` key in the `config` object. The value is converted to uppercase and quoted with "" (double quotes).

If you now run `helm template .` the ConfigMap will be included in the YAML output.

To use the ConfigMap in the deployment, add the following to `env:` of the container spec:

```yaml
env:
    {{- if .Values.config.enabled }}
    - name:  WELCOME
        valueFrom:
        configMapKeyRef:
            name: superapi-config
            key: welcome
    {{- end }}
    - name: PORT
        value: "8080" 
```

The `WELCOME` environment variable is only included if the `config.enabled` value is true. The `PORT` environment variable is always included. Not that we do not remove whitespace at the end of of if and end.

## Making the pods restart when the contents of the ConfigMap changes

When you flip `config.enabled` to true or false, the `env` list is changed. That changes the pod template which triggers a rolling update of the deployment.

However, when `config.enabled` is true, the pod template does not change when the `config.welcome` changes. That also means that the pods are not restarted and the new value is not picked up.

With `kustomize`, a ConfigMapGenerator's default behaviour is to add a hash to the name of the ConfigMap. The reference in the pod template is also updated, which triggers a rolling update of the deployment.

To trigger a rolling update with Helm, you can add an annotation to the pod template like so:

```yaml
annotations:
    confighash: {{ toString .Values.config | sha256sum  }}
```

The above annotation should be added to the pod template of the deployment. When the value of .Values.config changes, the hash will be different, and the pod(s) will be restarted because the annotations are part of the pod template.

You can try this with: `helm upgrade --install . --set config.welcome=$RANDOM` and run this multiple times. Each time, the pods will be recreated.

⚠️ Helm 2 had a `--recreate-pods` flag but that was removed in Helm 3.