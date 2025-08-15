import smtplib, ssl
import toml


def send_email(msg):
    port = 465  # For SSL
    smtp_server = "smtp.gmail.com"
    sender_email = "geoff.cluckcluck@gmail.com"  # Enter your address
    receiver_email = "geoff.dudds+cluckcluck@gmail.com"  # Enter receiver address
    secret = toml.load("secret.toml")
    password = secret["secrets"]["password"]

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, msg)
