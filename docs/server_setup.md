# Server setup for Gen3
Document covers setup of gen3.niehs.nih.gov hosted on a server.

## Accessing the server

### Log In to SCIGATE
Refer: [Logging In](https://osc.niehs.nih.gov/hpcdocs/)

You will be prompted to log in.  Login as: <NIH Username> when prompted for password: <NIH Password>

Once you have logged into SCIGate you will need to ssh to the server.

### SSH to Server

```
ssh gen3.niehs.nih.gov
```

### Use sudo to switch to gen3 user
(note: sudo rights must be granted by admin)

```
sudo su - gen3

[sudo] password for <username>:
```
Enter NIH password when prompted.

## prerequisite tools installation
### kubectl
Refer: [Installation steps](https://kubernetes.io/docs/tasks/tools/install-kubectl-linux/)

```json
>kubectl version --output=json
{
  "clientVersion": {
    "major": "1",
    "minor": "26",
    "gitVersion": "v1.26.0",
    "gitCommit": "b46a3f887ca979b1a5d14fd39cb1af43e7e5d12d",
    "gitTreeState": "clean",
    "buildDate": "2022-12-08T19:58:30Z",
    "goVersion": "go1.19.4",
    "compiler": "gc",
    "platform": "linux/amd64"
  },
  "kustomizeVersion": "v4.5.7"
}
```

### kubernetes
Refer: [Installation steps](https://www.devopsart.com/2023/01/step-by-step-installation-of-k3s-in.html)

```
curl -sfL https://get.k3s.io | INSTALL_K3S_VERSION=v1.21.14+k3s1 sh -s
```

### helm
Package manager for Kubernetes

Select a release version to be installed: [latest releases](https://github.com/helm/helm/releases)  

Refer: [Installation steps](https://helm.sh/docs/intro/install/#from-the-binary-releases)

version installed: `helm-v3.12.2-linux-amd64.tar.gz`

```json
>helm version
version.BuildInfo{Version:"v3.12.2", GitCommit:"1e210a2c8cc5117d1055bfaa5d40f51bbc2e345e", GitTreeState:"clean", GoVersion:"go1.20.5"}
```

### REPO setup
We will be using a service account **gen3** for deployment purpose.  

gen3 home dir location: `/var/althome/gen3`

#### pcor_gen3_artifacts
This [repository](https://github.com/NIEHS/pcor_gen3_artifacts) is a hub for PCOR development, docs and development workflow tools.  
Refer [README.md](https://github.com/NIEHS/pcor_gen3_artifacts#readme) for more details.  
> Clone repo and checkout git branche: `develop`  


#### gen3-helm
This [repository](https://github.com/uc-cdis/gen3-helm) contains Helm charts for deploying [Gen3](https://gen3.org) on any kubernetes cluster.  
> Clone repo and checkout git branch: `feat/es7`


```bash
gen3@ehsntpld06 [~]
>ls -1
attic                    ---> old repo files and folders
certs                    ---> ssl certs for gen3.niehs.nih.gov
gen3-helm                ---> [repo]
pcor_gen3_artifacts      ---> [repo]
```

### Deployment
On the server:
1. Navigate to gen3-helm repo
1. edit `helm/revproxy/values.yaml` file to add SSL cert and key
    ```
    # -- (map) Global configuration options.
    global:
    tls:
        cert: |
          -----BEGIN CERTIFICATE-----
          -----END CERTIFICATE-----
        key: |
          -----BEGIN PRIVATE KEY-----
          -----END PRIVATE KEY-----

1. Navigate to the gen3-helm/helm/gen3 directory and run `helm dependency update`
1. Navigate to the back to the gen3-helm directory
1. Copy values.yaml file from pcor_gen3_artifacts repo's [custom_configs](https://github.com/NIEHS/pcor_gen3_artifacts/tree/main/custom_configs) folder.  
`cp ~/pcor_gen3_artifacts/custom_configs/values.yaml ~/gen3-helm/`
1. Edit hostname in values.yaml
    ```
    global:
      hostname: gen3.niehs.nih.gov
    ```
1. Run `helm upgrade --install gen3 ./helm/gen3 -f ./values.yaml`

On your local machine:
1. Bring up https://gen3.niehs.nih.gov
1. Generate credentials.json under user profile
1. load data using python ingest pipeline

Ref: https://github.com/NIEHS/pcor_gen3_artifacts/blob/feature/sops/pcor_tools/RUNNING.md

On the Server:
1. Submit ETL job run `kubectl create job --from=cronjob/etl-cronjob etl`
1. Once ETL job is complete you can either wait for Kubernetes to re-deploy guppy or do it manually by killing current pod.  
*N.B.*: Guppy pod will fail until ETL job is completed,