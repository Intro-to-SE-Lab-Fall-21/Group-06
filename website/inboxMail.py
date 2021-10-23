from flask import Blueprint, render_template, flash, redirect, url_for
import imaplib

from .views import authenticate

inboxMail = Blueprint('inboxMail', __name__)


@inboxMail.route('/inbox', methods=['POST', 'GET'])
def inbox():
    if not authenticate():
        return redirect('/', display=False)

    user_info = open("user_details.txt", 'r')
    email = user_info.readline()
    password = user_info.readline()
    user_info.close()

    imap = imaplib.IMAP4_SSL("imap.gmail.com")

    imap.login(email, password)
    imap.select('Inbox')
    type, messages = imap.search(None, 'ALL')
    numEmails = len(messages[0].split())
    index = numEmails

    # if request.form.get('search'):
    #     search = request.form.get('search')  # requests the object with name 'search'
    #     loadInbox(search, index)
    #     search = None
    #
    # else:
    #     loadInbox(None, index)
    return render_template('inbox.html', display=True)
