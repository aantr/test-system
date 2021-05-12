import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from global_app import get_app

server = None
ready = False
app = None


def test_email():
    global ready
    global app
    app = get_app()
    server = smtplib.SMTP_SSL(app.config['MAIL_HOST'], app.config['MAIL_PORT'])
    if type(app.config['MAIL_LOGIN']) == str:
        server.login(app.config['MAIL_LOGIN'], app.config['MAIL_PASSWORD'])
        ready = True
    else:
        print('Warning: Setup mail login and password')
    server.ehlo()


def send_mail(from_, to_, subject, text, html):
    if not ready:
        return
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = from_
    msg['To'] = to_

    part1 = MIMEText(text, 'plain')
    part2 = MIMEText(html, 'html')

    msg.attach(part1)
    msg.attach(part2)

    server.sendmail(from_, to_, msg.as_string())
