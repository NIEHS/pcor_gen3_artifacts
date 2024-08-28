# Workflow for updating Gen3 at Chicago

## Make sure gen3-helm is updated

Make sure that gen3-gitops (our NIEHS fork) is up to date with upstream.

see: https://github.com/NIEHS/gen3-gitops

Note: be sure to check if any values under staging have changed in Chicago, these need to be reflected in our [jinja templates](../gen3-gitops/templates/) 
`Jinja templates are set to generate values for AWS staging environment`
`Production configs are to be created manually using auto generated staging values`

## Run generate gitops script

With updated jinja templates, we now run the generate gitops values located in pcor tools

On line 22: https://github.com/NIEHS/pcor_gen3_artifacts/blob/develop/pcor_tools/generate_gen3_gitops_values.py#L22

set the AWS Staging flag to True

```python

AWS_STAGING_FLAG = True

```

## Ensure the data dictionary URL is correct

Coordiate with Jawad for proper s3 bucket for data dictionary, place this value into values.yaml in gen3-gitops as the dictionary location.

see: https://github.com/NIEHS/gen3-gitops/blob/master/staging.chordshealth.org/values/values.yaml#L12

## Update custom image path
Need to manually update the custom image path in the values/portal.yaml file in gen3-gitops
`Todo: automate this step using github actions`

Local server deployment uses path `custom/ospcortf_logo.jpg` while staging uses `custom/images/ospcortf_logo.jpg`.
This is due to difference in how images are served in local vs AWS environments.

```
{
  "src": "custom/images/ospcortf_logo.jpg",
  "href": "https://aspe.hhs.gov/enhancing-patient-centered-outcomes-research-pcor-creating-national-small-area-social-determinants",
  "alt": "Patient-Centered Outcomes Research Trust Fund"
}
```

## Manually move the generated gen3-gitops values into gen3-gitops and prepare PR

The scripts will deposit the generated values in pcor_gen3_artifacts/gen3-gitops/values.

These values are manually copied into the gen3-gitops fork for staging to make the PR to Chicago.

Do a git diff to ensure the settings that were previously there are not overwritten.



## Loading

Loading new 141 via the test_pcor_gen3_ingest

new code at bottom cleans out gen3 upon rerun