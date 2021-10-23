import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from flask import Blueprint, render_template, redirect, request, url_for, flash

from .views import authenticate, server_add, port, context

compose = Blueprint('compose', __name__)


@compose.route('/compose', methods=['GET', 'POST'])
def composeMail():
    if not authenticate():
        return redirect('/', display=False)

    user_info = open("user_details.txt", 'r')
    email = user_info.readline()
    user_info.close()

    if request.method == "POST":
        message = MIMEMultipart()
        message['To'] = request.form['to']
        message['Subject'] = request.form['subject']
        message['From'] = email
        message_body = MIMEText(request.form['message'], 'html', 'utf-8')
        message_body.add_header('Content-Disposition', 'text/html')

        message.attach(message_body)

        image = request.files['attachment']
        filename = image.filename
        if filename != '':
            attachment = open(filename, 'rb')

            p = MIMEBase('application', 'octet-stream')
            p.set_payload(attachment.read())

            encoders.encode_base64(p)
            p.add_header('Content-Disposition', f'attachment; filename={filename}')
            message.attach(p)
        return sendMail(message)

    else:
        return render_template("compose.html", display=True)


def sendMail(message):
    user_info = open("user_details.txt", 'r')
    email = user_info.readline()
    password = user_info.readline()
    user_info.close()

    with smtplib.SMTP_SSL(server_add, port, context=context) as server:
        server.login(email, password)
        server.send_message(message)
        flash('Message Sent!', category='success')
    return redirect(url_for('inboxMail.inbox', display=True))
