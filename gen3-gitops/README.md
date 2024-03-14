# This is a staging area for the [gen3-gitops](https://github.com/NIEHS/gen3-gitops) repository forked from uc-cdis.

It contains jinja templates that are used to generate config values to be used by gen3-helm at deploy time.

Value files can be referenced by helm upgrade commands to override default values in the gen3-helm chart.

```commandline
helm upgrade --install gen3 ./helm/gen3 \
-f /path-to/pcor_gen3_artifacts/gen3-gitops/values/etl.yaml \
-f /path-to/pcor_gen3_artifacts/gen3-gitops/values/fence.yaml \
-f /path-to/pcor_gen3_artifacts/gen3-gitops/values/guppy.yaml \
-f /path-to/pcor_gen3_artifacts/gen3-gitops/values/portal.yaml \
-f /path-to/pcor_gen3_artifacts/gen3-gitops/values/values.yaml
```