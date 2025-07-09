import os
from dotenv import load_dotenv
from flask import Flask, jsonify, render_template
from extensions import init_extensions, db, login_manager
from auth import auth_bp
from todos import todos_bp
from models import User
from extensions import mail


load_dotenv()

def create_app():
    app = Flask(__name__, template_folder='templates')

    app.config.update(
        SECRET_KEY=os.getenv('SECRET_KEY', 'dev-secret-key'),
        SQLALCHEMY_DATABASE_URI=os.getenv('DATABASE_URL', 'sqlite:///instance/todos.db'),
        JWT_SECRET_KEY=os.getenv('JWT_SECRET_KEY', 'dev-jwt-secret-key'),
        JWT_TOKEN_LOCATION=['headers', 'cookies'],
        SESSION_COOKIE_SECURE=False,
        REMEMBER_COOKIE_SECURE=False,
        SESSION_COOKIE_HTTPONLY=True,
        REMEMBER_COOKIE_HTTPONLY=True,

        MAIL_SERVER=os.getenv('MAIL_SERVER', 'smtp.gmail.com'),
        MAIL_PORT=int(os.getenv('MAIL_PORT', 587)),
        MAIL_USE_TLS=os.getenv('MAIL_USE_TLS', 'True') == 'True',
        MAIL_USERNAME=os.getenv('MAIL_USERNAME'),
        MAIL_PASSWORD=os.getenv('MAIL_PASSWORD'),
        MAIL_DEFAULT_SENDER=os.getenv('MAIL_DEFAULT_SENDER', os.getenv('MAIL_USERNAME')),
    )

    init_extensions(app)

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(todos_bp, url_prefix='/')

    @app.errorhandler(404)
    def not_found(e):
        return render_template('404.html'), 404

    @app.errorhandler(401)
    def unauthorized(e):
        return jsonify({"error": "Unauthorized"})

    @app.errorhandler(500)
    def internal_error(e):
        return jsonify({"error": "Internal server error"})

    with app.app_context():
        db.create_all()

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
