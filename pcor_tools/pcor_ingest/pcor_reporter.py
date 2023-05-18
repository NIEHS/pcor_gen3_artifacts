import logging
import json
import os

import requests
import email.message
import smtplib

from jinja2 import Environment, PackageLoader, select_autoescape

from pcor_ingest.pcor_intermediate_model import PcorIntermediateProjectModel
logger = logging.getLogger(__name__)


class PcorReporter():

    """
        Format PCOR curation status response/errors into HTML format
    """

    def __init__(self):
        self.env = Environment(loader=PackageLoader('pcor_ingest', 'templates'))

    def produce_html_error_report(self, pcor_processing_result):

        """
        Produce the html report showing an error in curating pcor data
        :param pcor_processing_result: PcorProcessResult result data structure
        :return: html error report
        """
        logger.info("produce_html_report()")
        template = self.env.get_template("error_report.jinja")
        rendered = template.render(data=pcor_processing_result)
        logger.info("rendered: %s" % rendered)
        return rendered

    def send_email_report(self, email_text):
        msg = email.message.Message()
        msg['Subject'] = 'PCOR Curation Report'
        msg['From'] = 'no-reply-niehs-pcor@nih.gov'
        msg['To'] = 'mike.conway@nih.gov'
        msg.add_header('Content-Type', 'text/html')
        msg.set_payload(email_text)

        # Send the message via local SMTP server.
        s = smtplib.SMTP('smtp.niehs.nih.gov')
        s.starttls()
        # s.login(email_login,
        #        email_passwd)
        s.sendmail(msg['From'], [msg['To']], msg.as_string())
        s.quit()



