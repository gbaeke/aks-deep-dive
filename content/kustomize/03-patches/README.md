# Patches

You might want to change the resources in your kustomization.yaml file. You can do this by adding patches to the `patches` section. A patch is a file that contains a series of commands that can be applied to a resource. There are two ways to add a patch:

- Strategic Merge Patch (SM)
- JSON Merge Patch (JM)

Although these types can be added to the `patches` section, you can also add them in a `patchesStrategicMerge` section, or `patchesJson6902` sections. These sections correspond to the types discussed above.

## patchStrategicMerge

With a strategic merge patch, you can add fields to a resource. Suppose you want to add a `resources` section to a pod specification that sets a memory limit. You would create a patch file that looks like this:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: go-template-load
spec:
  template:
    spec:
      containers:
      - name: go-template-load
        resources:
          limits:
            memory: "128Mi"
```

This `patch` only contains what you want to add to a resource. You also identify the resource by specifying the `apiVersion` and `kind` of the resource and the name of the resource.

To apply this patch to the resources listed in the `resources` section of your kustomization file, you would add the following section to your kustomization file:

```yaml
patchesStrategicMerge:
  - memory.yaml
```

There is no need to specify a target because the target is identified in the patch file. When you make patches like this, it is best to keep them small so they can easily be applied to multiple resources.

In some cases, a strategic merge patch does not work. For example, if you try to add a field to a resource that already has a field with the same name, the patch will fail. In that case, you can use a JSON merge patch instead.

## JSON Merge Patch

With a JSON Merge Patch, you specify an operation, a path, and a value. The operation can be `add`, `remove` or `replace` and the path is a string that identifies the field to be modified. The value is the value to be added, removed or replaced.

Suppose you want to set the number of replicas in a deployment to 3. You would create a patch file that looks like this:

```yaml
- op: replace
  path: /spec/replicas
  value: 3
```

In this case, the patch does not look like YAML manifest. It is also not clear what the target is. You can specify the target in your kustomization file like so:

```yaml
patchesJson6902:
  - target:
      kind: Deployment
      name: go-template-load
      version: v1
      group: apps
    path: patch.yaml
```

In the above example, the patch containing the op, path and value fields is in `patch.yaml`. The target is a deployment called `go-template-load`.

## Patches

