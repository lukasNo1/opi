from configuration import botErrorAlert, mailConfig
import smtplib
from email.message import EmailMessage


def botFailed(asset, message):
    if botErrorAlert == 'email':
        msg = EmailMessage()
        msg.set_content(message)

        subj = 'OPI Error'

        if asset:
            subj = subj+', Asset: ' + asset

        msg['Subject'] = subj
        msg['From'] = mailConfig['from']
        msg['To'] = mailConfig['to']

        s = smtplib.SMTP(mailConfig['smtp'], mailConfig['port'], None, 3)
        s.login(mailConfig['username'], mailConfig['password'])

        try:
            s.send_message(msg)
            print('Sent error "'+message+'" via email')
        finally:
            s.quit()

        exit(1)
    else:
        if asset:
            print('Asset: ' + asset)

        print(message)
        exit(1)
