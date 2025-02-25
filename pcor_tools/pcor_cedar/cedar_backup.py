import datetime
import json
import logging
import os.path
import shutil
import time

from pcor_cedar.cedar_access import CedarAccess
from pcor_cedar.cedar_config import CedarConfig

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s: %(filename)s:%(funcName)s:%(lineno)d: %(message)s"

)
logger = logging.getLogger(__name__)

"""
Backup of templates and curation activity, create a backup zip
"""
class CedarBackup():

    sleep_factor = 5

    def __init__(self):
        self.cedar_config = CedarConfig()
        self.cedar_access = CedarAccess()

    def backup(self, templates, instances, output):
        """
        Backup templates and curation activity, create an archive file
        in the target output directory

        Parameters
        ----------
        templates - URL to templates
        instances - URL to cedar curation instances
        output - file directory where an archive (zip) will be deposited

        Returns
        -------
        void

        """

        logger.info("backup template: %s \ninstances: %s \n to output: %s", templates, instances,
                    output)

        if not os.path.isdir(output):
            logger.error("output directory %s does not exist", output)
            raise Exception("output directory %s does not exist")

        iso_date = datetime.datetime.now().isoformat().replace('/', '_')

        # create a temp directory under the output directory, this will be zipped later and
        # then deleted

        temp_dir = os.path.join(output, "temp_" + iso_date)
        try:
            os.mkdir(temp_dir)
        except FileExistsError:
            pass

        logger.info("created temp dir: %s", temp_dir)

        templates_dir = os.path.join(temp_dir, "templates")
        logger.info("template dir: %s", templates_dir)
        try:
            os.mkdir(templates_dir)
        except FileExistsError:
            pass

        self.recursive_backup_templates(templates, templates_dir)

        instances_dir = os.path.join(temp_dir, "instances")
        logger.info("instances dir: %s", instances_dir)
        try:
            os.mkdir(instances_dir)
        except FileExistsError:
            pass

        self.recursive_backup(instances, instances_dir)

        # now zip it and delete the dir
        shutil.make_archive(os.path.join(output, "cedar_backup_" + iso_date), 'zip', temp_dir)
        os.removedirs(temp_dir)


    def recursive_backup(self, parent_folder_id,  temp_dir):
        time.sleep(CedarBackup.sleep_factor)
        folder_contents = self.cedar_access.retrieve_folder_contents(parent_folder_id)
        if folder_contents.subfolders:
            for entry in folder_contents.subfolders:
                if entry.item_type == 'folder':
                    subdir = os.path.join(temp_dir, entry.folder_name.replace('/', '_'))
                    try:
                        os.mkdir(subdir)
                    except FileExistsError:
                        pass
                    self.recursive_backup(CedarAccess.extract_guid(entry.folder_id), subdir)
                else:
                    time.sleep(CedarBackup.sleep_factor)
                    resource_file = self.cedar_access.retrieve_resource(CedarAccess.extract_guid(entry.folder_id))
                    with open(os.path.join(temp_dir,entry.folder_name.replace('/', '_') +'.json'), 'w') as f:
                        json.dump(resource_file, f)

    def recursive_backup_templates(self, parent_folder_id,  temp_dir):
        time.sleep(CedarBackup.sleep_factor)
        folder_contents = self.cedar_access.retrieve_folder_contents(parent_folder_id)
        if folder_contents.subfolders:
            for entry in folder_contents.subfolders:
                if entry.item_type == 'folder':
                    subdir = os.path.join(temp_dir, entry.folder_name.replace('/', '_'))
                    try:
                        os.mkdir(subdir)
                    except FileExistsError:
                        pass
                    self.recursive_backup(CedarAccess.extract_guid(entry.folder_id), subdir)
                else:
                    time.sleep(CedarBackup.sleep_factor)
                    resource_file = self.cedar_access.retrieve_template(CedarAccess.extract_guid(entry.folder_id))
                    with open(os.path.join(temp_dir,entry.folder_name.replace('/', '_') +'.json'), 'w') as f:
                        json.dump(resource_file, f)




