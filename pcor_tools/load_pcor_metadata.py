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
MANIFEST = "dbgap_extract_guid.tsv"
