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
template_file = "templates/template.jinja"


def main():

    # auth = Gen3Auth(refresh_file="/Users/pateldes/.gen3/credentials-local.json")
    auth = Gen3Auth(refresh_file="/Users/conwaymc/credentials-http.json")

    # must provide a str to namespace the metadata from the file in a block in
    # the metadata service
    metadata_source = "pcor"
    resc_guid ="75964cb1-9d8e-45bd-a7db-14f529aca591"

    env = Environment(loader=PackageLoader("load_pcor_via_template"))
    env.filters['jsonify'] = json.dumps


    tags = [{"name": "resource", "category": "Resource"},
            {"name": "md_foo", "category": "Fubar Metadata"},
            {"name": "md_bar", "category": "Fubar Location"}]

    name = "Wildfire"
    full_name = "wildfire stuff"
    description = "its a wildfire, I mean, look out"
    resource_id = "75964cb1-9d8e-45bd-a7db-14f529aca591"

    template = env.get_template("template.jinja")
    content = template.render(tags=tags, resource_name=name, resource_full_name=full_name, resource_description=description, resource_id=resource_id)

    # Reading from file
    gen3_discovery = json.loads(content)
    discoverable_data = dict(_guid_type="discovery_metadata", gen3_discovery=gen3_discovery)

    metadata = Gen3Metadata(auth)
    #metadata.admin_endpoint = "http://localhost"
    metadata.create(resc_guid,discoverable_data, aliases=None, overwrite=True)


if __name__ == "__main__":
    main()
