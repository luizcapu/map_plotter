#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'luiz'

# all the imports
from flask import Flask, request, redirect, url_for, render_template
from helpers.data_extractor import DataExtractor
from helpers.helpers import Helpers
import argparse
import os


def _run_main(args):

    app = Flask(__name__)
    app.config.from_object(__name__)
    os.environ["api_env"] = args.env

    _cfg = Helpers.load_config()

    @app.route("/")
    def index(error=None):
        return render_template("index.html",
                               cities=Helpers.load_cities_from_uf("35"),
                               error=error)

    @app.route("/navg_redir", methods=['POST'])
    def navg_redir():
        return redirect(url_for("nominal_avg", **dict(city_id=request.form['city_id'])))

    @app.route("/nominal_avg/<city_id>")
    @app.route("/nominal_avg/<city_id>/")
    def nominal_avg(city_id):
        try:
            extractor = DataExtractor()
            extractor.run(city_id)
            city_geo = Helpers.get_place_geo(
                "BRASIL, SP, " + extractor.get_name_from_id(city_id))["results"][0]
            return render_template("nominal_avg.html",
                                   city_name=extractor.get_name_from_id(city_id),
                                   map_lat=city_geo["geometry"]["location"]["lat"],
                                   map_lon=city_geo["geometry"]["location"]["lng"],
                                   json_url=url_for('static', filename='map_json/%s.json' % city_id),
                                   gm_api_key=_cfg.get("google_maps", {}).get("api_key", ""))
        except:
            return index("Unable to load nominal avg for %s" % city_id)

    #app.add_url_rule('/favicon.ico', redirect_to=url_for('static', filename='favicon.ico'))
    app.run(debug=_cfg["env"] != "prod", host=_cfg["api"]["host"], port=_cfg["api"]["port"])


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--env", type=str, default="test",
                        help="Environment to run (prod|test). Default: test")
    args = parser.parse_args()
    _run_main(args)

