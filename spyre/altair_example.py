# tested with python2.7 and 3.4
from spyre import server
from altair import Chart, load_dataset


class Altair(server.App):
    title = "Altair Spyre Example"

    outputs = [{"type": "html",
                "output_id": "getAltair",
                "tab": "Altair"}
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

if __name__ == '__main__':
    app = Altair()
    app.launch(port=9091)

