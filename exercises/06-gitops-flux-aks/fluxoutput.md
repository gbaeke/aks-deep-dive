```json
{
  "bucket": null,
  "complianceState": "Non-Compliant",
  "configurationProtectedSettings": {},
  "errorMessage": "",
  "gitRepository": {
    "httpsCaCert": null,
    "httpsUser": null,
    "localAuthRef": null,
    "repositoryRef": {
      "branch": "main",
      "commit": null,
      "semver": null,
      "tag": null
    },
    "sshKnownHosts": null,
    "syncIntervalInSeconds": 600,
    "timeoutInSeconds": 600,
    "url": "https://github.com/Azure/gitops-flux2-kustomize-helm-mt"
  },
  "id": "/subscriptions/cb0b66f7-22e3-4114-9c4a-c7f52cf80791/resourceGroups/lab-user-00-rg/providers/Microsoft.ContainerService/managedClusters/clu-00/providers/Microsoft.KubernetesConfiguration/fluxConfigurations/cluster-config",
  "kustomizations": {
    "apps": {
      "dependsOn": [
        "infra"
      ],
      "force": false,
      "name": "apps",
      "path": "./apps/staging",
      "prune": true,
      "retryIntervalInSeconds": null,
      "syncIntervalInSeconds": 600,
      "timeoutInSeconds": 600
    },
    "infra": {
      "dependsOn": null,
      "force": false,
      "name": "infra",
      "path": "./infrastructure",
      "prune": true,
      "retryIntervalInSeconds": null,
      "syncIntervalInSeconds": 600,
      "timeoutInSeconds": 600
    }
  },
  "name": "cluster-config",
  "namespace": "cluster-config",
  "provisioningState": "Succeeded",
  "repositoryPublicKey": "",
  "resourceGroup": "lab-user-00-rg",
  "scope": "cluster",
  "sourceKind": "GitRepository",
  "sourceSyncedCommitId": "main/c4e327286379495f8b6edc2c9c208095b6cc53ab",
  "sourceUpdatedAt": "2022-05-13T11:54:42+00:00",
  "statusUpdatedAt": "2022-05-13T11:54:54.830000+00:00",
  "statuses": [
    {
      "appliedBy": null,
      "complianceState": "Compliant",
      "helmReleaseProperties": null,
      "kind": "GitRepository",
      "name": "cluster-config",
      "namespace": "cluster-config",
      "statusConditions": [
        {
          "lastTransitionTime": "2022-05-13T11:54:42+00:00",
          "message": "stored artifact for revision 'main/c4e327286379495f8b6edc2c9c208095b6cc53ab'",
          "reason": "Succeeded",
          "status": "True",
          "type": "Ready"
        },
        {
          "lastTransitionTime": "2022-05-13T11:54:42+00:00",
          "message": "stored artifact for revision 'main/c4e327286379495f8b6edc2c9c208095b6cc53ab'",
          "reason": "Succeeded",
          "status": "True",
          "type": "ArtifactInStorage"
        }
      ]
    },
    {
      "appliedBy": null,
      "complianceState": "Compliant",
      "helmReleaseProperties": null,
      "kind": "Kustomization",
      "name": "cluster-config-infra",
      "namespace": "cluster-config",
      "statusConditions": [
        {
          "lastTransitionTime": "2022-05-13T11:54:44+00:00",
          "message": "Applied revision: main/c4e327286379495f8b6edc2c9c208095b6cc53ab",
          "reason": "ReconciliationSucceeded",
          "status": "True",
          "type": "Ready"
        }
      ]
    },
    {
      "appliedBy": {
        "name": "cluster-config-infra",
        "namespace": "cluster-config"
      },
      "complianceState": "Compliant",
      "helmReleaseProperties": null,
      "kind": "HelmRepository",
      "name": "bitnami",
      "namespace": "cluster-config",
      "statusConditions": [
        {
          "lastTransitionTime": "2022-05-13T11:54:48+00:00",
          "message": "stored artifact for revision 'a04b873a125ad86005cec4b9ce99b2dad8de9ddcb0e5f896a0bad9c3598018b2'",
          "reason": "Succeeded",
          "status": "True",
          "type": "Ready"
        },
        {
          "lastTransitionTime": "2022-05-13T11:54:48+00:00",
          "message": "stored artifact for revision 'a04b873a125ad86005cec4b9ce99b2dad8de9ddcb0e5f896a0bad9c3598018b2'",
          "reason": "Succeeded",
          "status": "True",
          "type": "ArtifactInStorage"
        }
      ]
    },
    {
      "appliedBy": {
        "name": "cluster-config-infra",
        "namespace": "cluster-config"
      },
      "complianceState": "Compliant",
      "helmReleaseProperties": null,
      "kind": "HelmRepository",
      "name": "podinfo",
      "namespace": "cluster-config",
      "statusConditions": [
        {
          "lastTransitionTime": "2022-05-13T11:54:45+00:00",
          "message": "stored artifact for revision 'debd9e30ecc98721b7aa3404eb64db4032786e0572be4629359aa7b6cf0f5fe7'",
          "reason": "Succeeded",
          "status": "True",
          "type": "Ready"
        },
        {
          "lastTransitionTime": "2022-05-13T11:54:45+00:00",
          "message": "stored artifact for revision 'debd9e30ecc98721b7aa3404eb64db4032786e0572be4629359aa7b6cf0f5fe7'",
          "reason": "Succeeded",
          "status": "True",
          "type": "ArtifactInStorage"
        }
      ]
    },
    {
      "appliedBy": {
        "name": "cluster-config-infra",
        "namespace": "cluster-config"
      },
      "complianceState": "Pending",
      "helmReleaseProperties": {
        "failureCount": 0,
        "helmChartRef": {
          "name": "cluster-config-nginx",
          "namespace": "cluster-config"
        },
        "installFailureCount": 0,
        "lastRevisionApplied": 0,
        "upgradeFailureCount": 0
      },
      "kind": "HelmRelease",
      "name": "nginx",
      "namespace": "cluster-config",
      "statusConditions": [
        {
          "lastTransitionTime": "2022-05-13T11:54:52+00:00",
          "message": "Reconciliation in progress",
          "reason": "Progressing",
          "status": "Unknown",
          "type": "Ready"
        }
      ]
    },
    {
      "appliedBy": {
        "name": "cluster-config-infra",
        "namespace": "cluster-config"
      },
      "complianceState": "Pending",
      "helmReleaseProperties": {
        "failureCount": 0,
        "helmChartRef": {
          "name": "cluster-config-redis",
          "namespace": "cluster-config"
        },
        "installFailureCount": 0,
        "lastRevisionApplied": 0,
        "upgradeFailureCount": 0
      },
      "kind": "HelmRelease",
      "name": "redis",
      "namespace": "cluster-config",
      "statusConditions": [
        {
          "lastTransitionTime": "2022-05-13T11:54:53+00:00",
          "message": "Reconciliation in progress",
          "reason": "Progressing",
          "status": "Unknown",
          "type": "Ready"
        }
      ]
    },
    {
      "appliedBy": {
        "name": "cluster-config-infra",
        "namespace": "cluster-config"
      },
      "complianceState": "Compliant",
      "helmReleaseProperties": null,
      "kind": "HelmChart",
      "name": "test-chart",
      "namespace": "cluster-config",
      "statusConditions": [
        {
          "lastTransitionTime": "2022-05-13T11:54:52+00:00",
          "message": "pulled 'redis' chart with version '11.3.4'",
          "reason": "ChartPullSucceeded",
          "status": "True",
          "type": "Ready"
        },
        {
          "lastTransitionTime": "2022-05-13T11:54:52+00:00",
          "message": "pulled 'redis' chart with version '11.3.4'",
          "reason": "ChartPullSucceeded",
          "status": "True",
          "type": "ArtifactInStorage"
        }
      ]
    },
    {
      "appliedBy": null,
      "complianceState": "Non-Compliant",
      "helmReleaseProperties": null,
      "kind": "Kustomization",
      "name": "cluster-config-apps",
      "namespace": "cluster-config",
      "statusConditions": [
        {
          "lastTransitionTime": "2022-05-13T11:54:41+00:00",
          "message": "dependency 'cluster-config/cluster-config-infra' is not ready",
          "reason": "DependencyNotReady",
          "status": "False",
          "type": "Ready"
        }
      ]
    }
  ],
  "suspend": false,
  "systemData": {
    "createdAt": "2022-05-13T11:54:32.244962+00:00",
    "createdBy": null,
    "createdByType": null,
    "lastModifiedAt": "2022-05-13T11:54:32.244962+00:00",
    "lastModifiedBy": null,
    "lastModifiedByType": null
  },
  "type": "Microsoft.KubernetesConfiguration/fluxConfigurations"
}
```