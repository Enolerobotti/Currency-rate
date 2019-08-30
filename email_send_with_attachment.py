import smtplib, ssl

from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from getpass import getpass

def send_message_with_attachment(bot_email, bot_password, user_email, subject, body, filename):
    # Create a multipart message and set headers
    message = MIMEMultipart()
    message["From"] = bot_email
    message["To"] = user_email
    message["Subject"] = subject
    #message["Bcc"] = user_email  # Recommended for mass emails
    
    # Add body to email
    message.attach(MIMEText(body, "plain"))
    


    # Open PDF file in binary mode
    with open(filename, "rb") as attachment:
        # Add file as application/octet-stream
        # Email client can usually download this automatically as attachment
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())
        
        # Encode file in ASCII characters to send by email    
        encoders.encode_base64(part)

    # Add header as key/value pair to attachment part
    part.add_header(
            "Content-Disposition",
            f"attachment; filename= {filename}",
            )

    # Add attachment to message and convert message to string
    message.attach(part)
    text = message.as_string()
    
    # Log in to server using secure context and send email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(bot_email, bot_password)
        server.sendmail(bot_email, user_email, text)

if __name__ == "__main__":    
    subject0 = "An email with attachment from Python"
    body0 = "This is an email with attachment sent from Python"
    bot_email0 = "bot@gmail.com"
    bot_password0 = getpass(prompt='Bot password: ', stream=None)
    user_email0 = "user@gmail.com"
    filename0 = "plot.pdf"  # In same directory as script
    send_message_with_attachment(bot_email0, bot_password0, user_email0, subject0, body0, filename0)