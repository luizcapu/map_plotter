from distutils.core import setup

setup(
    name='taxi_api',
    version='0.1',
    packages=['taxi_api', 'taxi_api/resources', 'taxi_api/business',
              'taxi_api/config', 'taxi_api/dao', 'taxi_api/dao/elasticsearch',
              'taxi_api/ds_provider', 'taxi_api/ds_provider/datasources',
              'taxi_api/helpers', 'taxi_api/to'],
    package_dir={'taxi_api': 'taxi_api'},
    package_data={'taxi_api': ['config/*']},
    include_package_data=True,
    license='luizcapu All rights reserved',
    long_description=open('README.md').read(),
)
