# Fix if you want to use seaborn library: https://github.com/adamhajari/spyre/issues/34
from spyre import server

import pandas as pd
import seaborn as sns
import pdb  # only needed for debugging purposes


class SalesApp(server.App):
    title = "Sales - U.S. Market Only"

    # Define tabs that will be displayed and populated with output
    tabs = ["README", "Plot", "Table"]

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
                           {"label": "2016", "value": "2016"},
                           {"label": "2017", "value": "2017"}
                          ],
               "value": '2017',  # default value
               "key": 'year'
              },
              {
               "type": 'dropdown',
               "label": 'Plant',
               "options": [{"label": "ALL", "value": "ALL"},
                           {"label": "Css", "value": "CSS"},
                           {"label": "ELP", "value": "ELP"},
                           {"label": "HCL", "value": "HCL"},
                           {"label": "HCM", "value": "HCM"},
                           {"label": "HDM", "value": "HDM"},
                           {"label": "HMA", "value": "HMA"},
                           {"label": "HMI", "value": "HMIN"},
                           {"label": "HUM", "value": "HUM"},
                           {"label": "MAP", "value": "MAP"},
                           {"label": "PMC", "value": "PMC"},
                           {"label": "Sss", "value": "SSS"},
                           {"label": "Tss", "value": "TSS"},
                           {"label": "Xss", "value": "XSS"}
                          ],
               "value": 'ALL',  # default value
               "key": 'plant'
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
               "value": 'NSX',  # default value
               "key": 'model'
              },
              {
               "type": 'dropdown',
               "label": '# of Doors',
               "options": [{"label": "ALL", "value": "ALL"},
                           {"label": "2-Dr", "value": "2"},
                           {"label": "4-Dr", "value": "4"},
                           {"label": "5-Dr", "value": "5"}
                          ],
               "value": 'ALL',  # default value
               "key": 'doors'
              },
              {
               "type": 'dropdown',
               "label": 'Eng Cyl',
               "options": [{"label": "ALL", "value": "ALL"},
                           {"label": "L4", "value": "4"},
                           {"label": "V6", "value": "6"}
                          ],
               "value": 'ALL',  # default value
               "key": 'cyl'
              }
             ]

    controls = [{"control_type": "button",
                 "label": "Update",
                 "control_id": "update_data"
                }
               ]

    outputs = [{"type": "plot",
                "output_id": "getPlot",
                "control_id": "update_data",
                "tab": "Plot"
               },
               {"type": "table",
                 "output_id": "getData",
                 "control_id": "update_data",
                 "tab": "Table",
                 "on_page_load": True
               },
               {"type": "html",
                 "output_id": "readMe",
                 "control_id": "update_data",
                 "tab": "README"
               }
              ]

    def getData(self, params):
        """Function to obtain the sales for the specified model year and model.  It is also used to
        populate the "Table" tab."""

        # Obtain the model year and model dropdown widget selection

        # pdb.set_trace()  #  to debug...

        year = int(params['year'])
        plant = params['plant']
        model = params['model']
        doors = params['doors']
        cyl = params['cyl']

        # Read in the sales data
        df = pd.read_csv("sales2.csv")

        # Available criteria
        year_crit = df['MDL_YR'] == year
        plant_crit = df['FCTRY_CD'] == plant
        model_crit = df['MDL_NM'] == model
        doors_crit = df['DOORS'] == doors
        cyl_crit = df['ENG_CYL'] == cyl

        # Logic needed if 'ALL' option is selected in any of the dropdown options
        if plant == 'ALL' and doors == 'ALL' and cyl == 'ALL':
            data = df[year_crit & model_crit]
        elif doors == 'ALL' and cyl == 'ALL':
            data = df[year_crit & plant_crit & model_crit]
        elif plant == 'ALL' and doors == 'ALL':
            data = df[year_crit & model_crit & cyl_crit]
        elif plant == 'ALL' and cyl == 'ALL':
            data = df[year_crit & model_crit & doors_crit]
        elif plant == 'ALL':
            data = df[year_crit & model_crit & doors_crit & cyl_crit]
        elif doors == 'ALL':
            data = df[year_crit & plant_crit & model_crit & cyl_crit]
        elif cyl == 'ALL':
            data = df[year_crit & plant_crit & model_crit & doors_crit]
        else:
            data = df[year_crit & plant_crit & model_crit & doors_crit & cyl_crit]

        # Aggregate the sales data by sale month using pandas pivot_table method
        grouped = pd.pivot_table(data, values='QTY', index='SALE_MTH', aggfunc='sum')
        result = pd.DataFrame(data={'Sale_Month': grouped.index, 'Qty': grouped.values},
                              columns=['Sale_Month', 'Qty'])
        return result

    def getPlot(self, params):
        """Function to generate the plot onto the "Plot" tab"""

        df = self.getData(params)
        total_sales = df.Qty.sum()
        plot_object = df.plot.bar(x='Sale_Month', y='Qty')
        plot_object.set_title('Total Sales: ' + "{:,}".format(total_sales))  # Add formatting to add comma
        plot_object.set_ylabel('Qty')
        plot_object.tick_params(labelsize=8)
        return plot_object

    def readMe(self, params):

        html = """<html>Provides sales by sales month.<br><br>
<strong>WARNING: </strong>Filtering by doors or engine cylinder is not reliable for Japan-built models
        </html>"""
        return html


if __name__ == '__main__':
    app = SalesApp()
    app.launch(host='10.60.26.75', port=9095)
