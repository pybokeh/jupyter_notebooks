import pycovid19
import panel as pn

country_app = pycovid19.by_country
us_app = pycovid19.us_app

# myapp.show(host='localhost', port=8889, websocket_origin='localhost:8889', open=False)
# us_app.show(host='localhost', port=8889, websocket_origin='localhost:8889', open=False)

pn.serve({'By_Country': country_app, 'US_Only': us_app}, port=8890, websocket_origin='localhost:8890', show=False)