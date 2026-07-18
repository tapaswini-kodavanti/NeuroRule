# Docker image to administer evolution-service kuberenetes cluster

This document describes how to use a docker container to manage the evolution-service (aka ESP) Kubernetes cluster.
The following assumptions apply:
- User has the kubeconfig file on their localhost to allow access to the cluster
- Currently this file is called esp-prod.cfg but that of course is subject to change
- User has AWS credentials to allow access to the container

## Building the container
There exists a Codefresh pipeline which when run will create the container and publish it to our AWS ECR registry.
The pipeline is currently run manually on a as-needed basis.
The tool versions are spelled out in the kube_admin_Dockerfile and do not change frequently.

## Login to docker with AWS credentials

```shell script
aws ecr get-login-password --region us-west-2 --profile leafdev | docker login --username AWS --password-stdin 634208487213.dkr.ecr.us-west-2.amazonaws.com
```

## Determine which tag to use
You can see the available tags by running
``` shell script
docker images 634208487213.dkr.ecr.us-west-2.amazonaws.com/leaf/evolution-service-kube-admin
```

## Run kube admin container

```shell script
docker run -it 634208487213.dkr.ecr.us-west-2.amazonaws.com/leaf/evolution-service-kube-admin:<desired_tag> /bin/bash
```

## Set up credentials to allow cluster access
In the /home/leaf directory, create .aws directory
```shell script
cd ~
mkdir .aws
cd .aws
```
Next, create a file called credentials, using a credential that allows you to assume the LeafKubeAdm role

```
[default]
aws_access_key_id = <your id>
aws_secret_access_key = <your key>

[esp-eks]
role_arn = arn:aws:iam::634208487213:role/LeafKubeAdm
source_profile = default

```
Finally, create a kubectl config by running this command
```shell script
aws eks update-kubeconfig --region us-west-2 --name esp-prod-4 --profile esp-eks
```

## Set venv
```shell script
cd ~/evolution_server/python/esp/
source $HOME/venv/esp-3.8/bin/activate
```

## Test your setup with a simple command
```shell script
kubectl get pods --all-namespaces | grep esp
```
