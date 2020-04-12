import pycovid19global
import pycovid19us
import panel as pn

global_app = pycovid19global.global_app
us_app = pycovid19us.us_app

# myapp.show(host='localhost', port=8889, websocket_origin='localhost:8889', open=False)
# us_app.show(host='localhost', port=8889, websocket_origin='localhost:8889', open=False)

pn.serve({'By_Country': global_app, 'US_Only': us_app}, port=8890, websocket_origin='localhost:8890', show=False)