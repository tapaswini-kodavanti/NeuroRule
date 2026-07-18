# Delete the Cluster
#clusters/esp

Follow these steps or enter the seventh layer of AWS interdependency hell.

`kubectl -n default delete gateway esp`

`kubectl delete virtualservices esp`

`kubectl delete service esp`

`kubectl delete deployment  esp-blue esp-green`


`helm uninstall istio-ingressgateway -n default`

`helm uninstall istiod -n istio-system`

`helm uninstall istio-base -n istio-system`

**Delete the node group in eks.**

`eksctl delete nodegroup -f nodegroup-c6a-4xlarge.yaml --profile prodKubeAdmin --approve`

**Watch in Cloud Formation for deletion to finish before moving on.**

**Delete the cluster in EKS**

`eksctl delete cluster -f cluster.yaml --profile prodKubeAdmin`

**Verify in Cloud Formation that all the demo-apps stacks have been deleted.**
