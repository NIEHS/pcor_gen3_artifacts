{
    "@context": {
        "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
        "xsd": "http://www.w3.org/2001/XMLSchema#",
        "pav": "http://purl.org/pav/",
        "schema": "http://schema.org/",
        "oslc": "http://open-services.net/ns/core#",
        "skos": "http://www.w3.org/2004/02/skos/core#",
        "rdfs:label": {
            "@type": "xsd:string"
        },
        "schema:isBasedOn": {
            "@type": "@id"
        },
        "schema:name": {
            "@type": "xsd:string"
        },
        "schema:description": {
            "@type": "xsd:string"
        },
        "pav:derivedFrom": {
            "@type": "@id"
        },
        "pav:createdOn": {
            "@type": "xsd:dateTime"
        },
        "pav:createdBy": {
            "@type": "@id"
        },
        "pav:lastUpdatedOn": {
            "@type": "xsd:dateTime"
        },
        "oslc:modifiedBy": {
            "@type": "@id"
        },
        "skos:notation": {
            "@type": "xsd:string"
        },
        "SUBMITTER": "https://schema.metadatacenter.org/properties/3d454dea-f6f5-4e7b-b846-d684caacb084",
        "PROGRAM": "https://schema.metadatacenter.org/properties/e71f602c-cd3d-4ef2-ae3f-7b0aa9c220d7",
        "PROJECT": "https://schema.metadatacenter.org/properties/781467e3-30b8-4f60-b176-2047373ae399",
        "RESOURCE": "https://schema.metadatacenter.org/properties/f19bc2e3-ff1b-441e-8d33-a5dd3d25d9cf",
        "DATA RESOURCE": "https://schema.metadatacenter.org/properties/767bc5d6-7a8f-49ff-b390-952b50ef0d13",
        "GEOEXPOSURE DATA": "https://schema.metadatacenter.org/properties/f01cea3d-2e30-41b4-8f96-85a63548a510"
    },
    "SUBMITTER": {
        "@context": {
            "submitter_name": "https://schema.metadatacenter.org/properties/96a4f91e-12ab-4e54-b81d-c2914ef4a68c",
            "submitter_email": "https://schema.metadatacenter.org/properties/ee4a4a76-80a5-4283-86df-7c4d55f38072",
            "comment": "https://schema.metadatacenter.org/properties/6d11bd44-02e2-4915-b78d-d4dd1788fef5"
        },
        "submitter_name": {
            "@value": "{{ submission.curator_name }}"
        },
        "submitter_email": {
            "@value": "{{  submission.curator_email }}"
        },
        "comment": {
            "@value": "{{ submission.curator_comment }}"
        }
    },
    "PROGRAM": {
        "@context": {
            "Program_name": "https://schema.metadatacenter.org/properties/3521c0a4-3cb9-4b8f-93f9-0454ae0a72b9"
        },
        "Program_name": {
            "@value": "CHORDS"
        }
    },
    "PROJECT": {
        "@context": {
            "project_GUID": "https://schema.metadatacenter.org/properties/ae6efa9f-f645-41ce-9d57-cda2cad1d59c",
            "ProjecCode": "https://schema.metadatacenter.org/properties/ce99dd03-752d-4d29-92f0-b703ca9bea04",
            "project_name": "https://schema.metadatacenter.org/properties/d0113916-e0b8-4b26-822d-9ccb583f779d",
            "project_short_name": "https://schema.metadatacenter.org/properties/b6f426f0-75ab-44f4-b080-5a2aefd07f2e",
            "project_sponsor": "https://schema.metadatacenter.org/properties/b327cc8d-c5a5-40ee-8e44-2e1f92784cc0",
            "project_sponsor_other": "https://schema.metadatacenter.org/properties/9d6666ca-4390-467b-8797-e91c4a7542a8",
            "project_sponsor_type": "https://schema.metadatacenter.org/properties/0a09a32e-919b-450a-8c5e-6b5280c3327b",
            "project_sponsor_type_other": "https://schema.metadatacenter.org/properties/f353c0d9-02b1-4086-a596-66d40b3feca5",
            "project_url": "https://schema.metadatacenter.org/properties/2585ffee-8e89-485f-b44a-e1f945028341"
        },
        "project_GUID": {
            "@value": "{{ project.id }}"
        },
        "ProjecCode": {
            "@value": "{{ project.code }}"
        },
        "project_name": {
            "@value": "{{ project.name }}"
        },
        "project_short_name": {
            "@value": "{{ project.short_name }}"
        },
        "project_sponsor": [
            {% for entry in project.project_sponsor %}
                {
                    "@value": "{{ entry }}"
                }
                {{ "," if not loop.last }}
            {% endfor %}
        ],
        "project_sponsor_other": [
            {% for entry in project.project_sponsor_other %}
                {
                    "@value": "{{ entry }}"
                }
                {{ "," if not loop.last }}
            {% endfor %}
        ],
        "project_sponsor_type": [
            {% for entry in project.project_sponsor_type %}
                {
                    "@value": "{{ entry }}"
                }
                {{ "," if not loop.last }}
            {% endfor %}
        ],
        "project_sponsor_type_other": [
            {% for entry in project.project_sponsor_other %}
                {
                    "@value": "{{ entry }}"
                }
                {{ "," if not loop.last }}
            {% endfor %}
        ],
        "project_url": {
            "@id": "{{ project.project_url }}"
        }
    },
    "RESOURCE": {
        "@context": {
            "resource_GUID": "https://schema.metadatacenter.org/properties/395d7b78-7df4-4f87-bf2d-ed737ea0a163",
            "resource_name": "https://schema.metadatacenter.org/properties/30180920-c9cd-4184-b862-517fbf0a6448",
            "resource_type": "https://schema.metadatacenter.org/properties/0e9d47cb-5830-4c66-a712-8a4679532ddf",
            "domain": "https://schema.metadatacenter.org/properties/a66fa3f7-0e4c-4dd2-95ea-8911edf7bf6f",
            "domain_other": "https://schema.metadatacenter.org/properties/7e0e76ec-eebe-470a-8bdf-ec6d446b33d0",
            "access_type": "https://schema.metadatacenter.org/properties/a9f58a11-091e-455d-85f7-b4a02a66c8dc",
            "date_added": "https://schema.metadatacenter.org/properties/22e082a7-a677-4f22-be11-f1e524144f37",
            "Date_updated": "https://schema.metadatacenter.org/properties/474948e3-03f7-4168-ad0d-7f6a5d8fa326",
            "date_verified": "https://schema.metadatacenter.org/properties/115921e3-9860-42da-8cd1-7808f8eeebdc",
            "Publication": "https://schema.metadatacenter.org/properties/c6dbe16e-b7a8-4d36-8e58-d2833487cb76",
            "resource_short_name": "https://schema.metadatacenter.org/properties/20738dc0-8d33-4061-b1de-d4ebc3406df0",
            "keywords": "https://schema.metadatacenter.org/properties/5d6e8c97-9baf-4e55-b972-f21bcf0f1e1f",
            "resource_url": "https://schema.metadatacenter.org/properties/0dbb1ce4-3762-43df-b510-85e569b9c13a",
            "resource_description": "https://schema.metadatacenter.org/properties/1738ec04-e63d-4c24-b418-466bd3c35a21",
            "payment_required": "https://schema.metadatacenter.org/properties/4dfcf4d7-57cd-4af0-8146-0e30e2300e2e",
            "is_static": "https://schema.metadatacenter.org/properties/1fc3039a-b4e6-4c0a-82e0-839a8ce204d4",
            "Resource Reference_150": "https://schema.metadatacenter.org/properties/40d516a3-c2e7-48c9-a47a-1d86962656f0",
            "Resource Use Agreement_150": "https://schema.metadatacenter.org/properties/de892817-974c-4e6e-9cf8-c82d5c53d71a"
        },
        "resource_GUID": {
            "@value": "{{ resource.id }}"
        },
        "resource_name": {
            "@value": "{{ resource.name }}"
        },
        "resource_type": {
            "@value": "{{ resource.resource_type }}"
        },
        "domain": [
            {% for entry in resource.domain %}
                {
                    "@value": "{{ entry }}"
                }
                {{ "," if not loop.last }}
            {% endfor %}
        ],
        "domain_other": [
            {% for entry in resource.domain_other %}
                {
                    "@value": "{{ entry }}"
                }
                {{ "," if not loop.last }}
            {% endfor %}
        ],
        "access_type": {
            "@value": "{{ resource.access_type }}"
        },
        "date_added": {
            "@value": "{{ resource.created_datetime }}"
        },
        "Date_updated": {
            "@value": "{{ resource.updated_datetime }}"
        },
        "date_verified": {
            "@value": "{{ resource.verification_datetime }}"
        },
        "Publication": {
            "@context": {
                "publication_link": "https://schema.metadatacenter.org/properties/fbdce454-376d-47d8-92d0-dd76b9ec9f4e",
                "publication_citation": "https://schema.metadatacenter.org/properties/ab995a4e-a162-4820-936f-7a5dfcba3cdb"
            },
            "publication_link": [
                {% for entry in resource.publication_links %}
                    {
                        "@id": "{{ entry }}"
                    }
                    {{ "," if not loop.last }}
                {% endfor %}
            ],
            "publication_citation": [
                {% for entry in resource.publications %}
                    {
                        "@value": "{{ entry }}"
                    }
                    {{ "," if not loop.last }}
                { % endfor %}

            ]
        },
        "resource_short_name": {
            "@value": "{{ resource.short_name }}"
        },
        "keywords": [
            {% for entry in resource.keywords %}
                {
                    "@value": "{{ entry }}"
                }
                {{ "," if not loop.last }}
            {% endfor %}
        ],
        "resource_url": {
            "@id": "{{ resource.resource_url }}"
        },
        "resource_description": {
            "@value": "{{ resource.description }}"
        },
        "payment_required": {
            "@value": "{{ resource.payment_required }}"
        },
        "is_static": {
            "@value": "{{ resource.is_static }}"
        },
        "Resource Reference_150": {
            "@context": {
                "resource_reference": "https://schema.metadatacenter.org/properties/708239b8-c6d7-4100-947e-27389304d5fc",
                "resource_reference_link": "https://schema.metadatacenter.org/properties/1803de62-237c-4d4a-9df7-ba81c0f59326"
            },
            "resource_reference": {
                "@value": "{{  resource.resource_reference }}"
            },
            "resource_reference_link": {
                "@id": "{{  resource.resource_reference_link }}"
            },
            "Resource Use Agreement_150": {
                "@context": {
                    "resource_use_agreement": "https://schema.metadatacenter.org/properties/f62f7609-8ed8-44ca-9536-25d4d58d048c",
                    "resource_use_agreement_link": "https://schema.metadatacenter.org/properties/176d9215-4b01-437d-9520-84a348ff0056"
                },
                "resource_use_agreement": {
                    "@value": "{{ resource.resource_use_agreement }}"
                },
                "resource_use_agreement_link": {
                    "@id": "{{ resource.resource_use_agreement_link }}"
                }
            }
        },
        "DATA RESOURCE": {
            "@context": {
                "source_name": "https://schema.metadatacenter.org/properties/f1410177-357b-4882-93ce-ee39187a4a32",
                "update_frequency": "https://schema.metadatacenter.org/properties/0c0b551d-4fab-4518-ad03-a411f4bcb9b6",
                "includes_citizen_collected": "https://schema.metadatacenter.org/properties/0b94ec22-348a-474d-a59b-befc62688a82",
                "has_api": "https://schema.metadatacenter.org/properties/a9a1107a-ed6f-4da8-8b02-8b31bbd1c8b2",
                "has_visualization_tool": "https://schema.metadatacenter.org/properties/a7307f38-6919-4b21-9290-109894f8afd2",
                "Comments": "https://schema.metadatacenter.org/properties/cc95f1c8-0abe-4702-8aed-98be3d54436c",
                "intended_use": "https://schema.metadatacenter.org/properties/b03a83c8-2b53-4216-b3c8-7410944d7df4",
                "update_frequency_other": "https://schema.metadatacenter.org/properties/2c2daca1-8bbc-4bda-9d4d-88233afaff87"
            },
            "source_name": [
                {% for entry in geospatial_data_resource.source_name %}
                    {
                        "@value": "{{ entry }}"
                    }
                    {{ "," if not loop.last }}
                {% endfor %}
            ],
            "update_frequency": [
                {% for entry in geospatial_data_resource.update_frequency %}
                    {
                        "@value": "{{ entry }}"
                    }
                    {{ "," if not loop.last }}
                {% endfor %}
            ],
            "includes_citizen_collected": {
                "@value": "{{ geospatial_data_resource.includes_citizen_collected }}"
            },
            "has_api": {
                "@value": "{{ geospatial_data_resource.has_api }}"
            },
            "has_visualization_tool": {
                "@value": "{{ geospatial_data_resource.has_visualization_tool }}"
            },
            "Comments": {
                "@value": "{{ geospatial_data_resource.comments }}"
            },
            "intended_use": {
                "@value": "{{ geospatial_data_resource.intended_use }}"
            },
            "update_frequency_other": {
                "@value": "{{ geospatial_data_resource.update_frequency_other }}"
            }
        },
        "GEOEXPOSURE DATA": {
            "@context": {
                "measures": "https://schema.metadatacenter.org/properties/815df678-05eb-4e92-a0a4-157e78ddc102",
                "measures_other": "https://schema.metadatacenter.org/properties/6b89e65a-2f3c-48b6-b347-62cafd1bc5e6",
                "measurement_method": "https://schema.metadatacenter.org/properties/b041701b-3fa2-4163-8912-b1da81587379",
                "time_extent_start": "https://schema.metadatacenter.org/properties/8238cff8-de46-4efe-b38d-2dc8e8fe5316",
                "time_extent_end": "https://schema.metadatacenter.org/properties/37a5e8f3-dce4-485d-9e0d-44d2ce20c93d",
                "temporal_resolution": "https://schema.metadatacenter.org/properties/2a8c9390-5828-4c63-a388-98245625d312",
                "spatial_resolution": "https://schema.metadatacenter.org/properties/2d251fb8-92b3-441c-a259-fd75b4e17ac0",
                "spatial_resolution_other": "https://schema.metadatacenter.org/properties/3063a0db-c708-4c17-9afd-9ff9a27b4225",
                "spatial_coverage": "https://schema.metadatacenter.org/properties/887b3698-4443-4039-857a-05150c4cbb17",
                "spatial_coverage_specific_regions": "https://schema.metadatacenter.org/properties/60dc6de2-9b33-4fe8-aa76-99af99a14693",
                "spatial_bounding_box": "https://schema.metadatacenter.org/properties/7d2a6483-7ddc-46b7-9ced-32d9d34a5fd6",
                "geometry_type": "https://schema.metadatacenter.org/properties/edb8b817-dcc2-46bc-a687-8fb6048797e3",
                "geometry_source": "https://schema.metadatacenter.org/properties/f2435c54-6cab-4bc5-90d1-efe4377cd077",
                "model_methods": "https://schema.metadatacenter.org/properties/77473736-5d3c-4c96-a111-cd6cf92ad3f9",
                "exposure_media": "https://schema.metadatacenter.org/properties/b48ef6ad-267f-433f-ad98-02cfcd31d84a",
                "geographic_feature": "https://schema.metadatacenter.org/properties/56c4ed3e-7f04-4736-bdfe-400bfd0527f1",
                "geographic_feature_other": "https://schema.metadatacenter.org/properties/4dcefc8d-4b80-4edc-9951-8a556daa9eec",
                "data_formats": "https://schema.metadatacenter.org/properties/f0cbec7d-e517-4d53-866b-c2cdc6949d3f",
                "measurement_method_other": "https://schema.metadatacenter.org/properties/3e808915-27d9-434e-a428-b80ca070bafc",
                "data_location": "https://schema.metadatacenter.org/properties/37139233-991a-4079-a223-adba071e9aa2",
                "model_methods_other": "https://schema.metadatacenter.org/properties/08e7218e-c64d-4127-9a36-6e129c6e2db7",
                "time_available_comment": "https://schema.metadatacenter.org/properties/962d550f-4387-413e-b037-a18f764fa4b6"
            },
            "measures": [
                {% for entry in geospatial_data_resource.measures %}
                    {
                        "@value": "{{ entry }}"
                    }
                    {{ "," if not loop.last }}
                {% endfor %}
            ],
            "measures_other": [
                {% for entry in geospatial_data_resource.measures_other %}
                    {
                        "@value": "{{ entry }}"
                    }
                    {{ "," if not loop.last }}
                {% endfor %}
            ],
            "measurement_method": [
                {% for entry in geospatial_data_resource.measurement_method %}
                    {
                        "@value": "{{ entry }}"
                    }
                    {{ "," if not loop.last }}
                {% endfor %}
            ],
            "time_extent_start": {
                "@value": "{{ geospatial_data_resource.time_extent_start_yyyy }}"
            },
            "time_extent_end": {
                "@value": "{{ geospatial_data_resource.time_extent_end_yyyy }}"
            },
            "temporal_resolution": [
                {% for entry in geospatial_data_resource.temporal_resolution %}
                    {
                        "@value": "{{ entry }}"
                    }
                    {{ "," if not loop.last }}
                {% endfor %}
            ],
            "spatial_resolution": [
                {% for entry in geospatial_data_resource.spatial_resolution %}
                    {
                        "@value": "{{ entry }}"
                    }
                    {{ "," if not loop.last }}
                {% endfor %}
            ],
            "spatial_resolution_other": [
                {% for entry in geospatial_data_resource.spatial_resolution_other %}
                    {
                        "@value": "{{ entry }}"
                    }
                    {{ "," if not loop.last }}
                {% endfor %}
            ],
            "spatial_coverage": [
                {% for entry in geospatial_data_resource.spatial_coverage %}
                    {
                        "@value": "{{ entry }}"
                    }
                    {{ "," if not loop.last }}
                {% endfor %}
            ],
            "spatial_coverage_specific_regions": [
                {% for entry in geospatial_data_resource.spatial_coverage_specific_regions %}
                    {
                        "@value": "{{ entry }}"
                    }
                    {{ "," if not loop.last }}
                {% endfor %}
            ],
            "spatial_bounding_box": [
                {% for entry in geospatial_data_resource.spatial_bounding_box %}
                    {
                        "@value": "{{ entry }}"
                    }
                    {{ "," if not loop.last }}
                {% endfor %}
            ],
            "geometry_type": [
                {% for entry in geospatial_data_resource.spatial_coverage_geometry_type %}
                    {
                        "@value": "{{ entry }}"
                    }
                    {{ "," if not loop.last }}
                {% endfor %}
            ],
            "geometry_source": [
                {
                    "@value": "{{ geospatial_data_resource.geometry_source }}"
                }
            ],
            "model_methods": [
                {% for entry in geospatial_data_resource.model_methods %}
                    {
                        "@value": "{{ entry }}"
                    }
                    {{ "," if not loop.last }}
                {% endfor %}
            ],
            "exposure_media": [
                {% for entry in geospatial_data_resource.exposure_media %}
                    {
                        "@value": "{{ entry }}"
                    }
                    {{ "," if not loop.last }}
                {% endfor %}
            ],
            "geographic_feature": [
                {% for entry in geospatial_data_resource.geographic_feature %}
                    {
                        "@value": "{{ entry }}"
                    }
                    {{ "," if not loop.last }}
                {% endfor %}
            ],
            "geographic_feature_other": [
                {% for entry in geospatial_data_resource.geographic_feature_other %}
                    {
                        "@value": "{{ entry }}"
                    }
                    {{ "," if not loop.last }}
                {% endfor %}
            ],
            "data_formats": [
                {% for entry in geospatial_data_resource.data_formats %}
                    {
                        "@value": "{{ entry }}"
                    }
                    {{ "," if not loop.last }}
                {% endfor %}
            ],
            "measurement_method_other": [
                {% for entry in geospatial_data_resource.measurement_method_other %}
                    {
                        "@value": "{{ entry }}"
                    }
                    {{ "," if not loop.last }}
                {% endfor %}
            ],
            "data_location": [
                {% for entry in geospatial_data_resource.data_location %}
                    {
                        "@value": "{{ entry }}"
                    }
                    {{ "," if not loop.last }}
                {% endfor %}
            ],
            "model_methods_other": [
                {% for entry in geospatial_data_resource.model_methods_other %}
                    {
                        "@value": "{{ entry }}"
                    }
                    {{ "," if not loop.last }}
                {% endfor %}
            ],
            "time_available_comment": {
                "@value": "{{ geospatial_data_resource.time_available_comment }}"
            }
        }
    }
