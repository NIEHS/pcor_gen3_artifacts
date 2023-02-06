"""
This script will start the data portal locally in development mode using 
the configured gitops and schema

"""
import json
import os
import sys
import logging
import argparse

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s: %(filename)s:%(funcName)s: %(message)s"
)

logger = logging.getLogger(__name__)

def run_local(portal_dir, cdismanifest, pcor_artifacts):
    logging.info("run local")
    logging.info("portal_dir:%s" % portal_dir)
    logging.info("cdismanifest:%s" % cdismanifest)
    logging.info("pcor_artifacts:%s" % pcor_artifacts)
    

def main():
    logging.info("startup")
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataportal", help="local parent directory for the data portal repo")
    parser.add_argument("--cdismanifest", help="local parent directory for cdis manfiest")
    parser.add_argument("--pcorartifacts", help="local parent directory for pcorartifacts")

    args = parser.parse_args()

   
    portal_dir = args.dataportal
    cdismanifest = args.cdismanifest
    pcor_artifacts = args.pcorartifacts

    
    logger.debug("portal_dir:%s" % portal_dir)
    logger.debug("cdismanifest:%s" % cdismanifest)
    logger.debug("pcor_artifacts:%s" % pcor_artifacts)


if __name__ == "__main__":
    main()