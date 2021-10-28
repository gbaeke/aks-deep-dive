# Excercises

Exercises have the 👉 in front of the link.

## Service Mesh

👉 [Implementing a Service Mesh with Linkerd](00-service-mesh/README.md)

Requirements:
- need to install the Linkerd CLI

## DAPR

👉 [Service Invocation](01-dapr/00-service-invocation/README.md)

Requirements:
- git
- Docker
- Dapr CLI and ran `dapr init`
- .NET Core 5 SDK


👉 [Publish and subscribe](01-dapr/00-service-invocation/README.md)

Requirements:
- Node.js if you want to run the code locally
- Docker to create and push the images to your AKS cluster
- kubectl configured to access your AKS cluster

## Blue/green release

👉 [Blue/Green releases with Argo Rollouts](04-blue-green-release/README.md)

Requirements:
- kubectl configured to access your AKS cluster
- Installation of the Argo Rollouts kubectl plugin

## Canary release (optional)

👉 [Canary](08-canary-release/README.md)

👉 [Canary wit SMI traffic split](08-canary-release/manifests-smi/README.md)

Requirements:
- kubectl configured to access your AKS cluster
- Installation of the Argo Rollouts kubectl plugin
- Installation of the Linkerd CLI