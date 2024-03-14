# Local Development Workflow
Procedures and docs for developing the data portal

## Deploying Gen3 using Rancher Desktop

Install [Rancher Desktop](https://docs.rancherdesktop.io/)

After Rancher Desktop is installed, users will have access to these supporting utilities:
* Helm
* kubectl
* nerdctl
* Moby
* Docker Compose


Once rancher is installed.

1. Clone the repository
2. Navigate to the gen3-helm/helm/gen3 directory and run `helm dependency update`
3. Navigate to the back to the gen3-helm directory and create your values.yaml file. See the Sample values.yaml section for a minimal example.
4. Run `helm install --namespace gen3 gen3 ./helm/gen3 -f ../helm-local/values.yaml` (adjusting the location of your local values).
5. Bring up https://localhost. You may need an incognito window to accept the cert.


### Sample values.yaml
Use the following as a template for your values.yaml file for a minimum deployment of gen3 using these helm charts.

``` yaml
global:
  hostname: localhost
  dictionaryUrl: https://raw.githubusercontent.com/NIEHS/pcor_gen3_artifacts/feature/local-portal/custom_configs/schema.json

fence:
  FENCE_CONFIG:
    MOCK_AUTH: true

# Selective deployments: All service helm charts are sub-charts of the gen3 chart (which acts as an umbrella chart) To enable or disable a service you can add this pattern to your values.yaml
guppy:
  enabled: false

hatchery:
  enabled: false
```


## Loading data notes

Once data is loaded, the ETL job needs to be started (and guppy restarted). See (https://github.com/NIEHS/gen3-helm/blob/master/docs/etl.md)

## Developer tools and scripts

This repo will hold scripts and tools that help with the development workflow.

* [pull_containers.sh](../pull_containers.sh) is a script that can will pull the relevant docker images, faster than letting Helm do it
* [local_portal.py](../attic/local_portal.py) is a utility script for running data_portal locally for gitops development and for building the custom container. This is a work in progres, check the comments in that script for usage
