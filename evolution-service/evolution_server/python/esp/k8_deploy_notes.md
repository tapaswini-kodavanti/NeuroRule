# Deploy New ESP Version to Kuberetes Cluster

This document describes the manual steps required to push a new version of ESP to the Kubernetes cluster.
The following assumptions apply:
- A management workstation is configured according to the README.md document located in this directory.
- evolution-service is already checked out
- kubeconfig file is present in ~/.kube complete with access secrets and context enabled
- ability to run simple ESP experiment for testing changes

## Stand up the required tooling
```shell script
cd evolution-service/evolution_server/python/esp
export PYTHON_VERSION=`/usr/bin/python3.8 --version 2>&1 | cut -f2 -d' '`
virtualenv ./.direnv/python-$PYTHON_VERSION -p /usr/bin/python3.8
export CUSTOM_BIN_DIR=./.direnv/python-$PYTHON_VERSION/bin
export PATH=$CUSTOM_BIN_DIR:$PATH
source $CUSTOM_BIN_DIR/activate
```

### Optional: double check you have all the tools ready
```shell script
kubectl version
istioctl version
kustomize version
```

## Determine which node is live (blue or green)
Blue/green configuration can be determined via configuration review. However, it is advisable to have a
test client and minimal experiment config ready for pre-and-post deploy testing of the nodes. Therefore these directions
describe the empirical way to determine the current live node.

### Get the currently running pod names
```shell script
kubectl get pods --all-namespaces | grep esp
default        esp-blue-5dbd7cdd9c-4pqb9                                             2/2     Running   0          41d
default        esp-green-79ccfb78fb-8sztv
```

### Prepare experiment with unique name to simplify log grepping
Configure your test client experiment with a unique experiment name, eg, 'cluster_test_99'
- This is accomplished by setting experiment_name value in experiment parameters file.
Double check that you are ***not*** specifying a esp_service_name in your config. This
ensures you hit the default live service node.

### Follow the logs of one node, run experiment
Continuing with the example experiment name from above:
```shell script
kubectl logs --follow esp-blue-5dbd7cdd9c-4pqb9 esp | grep cluster_test_99
```

If your experiment doesn't show up there, run against the other node.
Once you have determined which node is live, you may proceed to updating the non-live node.

## Update ESP version on a given node.
To continue the example above, let us say we found 'blue' is the live node and in our case
we want to update the non-live node to the latest ESP version.

### Setup your test client to hit desired node
Again, continuing with our example from above, let us say green is the desired
node for this upgrade. In experiment_params.json file, LEAF section, add
    "esp_service_name": "green"
Run the experiment while watching the green logs to verify your 'before' case is 
working as expected.

### Change configs to specify new ESP version
In esp/deployment/overlays/production modify the versions.yaml file with the desired esp-service version number for either blue or green or both.
    
While still in esp/deployment/overlays/production try a kubectl diff command to see what would change if these changes are applied.

```shell script
kubectl diff -f <(istioctl kube-inject -f <(kustomize build))
```

that should show only a minimal diff if you are only bumping the docker version

`<a long single line that doesnt mean much and then>`

```yaml
-  generation: 22
+  generation: 23
   labels:
     app: esp
   name: esp-green
@@ -72,7 +72,7 @@
             secretKeyRef:
               key: AWS_SECRET_ACCESS_KEY
               name: esp-secrets-25kf4ff872
               - image: 634208487213.dkr.ecr.us-west-2.amazonaws.com/esp:2.6.4
               + image: 634208487213.dkr.ecr.us-west-2.amazonaws.com/esp:2.6.5
         imagePullPolicy: Always
         name: esp
```

### Deploy changes
If the diffs look ok, then go ahead and apply the changes.
```shell script
kubectl apply -f <(istioctl kube-inject -f <(kustomize build))
```

After deploying, run the pods name command again (the pods name change upon deploy). Then run your previous test experiment
while tailing the logs to ensure the experiment runs as before.

### Note: simple way to run test experiment

A simple way to run a test experiment is to use training docker.
See readme for latest. https://github.com/leaf-ai/leafbuild/blob/master/leaf_pack/README.md

Launch the docker interactively:
```shell script
    docker run -it \
    -e 'AUTH0_USERNAME=xxxxx' \
    -e 'AUTH0_PASSWORD=xxxxx' \
    cognizanttraining/leaf bash
```

Once logged into docker container, run experiment:
```shell script
    cd
    source /root/venv/esp-3.8/bin/activate
    <modify experiment json file with unique name, service name if desired>
    python esp_example.py
```

### If things go wrong -- rolling back
To roll back most changes, you can reset your local git repository to the state of origin master (this will lose any
local changes to files):
```shell script
git fetch origin
git reset --hard origin/master
```
You can then re-run the diff command to see what changes will be rolled back: 
```shell script
`kubectl diff -f <(istioctl kube-inject -f <(kustomize build))`
```

If all looks good, apply the changes:

```shell script
kubectl apply -f <(istioctl kube-inject -f <(kustomize build))
```

Note that this will _not_ remove extra items you may have added like `VirtualService`s and gateways. These will need
to be hunted down and cleaned up manually.

### Adding new deployment
For example, for some reason you want to create a new "color" beyond the existing blue and green versions of the
services, such as `orange`.

There are a lot of places that need to be updated to add a new service. One approach is to search recursively all 
files under the `deployment` directory of this project for "blue" (one of the existing services). That will give you 
an idea of all the places that need to be touched and which files you will need to make copies of for your new
service.

### Adding a new namespace
Examine the file `deployment/infrastructure/namespace.yaml`. This shows how to create a new namespace via
`kustomize`. When creating items in your new namespace such as `VirtualService`s and `DestinationRule`s, you will
need to specify the namespace at the appropriate place in your YAML file.

Note that due to [this issue](https://github.com/istio/istio/issues/22463) you will need to copy over the secrets
relating to the TLS certificate from the default namespace to your new namespace.

To copy the `configmap`:
```shell script
kubectl get configmap istio-ca-root-cert --namespace=default -o yaml | \
sed 's/namespace: default/namespace: <your_namespace>/' | \
kubectl create -f - configmap/istio-ca-root-cert created
```

To copy the "secret":
```shell script
kubectl get secrets esp-secrets-25kf4ff872 --namespace=default -o yaml | sed 's/namespace: default/namespace: <your_namespace>/' | kubectl create -f -
```
