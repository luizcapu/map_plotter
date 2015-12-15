__author__ = 'luiz'

# all the imports
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from helpers.data_extractor import DataExtractor

# configuration
DATABASE = '/tmp/flaskr.db'
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'

app = Flask(__name__)
app.config.from_object(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/navg_redir", methods=['POST'])
def navg_redir():
    return redirect(url_for("nominal_avg", **dict(city_id=request.form['city_id'])))

@app.route("/nominal_avg/<city_id>")
@app.route("/nominal_avg/<city_id>/")
def nominal_avg(city_id):
    extractor = DataExtractor()
    extractor.run(city_id)
    return render_template("nominal_avg.html",
                           city_id=city_id,
                           json_url=url_for('static', filename='map_json/%s.json' % city_id))

if __name__ == '__main__':

    app.run(debug=True, host='0.0.0.0')

