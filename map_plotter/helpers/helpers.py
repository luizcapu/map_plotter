# -*- coding: utf-8 -*-
__author__ = 'luiz'

import os
import json
from urllib2 import urlopen
from urllib import urlencode
import psycopg2


class Helpers(object):

    _loaded_configs = {}
    _loaded_uf_cities = {}

    @staticmethod
    def load_config(environment=None, force_reload=False):
        if environment is None:
            print "env is None, getting from os.environ"
            environment = os.environ.get("api_env", "test")
            print "env=", environment
        if not environment in Helpers._loaded_configs.keys() or force_reload:
            # get location of cfg file
            base_path = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))
            cfg_file = "%s/config/cfg-%s.json" % (base_path, environment)

            # read cfg file
            with open(cfg_file, "r+") as f:
                cfg = json.loads(f.read())
                cfg["env"] = environment
                Helpers._loaded_configs[environment] = cfg

        return Helpers._loaded_configs[environment]

    @staticmethod
    def get_place_geo(place):
        url = "https://maps.googleapis.com/maps/api/geocode/json?" + urlencode({"address": place})
        v = urlopen(url).read()
        return json.loads(v)

    @staticmethod
    def load_cities_from_uf(uf):
        if not uf in Helpers._loaded_uf_cities.keys():
            _cfg = Helpers.load_config()["database"]
            connection = psycopg2.connect(
                host=_cfg["host"],
                database=_cfg["dbname"],
                user=_cfg["username"],
                password=_cfg["password"]
            )
            cursor = connection.cursor()

            try:
                sql = "select " \
                      "distinct( nm_municip ), cod_municip " \
                      "from dadosgeo.malha_see_domicilio_tabela malha " \
                      "where cast(cod_setor as varchar) " \
                      "like %s " \
                      "order by nm_municip"

                cursor.execute(sql, (uf+"%",))
                Helpers._loaded_uf_cities[uf] = [dict(name=row[0], code=row[1]) for row in cursor]
            finally:
                cursor.close()
                connection.close()

        return Helpers._loaded_uf_cities[uf]