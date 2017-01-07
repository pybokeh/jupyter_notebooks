# tested with python2.7 and 3.4
from spyre import server
from altair import Chart, load_dataset


class Altair(server.App):
    title = "Altair Spyre Example"

    outputs = [{"type": "html",
                "output_id": "getAltair",
                "tab": "Altair",
                "on_page_load": True}
              ]

    tabs = ["Altair"]

    def getAltair(self, params):
        cars = load_dataset('cars')

        c = Chart(cars).mark_point().encode(
            x='Horsepower',
            y='Miles_per_Gallon',
            color='Origin'
        )

        return c.to_html()

    def getCustomJS(self):
        js1 = open('d3.v3.min.js', 'r').read()
        js2 = open('vega.js', 'r').read()
        js3 = open('vega-embed.js', 'r').read()
        js4 = open('vega-lite.js', 'r').read()

        return js1 + ' ' + js2 + ' ' + js3 + ' ' + js4

if __name__ == '__main__':
    app = Altair()
    app.launch(port=9091)

