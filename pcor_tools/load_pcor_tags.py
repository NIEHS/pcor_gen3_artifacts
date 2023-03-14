import json

import sys
import logging
import asyncio

from gen3.auth import Gen3Auth
from gen3.metadata import Gen3Metadata
from gen3.tools import metadata
from gen3.tools.metadata.ingest_manifest import manifest_row_parsers
from gen3.utils import get_or_create_event_loop_for_thread

logging.basicConfig(filename="output.log", level=logging.DEBUG)
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

# a file containing a "guid" column and additional, arbitrary columns to populate
# into the metadata service
MANIFEST = "test2.json"


def main():
    loop = get_or_create_event_loop_for_thread()

    # auth = Gen3Auth(refresh_file="/Users/pateldes/.gen3/credentials-local.json")
    auth = Gen3Auth(refresh_file="/Users/conwaymc/credentials-http.json")

    # must provide a str to namespace the metadata from the file in a block in
    # the metadata service
    metadata_source = "pcor"
    resc_guid ="75964cb1-9d8e-45bd-a7db-14f529aca591"
    f = open(MANIFEST, "r")

    # Reading from file
    gen3_discovery = json.loads(f.read())
    discoverable_data = dict(_guid_type="discovery_metadata", gen3_discovery=gen3_discovery)

    metadata = Gen3Metadata(auth)
    metadata.admin_endpoint = "http://localhost"
    metadata.create(resc_guid,discoverable_data, aliases=None, overwrite=True)


if __name__ == "__main__":
    main()
