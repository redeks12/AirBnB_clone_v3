#!/usr/bin/python3
"""for the following files"""
from flask import Flask
from models import storage
from api.v1.views import app_views

app = Flask(__name__)
app.register_blueprint(app_views)


@app.teardown_appcontext
def teardown(err):
    """Teardown the application"""
    storage.close()


if __name__ == "__main__":
    app.run(host="0.0.0.0")
