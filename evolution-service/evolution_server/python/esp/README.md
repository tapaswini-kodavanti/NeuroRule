# ESP (Evolutionary Surrogate-Enhanced Prediction) Service

This folder contains the code for the ESP service.

This README explains how to set up a Kubernetes cluster running the ESP service with suitable Istio ingress points, 
to accept requests, and egress points, for logging.

# Assumptions
It is assumed that you have access to a suitable AWS account along with privileges to add images to ECR, 
create EC2 instances and set up networking objects such as VPCs, subnets, load balancers and security groups.

It is also a requirement that the management workstation being used to launch these tasks on is an Ubuntu Server using 
18.04 LTS and that the root permissions for installation of software is granted to the user.

This document is aimed at administration personnel who posses Kubernetes and AWS cloud skills.

This document relates to production deployments of ESP.  

In particular, the document outlines a manual process for deploying ESP. Automation is outside the scope of this README.

Tools such as [Ansible](https://www.ansible.com/) could be used for such automation.

When using ESP in a production deployment with AWS it is expected that any domain names will be registered using Route53 
and that AWS will also be used for adding certificates for the service.

A production deployment of ESP on AWS will use an AWS load balancer. The **default idle timeout for AWS load balancers
is 60 seconds**. Based on experience, this timeout value is insufficient to allow a client to request and receive a
completed generation from the ESP service when the population size of the experiment reaches a critical point. To
alleviate this problem, the **load balancer must be configured with a greater time out value**. For example, the current
value in production is 600 seconds.

# Procedure

## Source code
Extract the leaf-ai github repository that contains the ESP proprietary source code:
```shell script
git clone https://github.com/leaf-ai/evolution-service
export ROOT=${PWD}/evolution-service
cd evolution-service/evolution_server/python/esp
```

##  Python environment
These commands prepare a Python runtime environment, using the same directory layout as [direnv](https://direnv.net/), 
and capture the Semver patch version (e.g. '9' for Python 3.8.9)
```shell script
export PYTHON_VERSION=`/usr/bin/python3.8 --version 2>&1 | cut -f2 -d' '`

virtualenv ./.direnv/python-$PYTHON_VERSION -p /usr/bin/python3.8

export CUSTOM_BIN_DIR=./.direnv/python-$PYTHON_VERSION/bin
export PATH=$CUSTOM_BIN_DIR:$PATH
source $CUSTOM_BIN_DIR/activate
```

## AWS command line tools
This installs the latest version of the AWS tools into the Python virtual environment created above.
```shell script
pip install awscli --upgrade
```

## AWS credentials
Set up your AWS credentials (via environment variables or default profile).  
More information [here](https://docs.aws.amazon.com/polly/latest/dg/setup-aws-cli.html).

For example, if you have an AWS profile set up:
```shell script
export AWS_PROFILE=<my profile name>
export AWS_ACCOUNT=`aws sts get-caller-identity --query Account --output text`
export AWS_ACCESS_KEY_ID=$(aws configure get aws_access_key_id)
export AWS_SECRET_ACCESS_KEY=$(aws configure get aws_secret_access_key)
```
Whichever method you used, verify your credentials have been correctly set up. To verify you have access to AWS, run 
the following command should result in a list of S3 buckets in the AWS account to which your credentials pertain:
```shell script
aws s3 ls
2019-05-10 08:00:35 example_dir
2019-07-24 14:50:21 a_bucket
2019-07-24 14:50:20 tests
```

Specify a valid S3 bucket for ESP to persist short-lived model data:

```shell script
export ESP_MODELS_BUCKET=<name of an S3 bucket to which we have write access e.g. my-bucket>
```

## Docker configuration
The following command writes to the docker credentials file at `~/.docker/config.json` which will be used later.

```shell script
`aws ecr get-login --region us-west-2 --no-include-email`
aws ecr create-repository --repository-name esp-service
ls ~/.docker/config.json
```
## ESP Service
Set the ESP version to be used:
```shell script
export ESP_VERSION=<your ESP version e.g. 2.5.1>
```

**Note:** Skip the following section and move on to "Kubernetes and Istio" if the ESP image that you wish to deploy 
already exists in the container repository, for example, if the image was built by someone else or by a CI system.

Build a docker image for deployment in the service mesh. You will choose the version of the service to be deployed
by setting the environment variable `ESP_VERSION` below.
```shell script
pushd $ROOT
docker build -t leaf/esp-service:${ESP_VERSION} -f ./Dockerfile .
docker tag leaf/esp-service:${ESP_VERSION} localhost:32000/leaf/esp-service:${ESP_VERSION}
docker tag leaf/esp-service:${ESP_VERSION} ${AWS_ACCOUNT}.dkr.ecr.us-west-2.amazonaws.com/esp-service:${ESP_VERSION}
docker push ${AWS_ACCOUNT}.dkr.ecr.us-west-2.amazonaws.com/esp-service:${ESP_VERSION}
popd
```
Verify the image is present in the list. There should be an image with a tag matching `ESP_VERSION`.
```shell script
aws ecr describe-images --repository-name esp-service
{
    "imageDetails": [
        {
            "registryId": "241428425432",
            "repositoryName": "esp-service",
            "imageDigest": "sha256:468e70aa1e282270bc3276c4373a6dc079b4712b58ef1be1c7fff03da29904ed",
            "imageTags": [
                "latest",
                "2.5.0"
            ],
            "imageSizeInBytes": 562253730,
            "imagePushedAt": 1569282028.0
        }
    ]
}

```
## Kubernetes tools: kubectl,istioctl and kustomize
The tooling required to interact with the kubernetes cluster requires specific versions
of these tools in order to function correctly. Currently the following
versions are known to be interoperable:
- kubectl (client): 1.18.6
- istioctl: 1.5.0
- kustomize: 3.5.4

### Install Kubernetes client side tooling
```shell script
# Find the correct 'channel' to install
snap info kubectl
```
The output will look something like this. Find the matching release channel name.

channels:<br>
  latest/stable:    1.18.6         2020-07-16 (1580) 10MB classic<br>
  latest/candidate: 1.18.6         2020-07-16 (1580) 10MB classic<br>
  latest/beta:      1.18.6         2020-07-16 (1580) 10MB classic<br>
  latest/edge:      1.18.6         2020-07-16 (1580) 10MB classic<br>
  1.19/stable:      1.19.0-alpha.1 2020-04-20 (1500) 10MB classic<br>
  1.19/candidate:   1.19.0-rc.3    2020-07-29 (1595) 10MB classic<br>
  1.19/beta:        1.19.0-rc.3    2020-07-29 (1595) 10MB classic<br>
  1.19/edge:        1.19.0-rc.3    2020-07-29 (1595) 10MB classic<br>
  **1.18/stable:      1.18.6**         2020-07-16 (1580) 10MB classic<br>
  1.18/candidate:   1.18.6         2020-07-16 (1580) 10MB classic<br>
  1.18/beta:        1.18.6         2020-07-16 (1580) 10MB classic<br>
  1.18/edge:        1.18.6         2020-07-16 (1580) 10MB classic<br>

So in our current case:

```shell script
sudo snap install kubectl --channel=1.18/stable --classic
```
### Install the correct version of kustomize

Use a browser and navigate to https://github.com/kubernetes-sigs/kustomize/releases to 
find the correct release of kustomize and find the correct download URL. Using that,
download the tar.gz as shown in the example below.

```shell script
wget https://github.com/kubernetes-sigs/kustomize/releases/download/kustomize%2Fv3.5.4/kustomize_v3.5.4_linux_amd64.tar.gz
tar xzf kustomize_v3.5.4_linux_amd64.tar.gz
mv kustomize $CUSTOM_BIN_DIR/kustomize
chmod u+x $CUSTOM_BIN_DIR/kustomize
rm kustomize_v3.5.4_linux_amd64.tar.gz

export KUBECONFIG=${HOME}/.kube/config
export KUBE_CONFIG=${KUBECONFIG}
export AWS_AVAILABILITY_ZONES="$(aws ec2 describe-availability-zones --query 'AvailabilityZones[].ZoneName' --output text | awk -v OFS="," '$1=$1')"
```
### Install the correct version of istioctl
Download the correct version as listed above.
For more information see documentation [here](https://istio.io/docs/setup/install/istioctl/)
```shell script
istioctl manifest apply
```

### Verify the installed versions match the requirements
- kubectl (client): 1.18.6
- istioctl: 1.5.0
- kustomize: 3.5.4

**Note** The tooling commands need to be run from the esp home directory and 
from the python virtual environment.

Output shortened for clarity
``` shell script
(python-3.8.9) ubuntu:~/evolution-service/evolution_server/python/esp$ kubectl version
Client Version: version.Info{Major:"1", Minor:"18", GitVersion:"v1.18.6"}
(python-3.8.9) ubuntu:~/evolution-service/evolution_server/python/esp$ kustomize version
{Version:kustomize/v3.5.4}
(python-3.8.9) ubuntu:~/evolution-service/evolution_server/python/esp$ istioctl version
client version: 1.5.0
control plane version: 1.5.0
data plane version: 1.5.0 (5 proxies)
```

### Helm
```shell script
sudo snap install helm --classic
```

### Install the AWS Kubernetes distribution cluster deployment tool and verify
```shell script
KOPS_VERSION=$(curl -s https://api.github.com/repos/kubernetes/kops/releases/latest | grep tag_name | cut -d '"' -f 4)
curl -Lo kops https://github.com/kubernetes/kops/releases/download/$KOPS_VERSION/kops-linux-amd64
chmod +x ./kops
mv ./kops $CUSTOM_BIN_DIR
kops version
```

### Cluster names
Set up the cluster name for Kops commannds to use `KOPS_CLUSTER_NAME`, as well as the qualified cluster name 
`CLUSTER_NAME` for other tools.
```shell script
export CLUSTER_NAME=${USER}-esp-dev
export KOPS_CLUSTER_NAME=${CLUSTER_NAME}.platform.cluster.k8s.local
```

### Kops state store
Create a writeable bucket for Kops and set the environment variable `KOPS_STATE_STORE` to the name of this bucket.
```shell script
export S3_BUCKET=kops-${USER}
export KOPS_STATE_STORE=s3://${S3_BUCKET}
aws s3 mb $KOPS_STATE_STORE 2>/dev/null || true
aws s3api put-bucket-versioning --bucket $S3_BUCKET --versioning-configuration Status=Enabled || true
```

Verify bucket was created:
```shell script
aws s3 ls $KOPS_STATE_STORE
```
(should succeed and show nothing, since the bucket is currently empty.)
### Create a cluster
See note [^1] on clusters
```shell script
kops create cluster --cloud-labels="HostUser=$HOST:$USER" --name $KOPS_CLUSTER_NAME --zones $AWS_AVAILABILITY_ZONES --node-count 1 --master-size=m5.large --node-size=m5.4xlarge --yes
```

Verify the cluster. It will take a while to create the cluster -- several minutes:
```shell script
while [ 1 ]; do
    kops validate cluster &>/dev/null && break || sleep 10
done;
```

### Set up Helm
```shell script
cd $ROOT/evolution_server/python/esp/
kubectl create serviceaccount --namespace kube-system tiller
kubectl create clusterrolebinding tiller-cluster-rule --clusterrole=cluster-admin --serviceaccount=kube-system:tiller
helm init --wait --history-max 200 --service-account tiller --upgrade
helm repo update
```
### Secure with LetsEncrypt Certificate
Run the commands in kube_admin_letsencrypt_README.md.

The same document applies to updating an existing LetsEncrypt Certificate.

### Using Amazon TLS
If you will use the gateway.yaml file you now have the option to enable the AWS TLS.  In order to complete these 
changes the certificate ARN supplied by AWS will be needed.  Applying the changes is done by adding annotations to the 
ingress gateway and then restarting the gateway service as detailed below.

If the services are being protected using AWS certificates then at this point the following step should be used to 
inject the ARN of the certificate into the ALB that will be used by Istio.  The ARN can be obtained from the 
AWS Web UI within the certificate details, be sure to expand the domain name line to see these details on your 
Certificate Manager UI.

This process is more fully described in 
[this github ticket](https://github.com/istio/istio/issues/6566#issuecomment-427136888). 

```shell script
cat << EOF >> ${TEMPLATE_DIR}/kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
- ${TEMPLATE_DIR}/helm-template.yaml
patchesStrategicMerge:
- ${TEMPLATE_DIR}/aws_cert_patches.yaml
EOF
```
Create a `aws_cert_patches.yaml` file:
```shell script
cat << EOF >> ${TEMPLATE_DIR}/aws_cert_patches.yaml
apiVersion: v1
kind: Service
metadata:
  name: istio-ingressgateway
  namespace: istio-system
  annotations:
    service.beta.kubernetes.io/aws-load-balancer-ssl-cert: "arn:aws:acm:us-west-2:241428425432:certificate/c47464c1-5c10-4238-830b-1cdf2cdc6f8a"
    service.beta.kubernetes.io/aws-load-balancer-backend-protocol: "http"
    service.beta.kubernetes.io/aws-load-balancer-ssl-ports: "https"
    service.beta.kubernetes.io/aws-load-balancer-connection-idle-timeout: "60"
EOF
kubectl apply -f ${TEMPLATE_DIR}/helm-template.yaml
rm -rf ${TEMPLATE_DIR}
```

### Cluster secrets for Honeycomb (logging)
At this step we resume the common steps for both AWS and self signed certificates.

Add a secret to your cluster that denotes the ESP Test Mesh API ID for your observational observability events etc.  
This key below is for ESP Test Meshes. For production you will need to source the correct ID.

```shell script
kubectl create secret generic -n kube-system honeycomb-writekey --from-literal=key=<the_key>
kubectl create secret generic -n default honeycomb-writekey --from-literal=key=<the_key>

kubectl create -f https://honeycomb.io/download/kubernetes/metrics/honeycomb-heapster.yaml
kubectl create -f https://honeycomb.io/download/kubernetes/logs/quickstart.yaml
```
### Kubernetes namespace
We will use the Kustomize tool to generate a Kubernetes namespace encapsulating the ESP application for the 
AWS Kubernetes deployment type:

**By hand** : You will see two resource files mentioned within the kustomization.yaml file, 
self-signed-gateway.yaml and gateway.yaml. These files define the ingress gateway for the ESP services and include 
details about the Transport Layer Security being used.  One of these should be chosen and the other deleted in 
accordance with the deployment environment being used.  When gateway.yaml is being used AWS TLS cert details can be 
applied using annotations. This is described later within this document.

```shell script
cp kustomization.yaml kustomization.yaml.bak
cp deployment/example/*.yaml .
cp kustomization.yaml.bak kustomization.yaml
kustomize edit set image esp=${AWS_ACCOUNT}.dkr.ecr.us-west-2.amazonaws.com/esp:${ESP_VERSION}
cp ~/.docker/config.json docker_config.json
```

### Kubernetes secrets
**By hand**: Edit your `docker_config.json` file to ONLY include the credentials of the docker repository you wish to
 use for your production images, then run the following command to encode the docker secret ready for injection:
```shell script
docker_secret=`base64 docker_config.json -w 0`
```

Create a secrets.yaml file and place into it a base64 encoded ~/.docker/config.json file without line breaks:

```shell script
cat <<EOF > secrets.yaml
apiVersion: v1
kind: Secret
type: kubernetes.io/dockerconfigjson
metadata:
  name: dockerkey
data:
  .dockerconfigjson: ${docker_secret}
EOF
```

Create a `versions.yaml` file. 

Note the CPU and memory resource constraints set on the containers via the `resources` element. 

```shell script
cat <<EOF > versions.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: esp-blue
spec:
  replicas: 1
  template:
    spec:
      containers:
      - name: esp
        image: ${AWS_ACCOUNT}.dkr.ecr.us-west-2.amazonaws.com/esp:${ESP_VERSION}
        imagePullPolicy: Always
        resources:
          requests:
            memory: "2Gi"
            cpu: "500m"
          limits:
            memory: "8Gi"
            cpu: "1.0"
      imagePullSecrets:
      - name: docker_key
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: esp-green
spec:
  replicas: 1
  template:
    spec:
      containers:
      - name: esp
        image: ${AWS_ACCOUNT}.dkr.ecr.us-west-2.amazonaws.com/esp:${ESP_VERSION}
        imagePullPolicy: Always
        resources:
          requests:
            memory: "2Gi"
            cpu: "500m"
          limits:
            memory: "8Gi"
            cpu: "1.0"
      imagePullSecrets:
      - name: dockerkey
---
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: grpc-esp-virtual-service
spec:
  http:
  - match:
    - uri:
        prefix: "/"
    route:
    - destination:
        host: esp
        subset: green
---
EOF
```

### Deploy application services
Finally the application services are deployed using the following:

```shell script
kubectl apply -f <(istioctl kube-inject -f <(kustomize build))
````

### Ingress points
Once the service has been initially deployed the ingress being used will not change as services are upgraded and 
changed.  At this point we extract the AWS ingress address and update the Route53 entries that are registered as 
the permanent endpoints for external users, for example:

```shell script
export INGRESS_PORT=$(kubectl -n istio-system get service istio-ingressgateway -o jsonpath='{.spec.ports[?(@.name=="http2")].port}')
export SECURE_INGRESS_PORT=$(kubectl -n istio-system get service istio-ingressgateway -o jsonpath='{.spec.ports[?(@.name=="https")].port}')
export INGRESS_HOST=$(kubectl -n istio-system get service istio-ingressgateway -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')
export CLUSTER_INGRESS=$INGRESS_HOST:$INGRESS_PORT
export | grep INGRESS
```

Output:
```shell script
CLUSTER_INGRESS=a8d37fe51af2511e9889d06a7ff0910d-468246571.us-west-2.elb.amazonaws.com:80
INGRESS_HOST=a8d37fe51af2511e9889d06a7ff0910d-468246571.us-west-2.elb.amazonaws.com
INGRESS_PORT=80
SECURE_INGRESS_PORT=443
```
If you are using an AWS deployed certificate and have it associated with a registered DNS address then communication 
with the ESP service should be done using the DNS host name.

### Securing the service
See note [^3] on authentication using Auth0.

**Note**: Set `AUTH0_CLIENT_ID` and `$AUTH0_CLIENT_SECRET` to appropriate values as provided by your Auth0 administrator.

Obtain an ESP JWT token that is specific to your user credentials, i.e. the typical use case, using the
following commands. **Replace the username and password with your own credentials**:

```shell script
export AUTH0_USERNAME=<your Auth0 username>
export AUTH0_PASSWORD=<your Auth0 password>
export AUTH0_REQUEST=$(printf '{"client_id": "%s", "client_secret": "%s", "audience":"http://api.cognizant-ai.dev/esp","grant_type":"password", "username": ${AUTH0_USERNAME}, "password": ${AUTH0_PASSWORD, "scope": "all:esp", "realm": "Username-Password-Authentication" }' "$AUTH0_CLIENT_ID" "$AUTH0_CLIENT_SECRET")
export AUTH0_TOKEN=$(curl -s --request POST --url https://cognizant-ai.auth0.com/oauth/token --header 'content-type: application/json' --data "$AUTH0_REQUEST" | jq -r '"\(.access_token)"')
```

Verify you obtained a valid Auth0 token:
```shell script
echo $AUTH0_TOKEN 
fyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImtpZCI6Ik5VUXhRMFpFUlVFek9UYzVPRVF6UlVKRFF6YzRRak0xUkRFME1qRkZNRFF3TkRNMFJFTXhRUSJ9.eyJpc3MiOiJodHRwczovL2NvZ25pemFudC1haS5hdXRoMC5jb20vIiwic3ViIjoiYXV0aDB8NWNlZGFiNzRmZmNlNGMxMTAwZGRhMWNiIiwiYXVkIjoiaHR0cDovL2FwaS5jb2duaXphbnQtYWkuZGV2L2VzcCIsImlhdCI6MTU3MjU2NDg5NCwiZXhwIjoxNTcyNTY4NDk0LCJhenAiOiJxTlViaVVjYWdzM0JlSVZJd0tvd0xQR3VmNGJRWGtYaiIsInNjb3BlIjoiYWxsOmVzcCIsImd0eSI6InBhc3N3b3JkIiwicGVybWlzc2lvbnMiOlsiYWxsOmVzcCJdfQ.PvUcvpIm0Z2-aY1yEcL3qXI__dqt4wadyEyKQnIAeLV0NUiNMN3sIkC0anGqHjEBdTLgx2nRnG9lpyh2NBIA5ZGSJVmBRc8i0KJFeYNR25o34IlynOy8eawQ1u6AdGbaQWBmun8ubLB6EOR__RDKunsGPYFzQdJ-pohWX3fATZyMA1XM78QmwhuSMbDicLkY-FmTTSl_caSK6f5KSkRe5lKpJE1QCWei33QvpM3zZVCdQDw3hkakIso86JR7yyVwut7OH6iduZdXSOyBmk4JoZM0iVH9KYYm86wiNBeEzJ7Y_kdNl2DNT9F2rjHFQTqRKyKExfQHpu4zfPUY2fc8jg
```

### Run the test client
This section shows how to run the test client against your installation using dummy experiment data.

Run the following commands to install the requirements for the test client:
```shell script
cd $ROOT
pip install -r requirements.txt
```

Now run the test client to obtain a sample population:

```shell script
PYTHONPATH=. \
python evolution_server/python/esp/esp_client_cli.py \
--host=${INGRESS_HOST} \
--port=${SECURE_INGRESS_PORT} \
--ssl_host_override=esp.cognizant-ai.net \
--auth0_token="${AUTH0_TOKEN}" \
next-population \
--version='v1' \
--experiment_id='abc123' \
--experiment_params_file='tests/fixtures/experiment.json'
```

Sample good response:
```shell script
INFO:esp_client:Connecting to a0eb8d430fccf11e9a2cc064699264fc-744307013.us-west-2.elb.amazonaws.com:443...
INFO:esp_client:Connected.
INFO:esp_client:NextPopulation results: 
individuals:20
generation:1
checkpoint_id:abc123/1/20191101-1936 
```

# Notes
[^1]: The commands given can be used to create a cluster.  For production systems a kops manifest file should be used 
and version controlled. For more information conering production configurations please see 
https://github.com/kubernetes/kops/blob/master/docs/manifests_and_customizing_via_api.md
Using manifests renders creation scripts for clusters redundant. Instead, devops tooling should be used for these cases 
that employ manifests. End-to-end and cluster credentials should also be managed as valuable artifacts.

[^2]: Here, we generate signed certificates for testing. In production we generate signed certificates from the 
Lets Encrypt CA. The steps in this document related to signed certificate deployments are derived from the Istio 
documentation for the 
[secure gateway feature]( https://istio.io/docs/tasks/traffic-management/ingress/secure-ingress-sds).
The way we do this is to use an ACME based provider that integrates with the LetsEncrypt service.
Using an ACME provider allows you to unburden yourself from handling the generation of the certificate chain components.

[^3]: The ESP service when deployed within a service mesh uses JWT to authenticate users connecting to the service.
Users are authenticated using the Auth0.com service. To setup Auth0.com to receive OIDC, (OpenIdentity Connect),
requests from users and from the ESP service a cognizant account has been created using a tenant ID of cognizant-id.
When the production operations role has been filled ownership of this account will be transitioned to the
responsible party. karl.mutch@cognizant.com is assigned temporary ownership until the production operations role
has been filled.

The ESP service is currently provisioned using the free tier which limits logins to 7,000 per month, and a
total of 1,000 access tokens being generated each month. Commercial deployments that require robust security and
production features require plans starting at about $100 a month for the service with 200 regular active users,
along with token validations by the service itself.

The application and API can be configured for ESP using the Auth0.com web UI. The ESP service authentication is a
machine-to-machine application and can be provisioned on the the Auth0 service by creating an API, the API should be
configured with an identifier set to, http://api.cognizant-ai.dev/esp. The cognizant-ai.dev domain is also registered
to karl.mutch@cognizant.com using the google domain service and will be transitioned when the production operations
role is filled.

When setting up the API the "Enable RBAC", "Add Permissions in the Access Token", and the "Allow skipping User Consent"
options should be selected. In the Permissions panel selected from the ribbon bar for the API you should add an
"all:esp" permission that is assigned to users accounts to enable access.The API when created will automatically
create an application for the API. If you navigate to the application panel using the API configuration menu you will
be able to select the Applications authorized for the API, use the mode slider to enable the application and also take
note of the client ID assigned to the application, it will be used when authenticating and when generating tokens.
Beside the modal slider that authorizes the application there is a drop down button that will expose a GRANT_ID and a
list of the scopes that the application supports. Each of these scopes needs to been enabled in order for them to be
accepted by the application when users login requesting them against our API.

Having recorded the URL that acts as the identifier and the clientID you can select the name of the application that
was created and you will be shown the setting panel for the application. The client secret is hidden in the web page
and can be copied to the clipboard. You now have the three elements need to generate tokens, you will also need the
user details.

Applications using the ESP APIs gain access to the service via an API gateway that employs JWT to authenticate the 
incoming requests.  In order for applications to obtain a JWT Token they will need to write code to obtain the token
 and then supply the token to the application via the Bearer standard headers.
