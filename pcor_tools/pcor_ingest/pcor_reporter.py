import logging
import json
import os

import requests
import smtplib, ssl
## email.mime subclasses
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
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
        template = self.env.get_template("error_report.html")
        rendered = template.render(data=pcor_processing_result)
        logger.info("rendered: %s" % rendered)
        return rendered

    def send_email_report(self, pcor_processing_result, email_text):
        email_message = MIMEMultipart()
        email_message['From'] = 'no-reply-niehs-pcor@nih.gov'
        email_message['To'] = pcor_processing_result.submitter_email
        email_message['Subject'] = 'PCOR Curation Report'

        # Attach the html doc defined earlier, as a MIMEText html content type to the MIME message
        email_message.attach(MIMEText(email_text, "html"))
        # Convert it as a string
        email_string = email_message.as_string()

        # Send the message via local SMTP server.
        s = smtplib.SMTP('smtp.niehs.nih.gov')
        s.starttls()
        # s.login(email_login,
        #        email_passwd)
        s.sendmail(email_message['From'], [email_message['To']], email_string)
        s.quit()



