import sys
import logging
import asyncio

from gen3.auth import Gen3Auth
from gen3.tools import metadata
from gen3.tools.metadata.ingest_manifest import manifest_row_parsers
from gen3.utils import get_or_create_event_loop_for_thread

logging.basicConfig(filename="output.log", level=logging.DEBUG)
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

# a file containing a "guid" column and additional, arbitrary columns to populate
# into the metadata service
MANIFEST = "test2.tsv"


def main():
    loop = get_or_create_event_loop_for_thread()

    auth = Gen3Auth(refresh_file="/Users/conwaymc/credentials-http.json")

    # must provide a str to namespace the metadata from the file in a block in
    # the metadata service
    metadata_source = "pcor"

    # (optional) override default guid parsing behavior
    def _custom_get_guid_for_row(commons_url, row, lock):
        """
        Given a row from the manifest, return the guid to use for the metadata object.

        Args:
            commons_url (str): root domain for commons where mds lives
            row (dict): column_name:row_value
            lock (asyncio.Semaphore): semaphones used to limit ammount of concurrent http
                connections if making a call to an external service

        Returns:
            str: guid
        """
        return row.get("guid") # OR row.get("some_other_column")

    # (optional) override default guid parsing behavior
    manifest_row_parsers["guid_for_row"] = _custom_get_guid_for_row

    loop.run_until_complete(
        metadata.async_ingest_metadata_manifest(
            auth.endpoint, manifest_file=MANIFEST, metadata_source=metadata_source, auth=auth
        )
    )


if __name__ == "__main__":
    main()
