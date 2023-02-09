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
4. Run `helm upgrade --install gen3 ./helm/gen3 -f ./values.yaml`


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