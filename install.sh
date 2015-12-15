#!/bin/sh

rm -fr build
pip install flask
pip install psycopg2
pip install geopy
python setup.py install


