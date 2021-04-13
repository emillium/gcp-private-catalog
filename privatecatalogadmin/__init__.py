from flask import Flask
from privatecatalogadmin import catalog

app = Flask(__name__)
app.register_blueprint(catalog.bp)

