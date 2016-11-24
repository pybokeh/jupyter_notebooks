# Fix if you want to use seaborn library: https://github.com/adamhajari/spyre/issues/34
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
               "key": 'year'
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
               "key": 'model'
              }
             ]

    controls = [{"control_type": "button",
                 "label": "Update",
                 "control_id": "update_data"
                }
               ]

    tabs = ["Plot", "Table"]

    outputs = [{"type": "plot",
                "output_id": "plot_id",
                "control_id": "update_data",
                "tab": "Plot"
               },
               {"type": "table",
                 "output_id": "table_id",
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
        data = df[yr_crit & mdl_crit]
        grouped = pd.pivot_table(data, values='QTY', index='SALE_MTH', aggfunc='sum')
        result = pd.DataFrame(data={'Sale_Month': grouped.index, 'Qty': grouped.values}, columns=['Sale_Month', 'Qty'])
        return result

    def getPlot(self, params):
        df = self.getData(params)
        total_sales = df.Qty.sum()
        print(total_sales)
        plot_object = df.plot.bar(x='Sale_Month', y='Qty')
        plot_object.set_title('Total Sales: ' + "{:,}".format(total_sales))  # Add formatting to add comma
        plot_object.set_ylabel('Qty')
        plot_object.tick_params(labelsize=8)
        return plot_object


if __name__ == '__main__':
    app = SalesApp()
    app.launch(port=9093)
