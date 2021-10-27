import os
import email
from email.header import decode_header
from flask import Blueprint, render_template, redirect, request
import imaplib
from .views import authenticate

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

    imap = imaplib.IMAP4_SSL("imap.gmail.com")
    imap.login(user_email, password)

    uids = []
    senders = []
    subjects = []
    dates_sent = []

    status, messages = imap.select("INBOX")
    # total number of emails
    messages = int(messages[0])

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

    return render_template('inbox.html', display=True, senders=senders, uids=uids, subjects=subjects,
                           dates_sent=dates_sent)


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
                    try:
                        # get the email body
                        user_emails = part.get_payload(decode=True).decode()
                    except:
                        pass
                    if "attachment" in content_disposition:
                        # download attachment
                        filename = part.get_filename()
                        if filename:
                            folder_name = 'AttachedFiles'
                            if not os.path.isdir(folder_name):
                                # make a folder for this email (named after the subject)
                                os.mkdir(folder_name)
                            filepath = os.path.join(folder_name, filename)
                            # download attachment and save it
                            open(filepath, "wb").write(part.get_payload(decode=True))
            else:
                user_emails = (msg.get_payload(decode=True).decode())

    return render_template('view_email.html', display=True, subject=subject, date=date_sent, From=From, emails=user_emails, uid=uid)


@inboxMail.route('/reply/<uid>', methods=['POST', 'GET'])
def reply(uid):
    if not authenticate():
        return redirect('/', display=False)

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
                sender = email.utils.parseaddr(sender)[1]
                print(sender)

            if msg.is_multipart():
                for part in msg.walk():
                    try:
                        message = part.get_payload(decode=True).decode()
                    except:
                        pass
            else:
                message = (msg.get_payload(decode=True).decode())

    sender = email.utils.parseaddr(sender)[1]
    subject = "RE: " + subject
    return render_template('compose.html', display=True, reply=True, sender=sender, message=message, subject=subject, uid=uid)


@inboxMail.route('/forward/<uid>', methods=['POST', 'GET'])
def forward(uid):
    if not authenticate():
        return redirect('/', display=False)

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
                    try:
                        message = part.get_payload(decode=True).decode()
                    except:
                        pass
            else:
                message = (msg.get_payload(decode=True).decode())

    subject = "FWD: " + subject
    return render_template('compose.html', display=True, forward=True, message=message, subject=subject, uid=uid)


@inboxMail.route('/search', methods=['POST', 'GET'])
def search():
    if not authenticate():
        return redirect('/', display=False)

    keyword = request.form.get['searchWord']

    print("test :")
    print(keyword)
    user_info = open("user_details.txt", 'r')
    user_email = user_info.readline()
    password = user_info.readline()
    user_info.close()

    imap = imaplib.IMAP4_SSL("imap.gmail.com")
    imap.login(user_email, password)

    uids = []
    senders = []
    subjects = []
    dates_sent = []

    status, messages = imap.select("INBOX")
    # total number of emails
    messages = int(messages[0])

    for i in range(messages, 0, -1):
        # fetch the email message by ID

        res, msg = imap.fetch(str(i), 'TEXT "{}",keyword')
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

    return render_template('inbox.html', display=True, senders=senders, uids=uids, subjects=subjects,
                           dates_sent=dates_sent)
