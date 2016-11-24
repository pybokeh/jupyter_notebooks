# tested with python2.7 and 3.4
from spyre import server

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from altair import Chart, load_dataset
import seaborn as sns


class Altair(server.App):
    title = "Altair Spyre Example"

    inputs = [{"type": "slider",
                "label": 'Exclude First',
                "min": 0, "max": 14, "value": 0,
                "key": 'ex_first'}]

    controls = [{"type": "button",
                 "label": "Make Matplotlib Graph",
                 "control_id": "submit_plot"},
                {"type": "button",
                    "label": "Load Table",
                    "control_id": "load_table"}]

    outputs = [{"type": "plot",
                "output_id": "plot_id",
                "control_id": "submit_plot",
                "tab": "Plot"},
               {"type": "table",
                "output_id": "table_id",
                "control_id": "load_table",
                "tab": "Table"},
               {"type": "html",
                "output_id": "getHTML",
                "on_page_load": True,
                "tab": "About"}]

    tabs = ["Plot", "Table", "About"]

    def getData(self, params):
        # cache values within the Launch object to avoid reloading the data each time
        ex_first = int(params['ex_first'])
        count = [620716, 71294, 50807, 7834, 5237, 3278, 2533, 2042, 1266, 1165, 980, 962, 747, 712, 679]
        name = ['Musician', 'Author', 'Book', 'Record Label', 'Actor', 'Public Figure', 'Comedian',
                'Producer', 'News/Media', 'Entertainer', 'Radio Station', 'TV Show', 'Company', 'Local Business', 'Apparel']
        df = pd.DataFrame({'name': name, 'count': count})
        df = df[['name', 'count']]
        return df[ex_first:]

    def getPlot(self, params):
        data = self.getData(params)  # get data
        fig = plt.figure()  # make figure object
        splt = fig.add_subplot(1, 1, 1)
        ind = np.arange(len(data['name']))
        width = 0.85
        splt.bar(ind, data['count'], width)
        splt.set_ylabel('Count')
        splt.set_title('Cars Data Set')
        splt.set_xticks(ind + width / 2)
        splt.set_xticklabels(data['name'].tolist())
        fig.autofmt_xdate(rotation=45)
        return splt

    def getHTML(self, params):
        cars = load_dataset('cars')

        c = Chart(cars).mark_point().encode(
            x='Horsepower',
            y='Miles_per_Gallon',
            color='Origin'
        )
        print(c.to_html())
        return c.to_html()

if __name__ == '__main__':
    app = Altair()
    app.launch(port=9091)

