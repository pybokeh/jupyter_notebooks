# tested with python2.7 and 3.4
# must be run from same directory as stock_data.json (in spyre examples directory)
from spyre import server

import pandas as pd
import seaborn as sns


class SalesApp(server.App):
    title = "Sales - US Mkt"

    inputs = [
              {
               "type": 'dropdown',
               "label": 'Model Year',
               "options": [{"label": "2008", "value": "2008"},
                           {"label": "2009", "value": "2009"},
                           {"label": "2010", "value": "2010"},
                           {"label": "2011", "value": "2011"},
                           {"label": "2012", "value": "2012"},
                           {"label": "2013", "value": "2013"},
                           {"label": "2014", "value": "2014"},
                           {"label": "2015", "value": "2015"},
                           {"label": "2016", "value": "2016"}
                          ],
               "value": '2016',  # default value
               "key": 'year',
               "action_id": "update_data"
              },
              {
               "type": 'dropdown',
               "label": 'Model Name',
               "options": [{"label": "Accord", "value": "ACCORD"},
                           {"label": "Civic", "value": "CIVIC"},
                           {"label": "Crosstour", "value": "CROSSTOUR"},
                           {"label": "CR-V", "value": "CRV"},
                           {"label": "CR-Z", "value": "CRZ"},
                           {"label": "Element", "value": "ELEMENT"},
                           {"label": "FCX", "value": "FCX"},
                           {"label": "Fit", "value": "FIT"},
                           {"label": "HR-V", "value": "HRV"},
                           {"label": "ILX", "value": "ILX"},
                           {"label": "Insight", "value": "INSIGHT"},
                           {"label": "MDX", "value": "MDX"},
                           {"label": "NSX", "value": "NSX"},
                           {"label": "Odyssey", "value": "ODYSSEY"},
                           {"label": "Pilot", "value": "PILOT"},
                           {"label": "RDX", "value": "RDX"},
                           {"label": "Ridgeline", "value": "Ridgeline"},
                           {"label": "RL", "value": "RL"},
                           {"label": "RLX", "value": "RLX"},
                           {"label": "S2000", "value": "S2000"},
                           {"label": "TL", "value": "TL"},
                           {"label": "TLX", "value": "TLX"},
                           {"label": "TSX", "value": "TSX"},
                           {"label": "ZDX", "value": "ZDX"}
                          ],
               "value": 'Accord',  # default value
               "key": 'model',
               "action_id": "update_data"
              }
             ]

    controls = [{"type": "hidden",
                 "id": "update_data"
                }
               ]

    tabs = ["Plot", "Table"]

    outputs = [{"type": "plot",
                "id": "plot",
                "control_id": "update_data",
                "tab": "Plot"
               },
               {"type": "table",
                 "id": "table_id",
                 "control_id": "update_data",
                 "tab": "Table",
                 "on_page_load": True
               }
              ]

    def getData(self, params):
        mdl_yr = int(params['year'])
        model = params['model']
        df = pd.read_csv("sales.csv")
        yr_crit = df.MDL_YR == mdl_yr
        mdl_crit = df.MDL_NM == model
        return df[yr_crit & mdl_crit]

    def getPlot(self, params):
        df = self.getData(params)
        grouped = pd.pivot_table(df, values='QTY', index='SALE_MTH', aggfunc='sum')
        plot_object = grouped.plot.bar()
        plot_object.set_title('Sales by Sales Month - U.S. Market ONLY')
        plot_object.set_ylabel('Qty')
        plot_object.tick_params(labelsize=8)
        return plot_object


if __name__ == '__main__':
    app = SalesApp()
    app.launch(port=9093)
