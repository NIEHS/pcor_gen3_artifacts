import logging
import os
import smtplib
import traceback
import warnings
import pandas as pd
from pcor_ingest.population_data_resource_parser import PcorTemplateParser
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from jinja2 import Environment, FileSystemLoader
from pcor_ingest.pcor_intermediate_model import PcorSubmissionInfoModel

logger = logging.getLogger(__name__)


class PcorReporter():
    """
        Format PCOR curation status response/errors into HTML format
    """

    def __init__(self, pcor_ingest_configuration):
        """
        sets up required components
        :param pcor_ingest_configuration:
        """
        self.pcor_ingest_configuration = pcor_ingest_configuration

        # Get the directory of the script
        script_dir = os.path.dirname(os.path.abspath(__file__))

        # Set the relative path to your template directory
        template_rel_path = 'templates'

        # Construct the absolute path to the template directory
        template_dir = os.path.join(script_dir, template_rel_path)
        logger.info('template_dir: %s' % template_dir)

        # Create a Jinja environment with the FileSystemLoader
        self.env = Environment(loader=FileSystemLoader(template_dir))

    def report(self, pcor_processing_result):  # TODO: how would we respond back (JSON?) to an endpoint
        """
        Main method will format report and send based on the processing result
        :param pcor_processing_result: PcorProcessResult
        :return: void
        """

        if pcor_processing_result.success:
            msg = self.produce_html_success_report(pcor_processing_result)
            self.send_email_report(pcor_processing_result=pcor_processing_result, email_text=msg, status='SUCCESS')
        else:
            msg = self.produce_html_error_report(pcor_processing_result)
            self.send_email_report(pcor_processing_result=pcor_processing_result, email_text=msg, status='FAILED')

    def produce_html_error_report(self, pcor_processing_result):

        """
        Produce the html report showing an error in curating pcor data
        :param pcor_processing_result: PcorProcessResult result data structure
        :return: html error report
        """
        logger.info("produce_html_report()")
        template = self.env.get_template("error_report.html")
        template.globals['now'] = datetime.utcnow
        submission = pcor_processing_result.model_data.get("submission")

        if not submission:
            warnings.simplefilter(action='ignore', category=UserWarning)
            df = pd.read_excel(pcor_processing_result.template_current_location, sheet_name=0)
            submission = PcorTemplateParser.extract_submission_data(df)
            pcor_processing_result.model_data["submission"] = submission

        rendered = template.render(data=pcor_processing_result,
                                   submission=submission)
        return rendered

    def produce_html_success_report(self, pcor_processing_result):

        """
        Produce the html report showing success in curating pcor data
        :param pcor_processing_result: PcorProcessResult result data structure
        :return: html error report
        """
        logger.info("produce_html_report()")
        template = self.env.get_template("success_report.html")
        template.globals['now'] = datetime.utcnow
        submission = pcor_processing_result.model_data["submission"]

        if not submission:
            warnings.simplefilter(action='ignore', category=UserWarning)
            df = pd.read_excel(pcor_processing_result.template_current_location, sheet_name=0)
            submission = PcorTemplateParser.extract_submission_data(df)
            pcor_processing_result.model_data["submission"] = submission

        rendered = template.render(data=pcor_processing_result,
                                   submission=submission)
        return rendered

    def send_email_report(self, pcor_processing_result, email_text, status=None):
        try:
            logger.info('send_email_report()')
            email_message = MIMEMultipart()
            email_message['From'] = self.pcor_ingest_configuration.mail_from
            recipients = ['mike.conway@nih.gov', 'deep.patel@nih.gov', 'april.graves@nih.gov']
            submission = pcor_processing_result.model_data["submission"]
            if submission.curator_email and self.pcor_ingest_configuration.mail_send_curator_email:
                recipients.append(submission.curator_email)

            email_message['To'] = ", ".join(recipients)

            email_message['Subject'] = '(' + status + ')CHORDS Curation Report'

            # Attach the html doc defined earlier, as a MIMEText html content type to the MIME message
            email_message.attach(MIMEText(email_text, "html"))
            # Convert it as a string
            email_string = email_message.as_string()

            # Send the message via local SMTP server.
            logger.info('Initializing SMTP connection....')
            s = smtplib.SMTP(self.pcor_ingest_configuration.smtp_server)
            s.starttls()
            # s.login(email_login,
            #        email_passwd)
            s.send_message(email_message)
            s.quit()
        except Exception as e:
            logger.info('Error sending email report: %s', e)
            # Log the stack trace
            stack_trace = traceback.format_exc()
            logger.error('Stack Trace: %s', stack_trace)
