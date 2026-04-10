import smtplib
import pandas as pd

import os
import random
import time
import datetime
import numpy as np
import mimetypes
from email.mime.text import MIMEText
import email
import email.mime.application
import email.mime.multipart
import logging

import modules.constants.main as const
import modules.database.database as db


# CHECK: re route to csv tools or utilities
# from bcc_bot import update_log
# from bcc_bot import fixing_df_bis


class SMTP():
    """
    This class handles everything related to sending out emails through smtp connection
    """

    def __init__(self, email_account):

        self.footer_path = const.FOOTER_PATH
        self.mm_list_path = const.MM_READY_CSV
        self.from_name = 'Ruth Stanat'
        self.host = const.SMTP_HOST
        self.port = const.SMTP_PORT
        self.email = email_account
        self.password = const.GODADDY_PASSWORD
        self.mailserver = smtplib.SMTP(self.host, self.port)
        try:
            self.mailserver.starttls()
            self.mailserver.ehlo()
            self.mailserver.login(self.email, self.password)
        except smtplib.SMTPException as e:
            self.mailserver.quit()
            raise RuntimeError('Failed connecting to %s' % self.email) from e

    def create_mail_msg_object(self, message, to_email):
        """
        Creates a email.message object so be sent through SMTP
        """

        from_string = '{0} <{1}>'.format(self.from_name, self.email)

        msg = MIMEText(message.split('\n',1)[1])
        msg.set_unixfrom('author')
        msg['From'] = from_string
        msg['To'] = to_email
        msg['Subject'] = message.split('\n',1)[0]

        return msg

    def create_mail_msg_with_attachment(self, message, to_email, attachment_path):

        from_string = '{0} <{1}>'.format(self.from_name, self.email)

        # Create a text/plain message
        msg = email.mime.multipart.MIMEMultipart()
        msg['Subject'] = message.split('\n',1)[0]
        msg['From'] = from_string
        msg['To'] = to_email

        # The main body is just another attachment
        body = MIMEText(message.split('\n',1)[1])
        msg.attach(body)

        # PDF attachment
        with open(attachment_path, 'rb') as fp:
            att = email.mime.application.MIMEApplication(fp.read(), _subtype="pdf")
        att.add_header('Content-Disposition', 'attachment', filename=os.path.basename(attachment_path))
        msg.attach(att)

        return msg

    def update_log(self, df):
        df = df[['Email','project_number','status','timestamp']]
        log_path = const.LOG_PATH
        df_log = pd.read_csv(log_path)

        df_log = pd.concat([df_log,df], ignore_index=True)
        df_log.to_csv(log_path, index=False)

    def fixing_df_bis(self, list_filename):
        df = pd.read_csv(list_filename)
        mailing_list = df.to_dict('records')
        return mailing_list

    def send_emails_smtp(self, email_id, remaining):
        """
        Fixes the message adding the footer to it
        Loops over the mailing list and sends out an email per record
        """

        today = datetime.date.today()

        # The following line is not needed as we don't want to slice the csv anymore
        mailing_list = self.fixing_df_bis(self.mm_list_path)          # This function reads a csv as a dataframe and then turns it into a dict
        mailing_list = mailing_list[:int(remaining)]
        new_df = pd.DataFrame(mailing_list)                     # which seems unecessary if I'm turning it into a DF back again here
        new_df['timestamp'] = today

        with open(self.footer_path, 'r', encoding='utf-8') as file:
            footer = file.read()
        footer = footer.format(FROM_NAME=self.from_name)

        # This loop is what actually sends out the mails
        n = 1
        try:
            for mail in mailing_list:
                message_1 = mail['message'] + '\n\n' + footer
                msg = self.create_mail_msg_object(message_1, mail['Email'])

                df_index = new_df[new_df['Email'] == mail['Email']].index

                try:
                    self.mailserver.sendmail(msg['From'], msg['To'], msg.as_string())
                    db.update_smtp_counters(email_id)
                    db.update_project_recruits_last_mm_sent(mail['project_id'], mail['id'])

                    new_df.loc[df_index, 'status'] = 'sent'

                except smtplib.SMTPRecipientsRefused:
                    logging.warning('Recipient refused for record id=%s', mail.get('id'))
                    new_df.loc[df_index, 'status'] = 'failed'

                except Exception as e:
                    logging.error('Unexpected error sending to record id=%s: %s', mail.get('id'), e)
                    new_df.loc[df_index, 'status'] = 'failed'

                wait_time = random.randint(1, 6)
                logging.info('Email sent. Total sent in session: %d', n)
                time.sleep(wait_time)
                n += 1
        finally:
            self.mailserver.quit()
            if os.path.exists(self.mm_list_path):
                os.remove(self.mm_list_path)
