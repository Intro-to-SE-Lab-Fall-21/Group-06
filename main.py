from website import create_app

app = create_app()


def test_home_page():
    with app.test_client() as test_client:
        response = test_client.get('/')
        assert response.status_code == 200


def test_inbox_unauthorized():
    with app.test_client() as test_client:
        response = test_client.get('/inbox')
        assert response.status_code == 302


def test_inbox_authorized():
    email = "introsetest1@gmail.com"
    password = "!ntr0test"
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        try:
            server.login(email, password)
            print("Test passed for correct credentials.")
        except:
            print("Test failed for correct credentials.")


def test_wrong_credentials():
    email = "sth@gmail.com"
    password = "somepassword"
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        try:
            server.login(email, password)
            print("Test failed for wrong credentials.")
        except:
            print("Test passed for wrong credentials.")
            
if __name__ == '__main__':
    app.run(debug=True)
