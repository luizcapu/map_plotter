# -*- coding: utf-8 -*-
__author__ = 'luiz'
import psycopg2
import json
from gradient_generator import GradientGenerator
import os
from helpers import Helpers


class DataExtractor(object):
    """
    Descricao codigo setor censitario

    Formato: UFMMMMMDDSDSSSS
    UF - unidade de federacao
    MMMMM - municipio
    DD - distrito
    SD - subdistrito
    SSSS - setor
    """

    _cities_name = {}
    __db_cfg = None
    _bairro_start_pos = '8'
    _bairro_copy_len = '2'

    def __init__(self):
        self.city_name = None

    def _row_to_feature(self, row):
        return {
            "type": "Feature",
            "properties": {
                "cod_distrito": row[0],
                "nominal_avg": "{:,}".format(int(row[1])),
                "num_nominal_avg": float(row[1]),
            },
            "geometry": json.loads(row[2])
        }

    @property
    def _cfg(self):
        if DataExtractor.__db_cfg is None:
            DataExtractor.__db_cfg = Helpers.load_config()["database"]
        return DataExtractor.__db_cfg

    def get_name_from_id(self, city_id, db_cursor=None):
        if not city_id in DataExtractor._cities_name.keys():
            if db_cursor is None:
                connection = psycopg2.connect(
                    host=self._cfg["host"],
                    database=self._cfg["dbname"],
                    user=self._cfg["username"],
                    password=self._cfg["password"]
                )
                db_cursor = connection.cursor()
            sql = 'select nm_municip from dadosgeo.malha_see_domicilio_tabela malha where cod_municip=%s limit 1'
            db_cursor.execute(sql, (city_id,))
            DataExtractor._cities_name[city_id] = db_cursor.fetchone()[0]
        return DataExtractor._cities_name[city_id]

    def run(self, city_id, *args, **kwargs):
        map_json_folder = "%s/static/map_json" % os.path.abspath(
            os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))
        if not os.path.isdir(map_json_folder):
            try:
                os.makedirs(map_json_folder)
            except:
                pass
        map_json_file = "%s/%s.json" % (map_json_folder, city_id)

        connection = psycopg2.connect(
            host=self._cfg["host"],
            database=self._cfg["dbname"],
            user=self._cfg["username"],
            password=self._cfg["password"]
        )
        cursor = connection.cursor()

        try:
            self.get_name_from_id(city_id, cursor)

            if not os.path.isfile(map_json_file):
                sql = 'select distrito_avg.cod_distrito,'
                sql += ' distrito_avg.nominal_avg,'
                sql += ' ST_AsGeoJSON(ST_Collect(malha.geom)) as json_geom'
                sql += ' from'
                sql += ' ('
                sql += ' select'
                sql += ' cast(substring(cast(malha.cod_setor as varchar) from '+\
                       DataExtractor._bairro_start_pos+' for '+\
                       DataExtractor._bairro_copy_len+') as varchar) as cod_distrito,'
                sql += ' cast(avg(cast(censo.v002 as int)) as float) as nominal_avg'
                sql += ' from dadosgeo.malha_see_domicilio_tabela malha,'
                sql += ' dadosgeo.ibge_censo_setor_2010_domiciliorenda censo'
                sql += ' where censo.cod_setor=malha.cod_setor'
                sql += ' and censo.v002 <> %s'
                sql += ' and malha.cod_municip=%s'
                sql += ' group by cod_distrito'
                sql += ' ) as distrito_avg, dadosgeo.malha_see_domicilio_tabela malha'
                sql += ' where malha.cod_municip=%s'
                sql += ' and cast(substring(cast(malha.cod_setor as varchar) from '+\
                       DataExtractor._bairro_start_pos+' for '+\
                       DataExtractor._bairro_copy_len+') as varchar)' \
                       ' = distrito_avg.cod_distrito'
                sql += ' group by distrito_avg.cod_distrito, distrito_avg.nominal_avg'
                sql += ' order by distrito_avg.nominal_avg desc'

                features = []
                feature_collection = {
                    "type": "FeatureCollection",
                    "features": features
                }

                max_avg = None
                min_avg = None
                city_id = str(city_id)
                cursor.execute(sql, ['X', city_id, city_id])
                for row in cursor:
                    if max_avg is None or max_avg < row[1]:
                        max_avg = row[1]
                    if min_avg is None or min_avg > row[1]:
                        min_avg = row[1]
                    features.append(self._row_to_feature(row))

                if max_avg is not None and min_avg is not None and max_avg != min_avg:
                    _range = max_avg - min_avg
                    for feature in features:
                        feat_avg = feature["properties"].pop("num_nominal_avg")
                        percentage = int(((feat_avg - min_avg) * 100) / _range)
                        feature["properties"]["color"] = GradientGenerator.gradient_from_percentage(
                            "#FF4C4C", "#007F00", percentage  # red to green
                        )
                else:
                    _idx = 0
                    for color in GradientGenerator.linear_gradient("#007F00", "#FF4C4C", len(features)):  # green to red
                        features[_idx]["properties"]["color"] = color
                        _idx += 1

                with open(map_json_file, "w+") as f:
                    f.write(json.dumps(feature_collection))
        finally:
            cursor.close()
            connection.close()

if __name__ == '__main__':
    e = DataExtractor()
    e.run('3550308')
