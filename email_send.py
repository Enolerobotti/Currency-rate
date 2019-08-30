import smtplib, ssl
from getpass import getpass

def send_email(bot_email, bot_password, receiver_email, message):   
    port = 465  # For SSL
    smtp_server = "smtp.gmail.com"
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(bot_email, bot_password)
        server.sendmail(bot_email, receiver_email, message)
    


if __name__ == "__main__":
    bot_email = "bot@gmail.com"  
    receiver_email = "user@gmail.com"
    bot_password = getpass(prompt='Bot password: ', stream=None) 
    message = "Subject: Hi there again2\n\nWhat's up? This message is sent from Python."
    send_email(bot_email, bot_password, receiver_email, message)