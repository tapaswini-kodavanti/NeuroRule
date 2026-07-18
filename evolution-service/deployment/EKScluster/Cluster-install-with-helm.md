# Initialize ESP Production Cluster with Helm
#clusters/esp

## Create the Cluster
The configuration for the demo cluster is stored in the leafops repository. The path is AWS_clusters_demo. The commands below expect to be run from leafops_AWS_Clusters/demo

**Create the base cluster**

`eksctl create cluster --profile prodKubeAdmin -f cluster.yaml`

`eksctl create nodegroup --profile prodKubeAdmin -f nodegroup-c6a-4xlarge.yaml`

**Update Security Group settings for nodes to block ssh from world.**
- - - -

**Label the default namespace for istio-injection**

`kubectl label ns default istio-injection=enabled --overwrite`

## Start Services and Applications
**Install Services**
`kubectl apply -f service.yaml`

## Install Isito with Helm
`kubectl create namespace istio-system`

`helm install istio-base istio/base -n istio-system`

`helm install istiod istio/istiod -n istio-system --wait`

`helm install  -f helm/values.yaml istio-ingressgateway istio/gateway  -n default --wait`

### Helm Information Commands
helm status istio-base

helm get all istio-base

 helm status istiod

 helm get all istiod

helm  install istio-ingress --dry-run --debug helm/gateway -n default

## Deployments
Deployments are installed after istio so they get a sidecar.

`kubectl apply -f deployment-blue.yaml`

`kubectl apply -f deployment-green.yaml`


## Install Istio Localizations
`kubectl apply -f virtual-service.yaml`

## Install Istio Auth settings
`kubectl apply -f authorization.yaml`

`kubectl apply -f request-auth.yaml`

## Install Istio Gateway 
`kubectl apply -f gateway.yaml`

*Update Security Policy to recommended. *

**Get a manifest of the ingress resource,**

`kubectl get ingress demo-apps -n istio-system -o yaml`

**Update the Route53 entry in the DAI (7200) account. The domain name is demoapi-test.cognizant-ai.net. Edit the record. Delete the existing load balancer entry. Select one that has "demo-apps" in the name.**