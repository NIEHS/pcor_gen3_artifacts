import json

import sys
import logging
import asyncio

from gen3.auth import Gen3Auth
from gen3.metadata import Gen3Metadata
from gen3.tools import metadata
from gen3.tools.metadata.ingest_manifest import manifest_row_parsers
from gen3.utils import get_or_create_event_loop_for_thread
from jinja2 import Environment, PackageLoader, select_autoescape

logging.basicConfig(filename="output.log", level=logging.DEBUG)
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

# a file containing a "guid" column and additional, arbitrary columns to populate
# into the metadata service
template_file = "pcor_ingest/templates/discoverymd.jinja"


def main():

    auth = Gen3Auth(refresh_file="/Users/pateldes/.gen3/credentials-local.json")
    # auth = Gen3Auth(refresh_file="/Users/conwaymc/credentials-http.json")

    # must provide a str to namespace the metadata from the file in a block in
    # the metadata service
    metadata_source = "pcor"
    resc_guid ="75964cb1-9d8e-45bd-a7db-14f529aca591"

    env = Environment(loader=PackageLoader("load_pcor_via_template"))
    env.filters['jsonify'] = json.dumps

    tags_1 = [{"name": "resource", "category": "Resource"},
            {"name": "USGS", "category": "Program"},
            {"name": "LANDFIRE", "category": "Data Source"},
            {"name": "fuel", "category": "Variable"},
            {"name": "vegetation", "category": "Variable"},
            {"name": "fire regime", "category": "Variable"},
            {"name": "web site", "category": "Link Type"},
            {"name": "geospatial data resource", "category": "Resource Type"}
            ]

    adv_search_filters_1 = [{"key_name": "Gender", "key_value": "Female"}]

    resource_data_1 = {
        "name": "LANDFIRE",
        "full_name": "LANDFIRE",
        "resource_description": "Reports of wildfire incidents, acreage burned, and location",
        "resource_id": "75964cb1-9d8e-45bd-a7db-14f529aca591",
        "resource_url": "https://www.fire.ca.gov/incidents/",
        "resolution": "undetermined"
    }

    template = env.get_template("discoverymd.jinja")
    content_1 = template.render(tags=tags_1, advSearchFilters=adv_search_filters_1, resource_data=resource_data_1)

    # Reading from file
    gen3_discovery_1 = json.loads(content_1)
    discoverable_data_1 = dict(_guid_type="discovery_metadata", gen3_discovery=gen3_discovery_1)

    metadata = Gen3Metadata(auth)
    #metadata.admin_endpoint = "http://localhost"
    metadata.create(resc_guid,discoverable_data_1, aliases=None, overwrite=True)

    # second entry
    resc_guid_2 = "12345aa1-9d8e-45bd-a7db-12a123abc123"

    tags_2 = [{"name": "resource", "category": "Resource"},
              {"name": "USGS", "category": "Program"},
              {"name": "FLOOD", "category": "Data Source"},
              {"name": "forest", "category": "Variable"},
              {"name": "web site", "category": "Link Type"},
              {"name": "geospatial data resource", "category": "Resource Type"}
              ]

    adv_search_filters_2 = [{"key_name": "Gender", "key_value": "Male"}]

    resource_data_2 = {
        "name": "Flood",
        "full_name": "Flood",
        "resource_description": "Reports of flood",
        "resource_id": "712345aa1-9d8e-45bd-a7db-12a123abc123",
        "resource_url": "https://www.fire.ca.gov/incidents/",
        "resolution": "undetermined"
    }

    content_2 = template.render(tags=tags_2, advSearchFilters=adv_search_filters_2, resource_data=resource_data_2)
    gen3_discovery_2 = json.loads(content_2)
    discoverable_data_2 = dict(_guid_type="discovery_metadata", gen3_discovery=gen3_discovery_2)

    metadata.create(resc_guid_2, discoverable_data_2, aliases=None, overwrite=True)

if __name__ == "__main__":
    main()
