"""
The flask application package.
"""

from flask import Flask
app = Flask(__name__)
app.secret_key = 'Hala Madrid y Nada Mas!'

import MovieGuru.views
