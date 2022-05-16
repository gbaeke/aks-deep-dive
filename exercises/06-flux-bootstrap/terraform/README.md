# Deploy with Terraform

```
terraform plan -var 'github_owner=OWNER' -var 'github_token=TOKEN'

terraform apply -var 'github_owner=OWNER' -var 'github_token=TOKEN'
```

This creates a private repo `flux-with-tf` in your GitHub account. There will be a folder `clu-00` in the repo with a folder `flux-system`. A git source and kustomization will be added as well.

To destroy this, run:

```
terraform destroy -var 'github_owner=OWNER' -var 'github_token=TOKEN'
```

Potential issues:
- Kustomization might not be deleted because of `finalizer`; use `kubectl edit` to remove the finalize
- Repository might not be deleted because of missing access on the token (remove manually)