from flask import Flask
from config import ProductionConfig

app = Flask(__name__)
app.config.from_object(ProductionConfig)
