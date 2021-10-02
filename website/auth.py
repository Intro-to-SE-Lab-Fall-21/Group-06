from flask import Blueprint, render_template, request, flash, redirect, url_for
import smtplib

auth = Blueprint('auth', __name__)
server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
flag = False


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        try:
            server.login(email, password)
            flag = True
            flash('Logged in successfully!', category='success')

            return redirect(url_for('views.home'))
        except smtplib.SMTPServerDisconnected:
            flash('Server Disconnected, try again.', category='error')
        except smtplib.SMTPAuthenticationError:
            flash('Authentication Error!', category='error')

    return render_template("login.html", boolean=True)


@auth.route('/logout')
def logout():
    try:
        server.quit()
        flag = False
        flash('Logged Out Successfully.', category='success')
    except smtplib.SMTPServerDisconnected:
        flash('No session detected.', category='error')

    return redirect(url_for('auth.login'))
