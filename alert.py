from configuration import botAlert, mailConfig
import smtplib
from email.message import EmailMessage


class Mail:
    def send(self, subject, message):
        msg = EmailMessage()
        msg.set_content(message)

        msg['Subject'] = subject
        msg['From'] = mailConfig['from']
        msg['To'] = mailConfig['to']

        s = smtplib.SMTP(mailConfig['smtp'], mailConfig['port'], None, 3)
        s.login(mailConfig['username'], mailConfig['password'])

        try:
            s.send_message(msg)
            print('Sent alert "' + message + '" via email')
        finally:
            s.quit()


def alert(asset, message, isError=False):
    if botAlert == 'email':
        msg = EmailMessage()
        msg.set_content(message)

        if isError:
            subj = 'OPI Error'
        else:
            subj = 'OPI Alert'

        if asset:
            subj = subj + ', Asset: ' + asset

        mail = Mail()
        mail.send(subj, message)

        if isError:
            exit(1)
    else:
        if asset:
            print('Asset: ' + asset)

        print(message)

        if isError:
            exit(1)


def botFailed(asset, message):
    return alert(asset, message, True)
