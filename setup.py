from distutils.core import setup

setup(
    name='map_ploter',
    version='0.1',
    packages=['map_ploter', 'map_ploter/helpers', 'map_ploter/static',
              'map_ploter/templates', 'map_ploter/config'],
    package_dir={'map_ploter': 'map_ploter'},
    package_data={'map_ploter': ['config/*']},
    include_package_data=True,
    license='luizcapu All rights reserved',
    long_description=open('README.md').read(),
)
