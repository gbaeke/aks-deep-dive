# Init containers

## simple-init.yaml

This is a simple example of init containers. Multiple init containers run before the main nginx container is started. The second init container has a non-zero exit code. It will be restarted until it succeeds and the init container will go in **CrashLoopBackOff** state.

A tool like k9s will clearly show this behavior.

When you set the `RestartPolicy` to `Never`, this behavior is not observed.

## wait-for-service.yaml

Example of waiting for a service to be available. You can create the service with:

``` 
k create service clusterip myservice --tcp=8080
```

## init-volume.yaml

Example of using an init container to clone a git repo to an in-memory volume. The nginx container uses the volume to serve the git repo.