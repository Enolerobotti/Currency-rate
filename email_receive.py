import easyimap
from getpass import getpass

def check_mail(bot_login, bot_password, sender_login):
    try:
        imapper = easyimap.connect('imap.gmail.com', bot_login, bot_password)
    except:
        pass
    for mail_id in imapper.listids(limit=100):
        mail = imapper.mail(mail_id)
        if sender_login in mail.from_addr:
            yield mail.body
            
def get_mail_bodies(bot_login, bot_password, sender_login):
    return [body for body in check_mail(bot_login, bot_password, sender_login)]

if __name__ == "__main__":
    bot_login = "bot@gmail.com"
    sender_login='user@gmail.com'
    bot_password = getpass(prompt='Bot password: ', stream=None)
    the_last_email=next(check_mail(bot_login, bot_password, sender_login))        
    mails = get_mail_bodies(bot_login, bot_password, sender_login)            