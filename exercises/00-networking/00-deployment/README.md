# Deploy sample workload

This workload uses an image in ACR: crazk8skjfsa6ufncm6ehkyi.azurecr.io/super:1.0.3

To import the image to your ACR, use:

```
az acr import \
  --name yourACR \
  --source ghcr.io/gbaeke/super:1.0.3 \
  --image super:1.0.3
```

After import, update `deployment.yaml` in the `manifests` folder with your ACR name.