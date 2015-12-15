TunEduc Map Plotter Project
============

Objetivos
-----

[Descrição dos Objetivos](docs/goals.pdf)


Instalação
-----

1) Prepare seu ambiente para rodar aplicações Python (2.7x) (https://www.python.org/about/gettingstarted/)

2) Preferencialmente, faço uso de ambientes virtuais (https://osantana.me/ambiente-isolado-para-python-com-virtualenv/)

3) Ative o virtualenv

4) Rode o arquivo install.sh encontrado na raiz do projeto


Help Output
-----

```
usage: server.py [-h] [-e ENV]

optional arguments:
  -h, --help         show this help message and exit
  -e ENV, --env ENV  Environment to run (prod|test). Default: test
```

Configurações
-----

Edite as configurações da aplicação no arquivo map_plotter/config/cfg-ENV.json (ex: cfg-test.json)


Exemplo de Uso
-----

```
./map_plotter/server.py -e prod
```

Pelo browser acesse o host e a porta configurados no arquivo de configuração. Ex: http://localhost:5001/


Exemplo de Plotagem
-----

![Exemplo de Plotagem](docs/exemplo.jpg?raw=true)
