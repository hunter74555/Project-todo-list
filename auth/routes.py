from flask import render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from extensions import db, login_manager
from models import User
from . import auth_bp
import re
from utils.email_utils import domain_has_mx
from auth.tokens import generate_confirmation_token, confirm_token
from auth.email_utils import send_confirmation_email
import time

EMAIL_REGEX = r'^[\w\.-]+@[\w\.-]+\.\w+$'


@auth_bp.route('/please_confirm')
def please_confirm():
    return render_template('please_confirm.html')

@auth_bp.route('/resend_confirmation', methods=['POST'])
def resend_confirmation():
    email = session.get('unconfirmed_email')

    if not email:
        flash('Не удалось определить email для повторной отправки.', 'error')
        return redirect(url_for('auth.login'))

    last_sent = session.get('last_confirmation_sent', 0)
    now = time.time()
    cooldown = 30  # время в секундах между отправками

    # Устанавливаем ограничение времени на повторную отправку письма
    if now - last_sent < cooldown:
        wait_time = int(cooldown - (now - last_sent))
        flash(f'Пожалуйста, подождите {wait_time} секунд перед повторной отправкой.', 'warning')
        return redirect(url_for('auth.please_confirm'))

    token = generate_confirmation_token(email)
    send_confirmation_email(email, token)

    session['last_confirmation_sent'] = now
    flash('Письмо с подтверждением отправлено повторно.', 'info')
    return redirect(url_for('auth.please_confirm'))

@auth_bp.route('/confirm/<token>')
def confirm_email(token):
    email = confirm_token(token)
    if not email:
        return render_template('invalid_token.html')

    user = User.query.filter_by(email=email).first_or_404()
    if user.confirmed:
        flash('Аккаунт уже подтверждён.', 'info')
    else:
        user.confirmed = True
        db.session.commit()
        flash('Спасибо! Ваш аккаунт подтверждён.', 'success')

    return redirect(url_for('auth.login'))


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

        if User.query.filter_by(username=username).first():
            flash('Этот логин уже занят!', 'error')
            return redirect(url_for('auth.register'))

        if User.query.filter_by(email=email).first():
            flash('Этот email уже зарегистрирован!', 'error')
            return redirect(url_for('auth.register'))

        if not re.match(EMAIL_REGEX, email):
            flash('Введите корректный email.', 'error')
            return redirect(url_for('auth.register'))

        if not domain_has_mx(email):
            flash('Почтовый домен не найден. Проверьте email.', 'error')
            return redirect(url_for('auth.register'))

        if len(password) < 8 or not re.search(r'[0-9]', password) or not re.search(r'[A-Za-z]', password):
            flash('Пароль должен содержать минимум 8 символов, цифры и буквы.', 'error')
            return redirect(url_for('auth.register'))


        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password=hashed_password, email=email, confirmed=False)
        db.session.add(new_user)
        db.session.commit()

        token = generate_confirmation_token(new_user.email)
        send_confirmation_email(new_user.email, token)

        session['unconfirmed_email'] = new_user.email

        # login_user(new_user) если нужно сразу залогать клиента
        return redirect(url_for('auth.please_confirm'))

    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username_or_email = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username_or_email).first()
        if not user:
            user = User.query.filter_by(email=username_or_email).first()

        if user and check_password_hash(user.password, password):
            if not user.confirmed:
                flash('Пожалуйста, подтвердите ваш email, чтобы войти.', 'warning')
                return redirect(url_for('auth.please_confirm'))
            login_user(user)
            return redirect(url_for('todos.index'))

        flash('Неверный логин/почта или пароль!', 'error')

    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
