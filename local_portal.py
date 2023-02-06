"""
This script will start the data portal locally in development mode using 
the configured gitops and schema

"""
import json
import os
import sys
import logging
import argparse
import shutil

LOCAL_PORTAL_DNS_NAME = "pcor.local"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s: %(filename)s:%(funcName)s: %(message)s"
)

logger = logging.getLogger(__name__)


def run_local(portal_dir, pcor_artifacts, cdismanifest=LOCAL_PORTAL_DNS_NAME):
    logging.info("run local")
    logging.info("portal_dir:%s" % portal_dir)
    logging.info("cdismanifest:%s" % cdismanifest)
    logging.info("pcor_artifacts:%s" % pcor_artifacts)

    # move gitops to portal folder
    shutil.copy2(pcor_artifacts+'/custom_configs/gitops.json', pcor_artifacts + "/" + cdismanifest + "/portal/gitops.json")

    

def main():
    logging.info("startup")
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataportal", help="local parent directory for the data portal repo", default="/Users/conwaymc/Documents/workspace-pcor/data-portal")
    parser.add_argument("--cdismanifest", help="local parent directory for cdis manfifest", default=LOCAL_PORTAL_DNS_NAME)
    parser.add_argument("--pcorartifacts", help="local parent directory for pcorartifacts", default="/Users/conwaymc/Documents/workspace-pcor/pcor_gen3_artifacts")

    args = parser.parse_args()

   
    portal_dir = args.dataportal
    cdismanifest = args.cdismanifest
    pcor_artifacts = args.pcorartifacts

    
    logger.debug("portal_dir:%s" % portal_dir)
    logger.debug("cdismanifest:%s" % cdismanifest)
    logger.debug("pcor_artifacts:%s" % pcor_artifacts)

    run_local(portal_dir=portal_dir, pcor_artifacts=pcor_artifacts, cdismanifest=cdismanifest)


if __name__ == "__main__":
    main()