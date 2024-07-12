# Step 1 - Import required packages
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
# Step 2 - Create message object instance

# Step 3 - Create message body

# Step 4 - Declare SMTP credentials
port = 587
# smtp_server = "sandbox.smtp.mailtrap.io"
# login = "cf0c4288b2c730"
# password = "47d6fe0fd312a4"

smtp_server = "live.smtp.mailtrap.io"
username = "api"
password = "3b4855ed9ae2c8b141fde7f33015da20"


sender_email = "mailtrap@demomailtrap.com"
# receiver_email = "dokib52052@kinsef.com"
receiver_email = "fminaseidiema26@gmail.com"

text = "Test from Python via AuthSMTP"

# Step 5 - Declare message elements
# msg = MIMEText(text, "plain")
# msg['Subject'] = "Plain Text Email"
# msg['From'] = sender_email
# msg['To'] = receiver_email

msg = f"""\
Subject: Hi Jerry
To: {receiver_email}
From: {sender_email}

This is a test e-mail message."""

with smtplib.SMTP(smtp_server, port) as server:
    server.starttls()
    server.login(username, password)
    server.sendmail(sender_email, receiver_email, msg)

print("Successfully sent email")


# Step 6 - Add the message body to the object instance
# msg.attach(MIMEText(message, 'plain'))

# Step 7 - Create the server connection
# server = smtplib.SMTP(smtphost)

# Step 8 - Switch the connection over to TLS encryption
# server.starttls()

# Step 9 - Authenticate with the server
# server.login(username, password)

# Step 10 - Send the message
# server.sendmail(msg['From'], msg['To'], msg.as_string())

# Step 11 - Disconnect
# server.quit()

# Step 12 -
# print("Successfully sent email message to %s:" % (msg['To'])


# with smtplib.SMTP('sandbox.smtp.mailtrap.io', 2525) as server:
#     server.starttls()
#     server.login("cf0c4288b2c730", "47d6fe0fd312a4")
#     server.sendmail(sender, receiver, message)
#     print("Successfully sent email message")


# MAIL_USERNAME=wpopping.ng@gmail.com
# MAIL_PASSWORD=riubbwzxypmpkftp
# MAIL_FROM=wpopping.ng@gmail.com
# MAIL_PORT=587
# MAIL_SERVER=smtp.gmail.com
# MAIL_FROM_NAME="What's Popping"
# TEMPLATE_FOLDER='app/templates'

#
# MAIL_USERNAME="api",
# MAIL_PASSWORD="3b4855ed9ae2c8b141fde7f33015da20",
# MAIL_FROM="mailtrap@demomailtrap.com",
# MAIL_PORT=587,
# MAIL_SERVER="live.smtp.mailtrap.io",
# MAIL_FROM_NAME="What's Popping",
# TEMPLATE_FOLDER = 'app/templates'