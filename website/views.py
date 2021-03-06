from flask import Blueprint, render_template, request, flash, redirect, url_for
import smtplib
import ssl

from flask_login import logout_user

views = Blueprint('views', __name__)
server_add = 'smtp.gmail.com'
port = 465
server = smtplib.SMTP_SSL(server_add, port)
context = ssl.create_default_context()


@views.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get the inputs from the webapp
        email = request.form.get('email')
        password = request.form.get('password')

        # Create a text file and store the credentials.
        user_info = open('user_details.txt', 'w')
        user_info.write(email + "\n")
        user_info.write(password + "\n")
        user_info.close()

        if authenticate():
            flash('Logged in successfully!', category='success')
            return redirect(url_for('inboxMail.inbox', display=True))
        elif email == '' or password == '':
            flash('Input required for both fields.', category='error')
        else:
            flash('Wrong Credentials Entered. Try Again!', category='error')

    return render_template('login.html', display=False)


@views.route('/logout')
def logout():
    file = open('user_details.txt', 'r+')
    file.truncate(0)
    file.close()
    flash('Logged Out Successfully.', category='success')

    # return render_template("login.html")
    return redirect(url_for('views.login', display=False))


def authenticate():
    user_info = open("user_details.txt", 'r')
    userEmail = user_info.readline()
    userPassword = user_info.readline()
    user_info.close()

    with smtplib.SMTP_SSL(server_add, port, context=context) as server:
        try:
            server.login(userEmail, userPassword)
            return True
        except smtplib.SMTPAuthenticationError:
            return False
