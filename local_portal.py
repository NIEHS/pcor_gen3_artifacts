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

LOCAL_PORTAL_DNS_NAME = "localhost"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s: %(filename)s:%(funcName)s: %(message)s"
)

logger = logging.getLogger(__name__)


def setup_and_run(portal_dir, pcor_artifacts, hostname=LOCAL_PORTAL_DNS_NAME, runit=False):
    logging.info("run local")
    logging.info("portal_dir:%s" % portal_dir)
    logging.info("hostname:%s" % hostname)
    logging.info("pcor_artifacts:%s" % pcor_artifacts)
    logging.info("runit:%s" % runit)
    # assume that a common parent folder sits above data_portal and pcor_gen3_artifacts, will put cdis-manifest under common parent
    os.chdir(pcor_artifacts)
    os.chdir("..")
    parent_dir = os.getcwd()
    logger.info("parent dir is:%s" % parent_dir)

    try:
        os.makedirs(parent_dir + "/cdis-manifest/" + hostname + "/portal", exist_ok=True)
    except OSError as error:
        print(error)

        # move gitops and manifest to cdis manifest
    shutil.copy2(pcor_artifacts+'/custom_configs/gitops.json', parent_dir + "/cdis-manifest/" + hostname + "/portal/gitops.json")
    shutil.copy2(pcor_artifacts+'/custom_configs/manifest.json', parent_dir + "/cdis-manifest/" + hostname + "/manifest.json")
    # copy schema.json to data
    shutil.copy2(pcor_artifacts+'/custom_configs/schema.json', portal_dir + "/data/schema.json")

    if not runit:
        logger.info("not running, all done!")
        exit(0)

    logger.info("running npm ci")
    os.chdir(portal_dir)
    os.system("pwd")
    #os.system("npm ci ")
    os.system("HOSTNAME=" + hostname + " NODE_ENV=auto bash ./runWebpack.sh")

    
def main():
    logging.info("startup")
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataportal", help="local parent directory for the data portal repo", default="/Users/conwaymc/Documents/workspace-pcor/data-portal")
    parser.add_argument("--hostname", help="hostname to find in cdis-manifest", default=LOCAL_PORTAL_DNS_NAME)
    parser.add_argument("--pcorartifacts", help="local parent directory for pcorartifacts", default="/Users/conwaymc/Documents/workspace-pcor/pcor_gen3_artifacts")
    parser.add_argument("--run", help="flag indicates that the portal should be started", default=True)

    args = parser.parse_args()
    portal_dir = args.dataportal
    hostname = args.hostname
    pcor_artifacts = args.pcorartifacts
    runit = args.run
    
    logger.info("portal_dir:%s" % portal_dir)
    logger.info("hostname:%s" % hostname)
    logger.info("pcor_artifacts:%s" % pcor_artifacts)
    logger.info("runit:%s" % runit)

    setup_and_run(portal_dir=portal_dir, pcor_artifacts=pcor_artifacts, hostname=hostname, runit=runit)




if __name__ == "__main__":
    main()