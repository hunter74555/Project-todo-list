from flask_mail import Message
from extensions import mail
from flask import url_for

def send_confirmation_email(user_email, token):
    confirm_url = url_for(endpoint='auth.confirm_email', token=token, _external=True)
    html = f'''
    <p>Здравствуйте!</p>
    <p>Пожалуйста, подтвердите ваш email, перейдя по ссылке ниже:</p>
    <p><a href="{confirm_url}">{confirm_url}</a></p>
    <p>Если вы не регистрировались, просто проигнорируйте это письмо.</p>
    '''
    msg = Message(subject='Подтверждение email', recipients=[user_email], html=html)
    mail.send(msg)
