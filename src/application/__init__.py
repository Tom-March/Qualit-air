from .app import app
from .routes import qualitair_app

app.register_blueprint(qualitair_app)