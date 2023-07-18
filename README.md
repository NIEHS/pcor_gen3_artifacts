# PCOR Gen3 Artifacts

This repository is a hub for PCOR development, docs and development workflow tools. 

PCOR has multiple associated repositories which are cataloged here:

* [PCOR Climate Tools](https://github.com/NIEHS/pcor_climate_tools) holds notebooks, workflows and other specific tools
* [Data Portal](https://github.com/NIEHS/data-portal) holds a fork of the Gen3 data portal with PCOR customizations
* [Gen3 Helm](https://github.com/NIEHS/gen3-helm) holds Helm charts for installing Gen3 locally or on AWS and is a fork of CDIS


This space is for development and encoding of a data model for PCOR to support the data catalog and other activities.

* The [docs](./docs/) section includes developer docs for [running the portal](./docs/local-development-workflow.md) as a dev and [data model development workflow](./docs/model-development.md)
* The [schema](./schema/gdcdictionary/schemas/) section holds the encoded model artifacts
* The [workflows section](./.github/workflows/) supports GitHub CI/CD actions and automation for model development
* The [custom configs](./custom_configs/) section holds the gitops, manifest, and other deployment artifacts that customize the catalog

## Notes

The github actions here synch with the chords-health-dictionary and the cdis-manifest




