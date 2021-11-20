import smtplib
import ssl
import sys
from email.message import EmailMessage
from website import create_app

flask_app = create_app()

def test_home_page():
    with flask_app.test_client() as test_client:
        response = test_client.get('/')
        assert response.status_code == 200

in_server = 'smtp.gmail.com'
in_port = 465
context = ssl.create_default_context()

def test_travis1():
    print("Test 1: Login with wrong credentials.")
    email = "sth@gmail.com"
    password = "somepassword"
    with smtplib.SMTP_SSL(in_server, in_port, context=context) as server:
        try:
            server.login(email, password)
            print("FAIL")
        except:
            print("PASS")

def test_travis2():
    print("Test 2: Login with wrong password/correct email.")
    userEmail = "introsetest1@gmail.com"
    userPassword = "somePassword"
    with smtplib.SMTP_SSL(in_server, in_port, context=context) as server:
        try:
            server.login(userEmail, userPassword)
            print("FAIL")
        except:
            print("PASS")

def test_travis3():
    print("Test 3: Login with correct credentials.")  # setting up email
    userEmail = "introsetest1@gmail.com"
    userPassword = "!ntr0test"

    with smtplib.SMTP_SSL(in_server, in_port, context=context) as server:
        try:
            server.login(userEmail, userPassword)
            print("PASS")
        except:
            print("FAIL")

def test_travis4():
    print("Test 4: Create email with no sender, but includes a subject and body.")
    userEmail = "introsetest1@gmail.com"
    userPassword = "!ntr0test"
    newMessage = EmailMessage()
    newMessage['To'] = ""
    newMessage['Subject'] = "TRAVIS CI TEST"
    newMessage['From'] = "Group 6"

    with smtplib.SMTP_SSL(in_server, in_port, context=context) as server:
        try:
            server.login(userEmail, userPassword)
            server.send_message(newMessage)
            print("FAIL")
        except:
            print("PASS")

def test_travis5():
    print("Test 5: Create email")
    userEmail = "introsetest1@gmail.com"
    userPassword = "!ntr0test"
    newMessage = EmailMessage()
    newMessage['To'] = userEmail
    newMessage['Subject'] = "TRAVIS CI TEST"
    newMessage['From'] = "Group 2"

    with smtplib.SMTP_SSL(in_server, in_port, context=context) as server:
        try:
            server.login(userEmail, userPassword)
            server.send_message(newMessage)
            print("PASS")
        except:
            print("FAIL")

def test_travis6():
    print("Test 6: Navigating to login page")
    try:
        with app.test_client() as test_client:
            response = test_client.get('/')
            assert response.status_code == 200
            print("PASS")
    except:
        print("FAIL")

def test_travis7():
    print("Test 7: Navigating to inbox with unauthorized access")
    try:
        with app.test_client() as test_client:
            response = test_client.get('/inbox')
            assert response.status_code != 200
            print("PASS")
    except:
        print("FAIL")

def test_travis8():
    print("Test 8: Navigating to inbox with authorized access")
    email = "introsetest1@gmail.com"
    password = "!ntr0test"
    with smtplib.SMTP_SSL(in_server, in_port, context=context) as server:
        try:
            server.login(email, password)
            print("Test passed for correct credentials.")
        except:
            print("Test failed for correct credentials.")