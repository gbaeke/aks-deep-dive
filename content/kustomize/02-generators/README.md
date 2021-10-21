# Generators

Generators in Kustomize are used to generate new resources. Two types of generators are supported:
- ConfigMaps
- Secrets

When you create a ConfigMap or Secret with `kubectl`, you can use literals or files. Similarly, Kustomize supports literals and files for generators. In addition, Kustomize supports environment files (typically a .env file). An example of an environment file is shown below:

```
SOMEKEY=somevalue
OTHERKEY=othervalue
```

## Generating ConfigMaps

The Kustomization snippet below generates a ConfigMap:

```yaml
configMapGenerator:
- name: superapi-config
  files:
    - config.toml
  literals:
    - WELCOME=Hello
    - PORT=8080
  envs:
    - myenvfile.env
  options:
    annotations:
      note: api config
    labels:
      type: generated
    disableNameSuffixHash: true
```

The name of the ConfigMap will be `superapi-config` but it might be changed with a suffix or prefix. It adds the contents of the file `config.toml` to the ConfigMap, in addition to two literals `WELCOME` and `PORT`. Via `envs:` the variables inside the `myenvfile.env` are added as well.

In the example above, we set `options` to add an annotation and a label. We also turn off the name suffix hash although you would usually leave this on.

Note that the key of the file contents data will be the name of the file. That can be changed by adding the key in front of the file name.

## Generating Secrets

Secrets are generated similarly to ConfigMaps. The example below generates a Secret with a literal and a file:

```YAML
secretGenerator:
- name: superapi-secret
  files:
    - secret.txt
  literals:
    - SECRETKEY=secret value
  type: Opaque
```

Because there are multiple types of secrets in Kubernetes, you can specify the type of the secret with the `type:` option. The default type is `Opaque`. To create a TLS secret, you can use the `kubernetes.io/tls` type. The example below creates a TLS secret:

```yaml
secretGenerator:
- name: app-tls
  files:
  - secret/tls.cert
  - secret/tls.key
  type: "kubernetes.io/tls"
```


