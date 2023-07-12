import email.message
import smtplib

msg = email.message.Message()
msg['Subject'] = 'foo'
msg['From'] = 'mike.conway@nih.gov'
msg['To'] = 'mike.conway@nih.gov'
msg.add_header('Content-Type','text/html')
msg.set_payload('Body of <b>message</b>')

# Send the message via local SMTP server.
s = smtplib.SMTP('smtp.niehs.nih.gov')
s.starttls()
#s.login(email_login,
#        email_passwd)
s.sendmail(msg['From'], [msg['To']], msg.as_string())
s.quit()

# see: https://stackoverflow.com/questions/882712/send-html-emails-with-python