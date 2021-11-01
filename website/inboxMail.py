import os
import email
import smtplib
from email import encoders
from email.header import decode_header
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from flask import Blueprint, render_template, redirect, request, flash, url_for
import imaplib

from .compose import sendMail
from .views import authenticate, server_add, port, context

inboxMail = Blueprint('inboxMail', __name__)


def clean(text):
    # clean text for creating a folder
    return "".join(c if c.isalnum() else "_" for c in text)


@inboxMail.route('/inbox', methods=['POST', 'GET'])
def inbox():
    if not authenticate():
        return redirect('/', display=False)

    user_info = open("user_details.txt", 'r')
    user_email = user_info.readline()
    password = user_info.readline()
    user_info.close()

    # Find the uids of all emails
    imap = imaplib.IMAP4_SSL("imap.gmail.com")
    imap.login(user_email, password)
    imap.select("INBOX")
    res, msg = imap.uid('search', None, "ALL")
    allUids = msg[0].decode()
    allUidsList = list(allUids.split())

    # Find the uids of unseen emails
    res, msg = imap.uid('search', None, "UNSEEN")
    allUnseenUids = msg[0].decode()
    allUnseenUidsList = list(allUnseenUids.split())

    uids = []
    senders = []
    subjects = []
    dates_sent = []
    isUnseen = []

    imap = imaplib.IMAP4_SSL("imap.gmail.com")
    imap.login(user_email, password)

    status, messages = imap.select("INBOX", readonly=True)
    # total number of emails
    messages = int(messages[0])

    # This is for search method
    if request.method == "POST":
        keyword = request.form['searchWord']
        flash("Showing search results for \'%s\'" % keyword, category='success')
        for i in range(messages, 0, -1):
            # fetch the email message by ID

            res, msg = imap.fetch(str(i), "(RFC822)")
            for response in msg:
                if isinstance(response, tuple):

                    # parse a bytes email into a message object
                    msg = email.message_from_bytes(response[1])

                    # decode the email subject
                    subject, encoding = decode_header(msg["Subject"])[0]
                    if isinstance(subject, bytes):
                        # if it's a bytes, decode to str
                        subject = subject.decode(encoding)

                    # decode email sender
                    From, encoding = decode_header(msg.get("From"))[0]
                    if isinstance(From, bytes):
                        From = From.decode(encoding)

                    date_sent = msg['Date']

                    if keyword in subject or keyword in From:
                        uids.append(i)
                        dates_sent.append(date_sent)
                        subjects.append(subject)
                        senders.append(email.utils.parseaddr(From)[0])

                    if allUidsList[i-1] in allUnseenUidsList:
                        isUnseen.append('unseen')
                    else:
                        isUnseen.append('seen')

    else:
        for i in range(messages, 0, -1):
            # fetch the email message by ID

            res, msg = imap.fetch(str(i), "(RFC822)")
            for response in msg:
                if isinstance(response, tuple):

                    # parse a bytes email into a message object
                    msg = email.message_from_bytes(response[1])

                    # decode the email subject
                    subject, encoding = decode_header(msg["Subject"])[0]
                    if isinstance(subject, bytes):
                        # if it's a bytes, decode to str
                        subject = subject.decode(encoding)

                    # decode email sender
                    From, encoding = decode_header(msg.get("From"))[0]
                    if isinstance(From, bytes):
                        From = From.decode(encoding)

                    date_sent = msg['Date']

                    uids.append(i)
                    dates_sent.append(date_sent)
                    subjects.append(subject)
                    senders.append(email.utils.parseaddr(From)[0])

                    if allUidsList[i - 1] in allUnseenUidsList:
                        isUnseen.append('unseen')
                    else:
                        isUnseen.append('seen')

    return render_template('inbox.html', display=True, senders=senders, uids=uids, subjects=subjects,
                           dates_sent=dates_sent, isUnseen=isUnseen)


@inboxMail.route('/view_email/<uid>', methods=['GET', 'POST'])
def view_email(uid):
    if not authenticate():
        return redirect('/', display=False)

    user_info = open("user_details.txt", 'r')
    user_email = user_info.readline()
    password = user_info.readline()
    user_info.close()

    imap = imaplib.IMAP4_SSL("imap.gmail.com")
    imap.login(user_email, password)
    user_emails = ""
    subject= ""
    From = ""
    date_sent = ""

    imap.select("INBOX")

    res, msg = imap.fetch(str(uid), "(RFC822)")
    for response in msg:
        if isinstance(response, tuple):
            # parse a bytes email into a message object
            msg = email.message_from_bytes(response[1])

            # decode the email subject
            subject, encoding = decode_header(msg["Subject"])[0]
            if isinstance(subject, bytes):
                # if it's a bytes, decode to str
                subject = subject.decode(encoding)

            # decode email sender
            From, encoding = decode_header(msg.get("From"))[0]
            if isinstance(From, bytes):
                From = From.decode(encoding)

            date_sent = msg['Date']

            # if the email message is multipart
            if msg.is_multipart():
                # iterate over email parts
                for part in msg.walk():
                    # extract content type of email
                    content_type = part.get_content_type()
                    content_disposition = str(part.get("Content-Disposition"))

                    if content_type == "text/plain" or content_type == "text/html" and "attachment" not in \
                            content_disposition:
                        user_emails = part.get_payload(decode=True).decode()
                    elif "attachment" in content_disposition:
                        # download attachment
                        filename = part.get_filename()
                        if filename:
                            folder_name = 'AttachedFiles'
                            if not os.path.isdir(folder_name):
                                # make a folder for this email.
                                os.mkdir(folder_name)
                            filepath = os.path.join(folder_name, filename)
                            # download attachment and save it
                            open(filepath, "wb").write(part.get_payload(decode=True))
                        flash('Find the attachments in the project folder.', category='success')
            else:
                user_emails = msg.get_payload(decode=True).decode()

    return render_template('view_email.html', display=True, subject=subject, date=date_sent, From=From,
                           emails=user_emails, uid=uid)


