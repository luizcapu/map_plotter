__author__ = 'luiz'
import psycopg2
import json
from gradient_generator import GradientGenerator
import os


class DataExtractor(object):

    def __init__(self):
        pass

    def _row_to_feature(self, row):
        return {
            "type": "Feature",
            "properties": {
                "cod_distrito": row[0],
                "nominal_avg": float(row[1]),
            },
            "geometry": json.loads(row[2])
        }

    def run(self, cod_municipio, *args, **kwargs):
        map_json_folder = "%s/static/map_json" % os.path.abspath(
            os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))
        if not os.path.isdir(map_json_folder):
            try:
                os.makedirs(map_json_folder)
            except:
                pass
        map_json_file = "%s/%s.json" % (map_json_folder, cod_municipio)

        if not os.path.isfile(map_json_file):
            connection = psycopg2.connect(
                host='127.0.0.1', database = 'modgeo', user = 'root', password='pgrt123')
            cursor = connection.cursor()

            try:
                sql = 'select distrito_avg.cod_distrito,'
                sql += ' distrito_avg.nominal_avg,'
                sql += ' ST_AsGeoJSON(ST_Collect(malha.geom)) as json_geom'
                sql += ' from'
                sql += ' ('
                sql += ' select'
                sql += ' cast(substring(cast(malha.cod_setor as varchar) from 8 for 2) as varchar) as cod_distrito,'
                sql += ' cast(avg(cast(censo.v002 as int)) as numeric(15, 2)) as nominal_avg'
                sql += ' from dadosgeo.malha_see_domicilio_tabela malha,'
                sql += ' dadosgeo.ibge_censo_setor_2010_domiciliorenda censo'
                sql += ' where censo.cod_setor=malha.cod_setor'
                sql += ' and censo.v002 <> %s'
                sql += ' and malha.cod_municip=%s'
                sql += ' group by cod_distrito'
                sql += ' ) as distrito_avg, dadosgeo.malha_see_domicilio_tabela malha'
                sql += ' where malha.cod_municip=%s'
                sql += ' and cast(substring(cast(malha.cod_setor as varchar) from 8 for 2) as varchar)' \
                       ' = distrito_avg.cod_distrito'
                sql += ' group by distrito_avg.cod_distrito, distrito_avg.nominal_avg'
                sql += ' order by distrito_avg.nominal_avg desc'

                features = []
                feature_collection = {
                    "type": "FeatureCollection",
                    "features": features
                }

                cod_municipio = str(cod_municipio)
                cursor.execute(sql, ['X', cod_municipio, cod_municipio])
                for row in cursor:
                    features.append(self._row_to_feature(row))

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