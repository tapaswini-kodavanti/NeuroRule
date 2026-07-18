# Use the kube_admin docker container to update letsencrypt certificate

## To query the current certificate status
From any machine with openssl installed:
```shell script
openssl s_client -showcerts -servername v3.esp.evolution.ml -connect v3.esp.evolution.ml:443 | openssl x509 -noout -dates
```

### Get the Kuberntes config file

`aws eks update-kubeconfig --region us-west-2 --name esp --profile prodKubeAdmin`

### Generate the certs
You may need to start the certbot instance, located in the prod account. If so, the IP address will be different.

`ssh 54.184.136.184`

`sudo -s`

`source /root/.aws/setEnv.sh`

`certbot certonly --dns-route53 `

The domain name is v3.esp.evolution.ml

Tar up and copy the files

`cd /etc/letsencrypt`

`tar -czf /tmp/certs.tgz archive live`

copy to local system

`cd ~/Work/Certificates/2024`

`scp 54.184.136.184:/tmp/certs.tgz .`

` tar -xzf certs.tgz`

### Install the Certificate
`kubectl delete secret esp-tls-credentials`

```
kubectl create secret tls esp-tls-credentials \
 --key=live/v3.esp.evolution.ml/privkey.pem \
 --cert=live/v3.esp.evolution.ml/fullchain.pem
```

### Test with
`curl https://v3.esp.evolution.ml -vI --stderr - | grep "expire date" 
