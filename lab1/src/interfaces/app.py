from flask import Flask

def create_app():
    """Создание и настройка Flask-приложения"""
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'kindergarten-secret-key-2024'  # нужно для flash-сообщений

    # Импортируем и регистрируем маршруты
    from src.interfaces.web_interface.routes import main_bp
    app.register_blueprint(main_bp)

    return app