@inboxMail.route('/reply/<uid>', methods=['POST', 'GET'])
def reply(uid):
    if not authenticate():
        return redirect('/', display=False)

    if request.method == "POST":
        mess = MIMEMultipart()
        mess['To'] = request.form['to']
        mess['Subject'] = request.form['subject']

        user_info = open("user_details.txt", 'r')
        from_email = user_info.readline()
        user_info.close()

        mess['From'] = from_email
        message_body = MIMEText(request.form['message'], 'html', 'utf-8')
        message_body.add_header('Content-Disposition', 'text/html')

        mess.attach(message_body)

        image = request.files['attachment']
        filename = image.filename
        if filename != '':
            attachment = open(filename, 'rb')

            p = MIMEBase('application', 'octet-stream')
            p.set_payload(attachment.read())

            encoders.encode_base64(p)
            p.add_header('Content-Disposition', f'attachment; filename={filename}')
            mess.attach(p)
        return sendMail(mess)

    else:
        subject = ""
        sender = ""
        message = ""

        user_info = open("user_details.txt", 'r')
        user_email = user_info.readline()
        password = user_info.readline()
        user_info.close()

        imap = imaplib.IMAP4_SSL("imap.gmail.com")
        imap.login(user_email, password)

        imap.select("INBOX")

        res, msg = imap.fetch(str(uid), "(RFC822)")
        for response in msg:
            if isinstance(response, tuple):
                msg = email.message_from_bytes(response[1])

                subject, encoding = decode_header(msg["Subject"])[0]
                if isinstance(subject, bytes):
                    subject = subject.decode(encoding)

                sender, encoding = decode_header(msg.get("From"))[0]
                if isinstance(sender, bytes):
                    sender = sender.decode(encoding)

                if msg.is_multipart():
                    for part in msg.walk():
                        content_type = part.get_content_type()
                        content_disposition = str(part.get("Content-Disposition"))

                        if content_type == "text/plain" or content_type == "text/html" and "attachment" not in \
                                content_disposition:
                            message = part.get_payload(decode=True).decode()

                else:
                    message = (msg.get_payload(decode=True).decode())

        sender = email.utils.parseaddr(sender)[1]
        subject = "RE: " + subject

        imap.close()
        imap.logout()

        return render_template('compose.html', display=True, reply=True, sender=sender, message=message,
                               subject=subject,
                               uid=uid)


@inboxMail.route('/forward/<uid>', methods=['POST', 'GET'])
def forward(uid):
    if not authenticate():
        return redirect('/', display=False)

    if request.method == "POST":
        mess = MIMEMultipart()
        mess['To'] = request.form['to']
        mess['Subject'] = request.form['subject']

        user_info = open("user_details.txt", 'r')
        from_email = user_info.readline()
        user_info.close()

        mess['From'] = from_email
        message_body = MIMEText(request.form['message'], 'html', 'utf-8')
        message_body.add_header('Content-Disposition', 'text/html')

        mess.attach(message_body)

        image = request.files['attachment']
        filename = image.filename
        if filename != '':
            attachment = open(filename, 'rb')

            p = MIMEBase('application', 'octet-stream')
            p.set_payload(attachment.read())

            encoders.encode_base64(p)
            p.add_header('Content-Disposition', f'attachment; filename={filename}')
            mess.attach(p)
        return sendMail(mess)

    else:
        subject = ""
        message = ""

        user_info = open("user_details.txt", 'r')
        user_email = user_info.readline()
        password = user_info.readline()
        user_info.close()

        imap = imaplib.IMAP4_SSL("imap.gmail.com")
        imap.login(user_email, password)

        imap.select("INBOX")

        res, msg = imap.fetch(str(uid), "(RFC822)")
        for response in msg:
            if isinstance(response, tuple):
                msg = email.message_from_bytes(response[1])

                subject, encoding = decode_header(msg["Subject"])[0]
                if isinstance(subject, bytes):
                    subject = subject.decode(encoding)

                if msg.is_multipart():
                    for part in msg.walk():
                        content_type = part.get_content_type()
                        content_disposition = str(part.get("Content-Disposition"))

                        if content_type == "text/plain" or content_type == "text/html" and "attachment" not in \
                                content_disposition:
                            message = part.get_payload(decode=True).decode()

                else:
                    message = (msg.get_payload(decode=True).decode())

    subject = "FWD: " + subject
    return render_template('compose.html', display=True, forward=True, message=message, subject=subject, uid=uid)


@inboxMail.route('/delete/<uid>', methods=['POST', 'GET'])
def delete(uid):
    if not authenticate():
        return redirect('/', display=False)

    user_info = open("user_details.txt", 'r')
    user_email = user_info.readline()
    password = user_info.readline()
    user_info.close()

    imap = imaplib.IMAP4_SSL("imap.gmail.com")
    imap.login(user_email, password)
    imap.select("INBOX")

    res, msg = imap.uid('search', None, "ALL")
    uids = msg[0].decode()
    uidsList = list(uids.split())
    email_uid = uidsList[int(uid)-1]
    imap.uid('STORE', email_uid, '+X-GM-LABELS', '(\\Trash)')
    imap.expunge()
    imap.close()
    imap.logout()

    flash("Message deleted!", category="success")

    return redirect(url_for('inboxMail.inbox', display=True))
