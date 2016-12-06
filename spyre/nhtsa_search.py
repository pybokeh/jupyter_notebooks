# Fix if you want to use seaborn library: https://github.com/adamhajari/spyre/issues/34
from spyre import server

import pandas as pd
import sqlite3


class NhtsaApp(server.App):
    title = "NHTSA Search App"

    # Define tabs that will be displayed and populated with output
    tabs = ["ReadMe", "ExcelOutput"]

    inputs = [
              {
               "type": 'multiple',
               "label": 'Model Year',
               "options": [{"label": "2008", "value": "2008", "checked": True},
                           {"label": "2009", "value": "2009"},
                           {"label": "2010", "value": "2010"},
                           {"label": "2011", "value": "2011"},
                           {"label": "2012", "value": "2012"},
                           {"label": "2013", "value": "2013"},
                           {"label": "2014", "value": "2014"},
                           {"label": "2015", "value": "2015"},
                           {"label": "2016", "value": "2016"},
                           {"label": "2017", "value": "2017"},
                           {"label": "2018", "value": "2018"}
                          ],
               "key": 'year'
              },
              {
               "type": 'multiple',
               "label": 'Model Name',
               "options": [{"label": "Accord", "value": "ACCORD", "checked": True},
                           {"label": "Civic", "value": "CIVIC"},
                           {"label": "CL", "value": "CL"},
                           {"label": "CR-V", "value": "CR-V"},
                           {"label": "Del Sol", "value": "DEL SOL"},
                           {"label": "Element", "value": "ELEMENT"},
                           {"label": "Fit", "value": "FIT"},
                           {"label": "HR-V", "value": "HR-V"},
                           {"label": "ILX", "value": "ILX"},
                           {"label": "Insight", "value": "INSIGHT"},
                           {"label": "Integra", "value": "INTEGRA"},
                           {"label": "Legend", "value": "Legend"},
                           {"label": "MDX", "value": "MDX"},
                           {"label": "NSX", "value": "NSX"},
                           {"label": "Odyssey", "value": "ODYSSEY"},
                           {"label": "Passport", "value": "PASSPORT"},
                           {"label": "Pilot", "value": "PILOT"},
                           {"label": "Prelude", "value": "PRELUDE"},
                           {"label": "RDX", "value": "RDX"},
                           {"label": "Ridgeline", "value": "RIDGELINE"},
                           {"label": "RL", "value": "RL"},
                           {"label": "RLX", "value": "RLX"},
                           {"label": "RSX", "value": "RSX"},
                           {"label": "S2000", "value": "S2000"},
                           {"label": "SLX", "value": "SLX"},
                           {"label": "TL", "value": "TL"},
                           {"label": "TLX", "value": "TLX"},
                           {"label": "Vigor", "value": "VIGOR"},
                           {"label": "ZDX", "value": "ZDX"}
                          ],
               "key": 'model'
              },
              {
               "type": 'multiple',
               "label": 'System/Component',
               "options": [{"label": "All", "value": "%", "checked": True},
                           {"label": "Air Bags", "value": "AIR BAGS"},
                           {"label": "Back Over Prevention", "value": "BACK OVER PREVENTION"},
                           {"label": "Brakes", "value": "BRAKE"},
                           {"label": "Child Seat", "value": "CHILD SEAT"},
                           {"label": "Electrical System", "value": "ELECTRICAL"},
                           {"label": "Electronic Stability Control", "value": "ELECTRONIC STABILITY CONTROL"},
                           {"label": "Equipment", "value": "EQUIPMENT"},
                           {"label": "Equipment Adaptive", "value": "EQUIPMENT ADAPTIVE"},
                           {"label": "Equipment:Mechanical", "value": "EQUIPMENT:MECHANICAL"},
                           {"label": "Equipment:Other", "value": "EQUIPMENT:OTHER"},
                           {"label": "Equipment:Recreational", "value": "EQUIPMENT:RECREATIONAL"},
                           {"label": "Engine", "value": "ENGINE"},
                           {"label": "Exterior Lighting", "value": "EXTERIOR LIGHTING"},
                           {"label": "Forward Collision Avoidance", "value": "FORWARD COLLISION AVOIDANCE"},
                           {"label": "Fuel System", "value": "FUEL"},
                           {"label": "Hybrid Propulsion System", "value": "HYBRID PROPULSION SYSTEM"},
                           {"label": "Interior Lighting", "value": "INTERIOR LIGHTING"},
                           {"label": "Lane Departure", "value": "LANE DEPARTURE"},
                           {"label": "Latches/Locks/Linkages", "value": "LATCHES/LOCKS/LINKAGES"},
                           {"label": "Other", "value": "OTHER"},
                           {"label": "Power Train", "value": "POWER TRAIN"},
                           {"label": "Seat Belts", "value": "SEAT BELTS"},
                           {"label": "Seats", "value": "SEATS"},
                           {"label": "Steering", "value": "STEERING"},
                           {"label": "Structure", "value": "STRUCTURE"},
                           {"label": "Suspension", "value": "Suspension"},
                           {"label": "Tires", "value": "TIRES"},
                           {"label": "Traction Control System", "value": "TRACTION CONTROL SYSTEM"},
                           {"label": "Trailer Hitches", "value": "TRAILER HITCHES"},
                           {"label": "Unknown or Other", "value": "UNKNOWN OR OTHER"},
                           {"label": "Vehicle Speed Control", "value": "VEHICLE SPEED CONTROL"},
                           {"label": "Visibility", "value": "VISIBILITY"},
                           {"label": "Wheels", "value": "WHEELS"}
                          ],
               "key": 'component'
              }
             ]

    controls = [{"control_type": "button",
                 "label": "Export to Excel",
                 "control_id": "update_data"
                }
               ]

    outputs = [{"type": "html",
                 "output_id": "readMe",
                 "tab": "ReadMe",
                 "on_page_load": True
               },
               {"type": "html",
                 "output_id": "outputExcel",
                 "control_id": "update_data",
                 "tab": "ExcelOutput",
                 "on_page_load": False
               }
              ]

    def sqlCriteria(self, yearsList, modelsList, compsList):
        join_str = "','"
        year_criteria = "YEARTXT IN(" + "'" + join_str.join(yearsList) + "'" + ") \n"

        model_criteria = ''
        if len(modelsList) == 1:
            model_criteria_final = "MODELTXT like '%" + modelsList[0] + "%' \n"
        else:
            model_criteria1 = "(MODELTXT like '%" + modelsList[0] + "%' \n"
            for model in modelsList[1:]:
                model_criteria = model_criteria + " or MODELTXT like '%" + model + "%' \n"
            model_criteria_final = model_criteria1 + model_criteria + ") "

        comp_criteria = ''

        if len(compsList) == 1:
            comp_criteria_final = "COMPDESC like '%" + compsList[0] + "%' \n"
        else:
            comp_criteria1 = "(COMPDESC like '%" + compsList[0] + "%' \n"
            for comp in compsList[1:]:
                comp_criteria = comp_criteria + " or COMPDESC like '%" + comp + "%' \n"
            comp_criteria_final = comp_criteria1 + comp_criteria + ") "

        return year_criteria + "AND " + model_criteria_final + "AND " + comp_criteria_final

    def outputExcel(self, params):

        years = params['year']
        models = params['model']
        comps = params['component']
        yearsList = years.split(',')
        modelsList = models.split(',')
        compsList = comps.split(',')

        sql = """
SELECT
VIN,
CITY,
STATE,
COMPDESC,
CDESCR,
CASE
WHEN CMPL_TYPE = 'EVOQ' THEN 'HOTLINE VOQ'
WHEN CMPL_TYPE = 'IVOQ' THEN 'NHTSA WEB SITE'
WHEN CMPL_TYPE = 'CAG' THEN 'CONSUMER ACTION GROUP'
WHEN CMPL_TYPE = 'CON' THEN 'FORWARDED FROM A CONGRESSIONAL OFFICE'
WHEN CMPL_TYPE = 'DP' THEN 'DEFECT PETITION,RESULT OF A DEFECT PETITION'
WHEN CMPL_TYPE = 'EWR' THEN 'EARLY WARNING REPORTING'
WHEN CMPL_TYPE = 'INS' THEN 'INSURANCE COMPANY'
WHEN CMPL_TYPE = 'LETR' THEN 'CONSUMER LETTER'
WHEN CMPL_TYPE = 'MAVQ' THEN 'NHTSA MOBILE APP'
WHEN CMPL_TYPE = 'MIVQ' THEN 'NHTSA MOBILE APP'
WHEN CMPL_TYPE = 'MVOQ' THEN 'OPTICAL MARKED VOQ'
WHEN CMPL_TYPE = 'RC' THEN 'RECALL COMPLAINT,RESULT OF A RECALL INVESTIGATION'
WHEN CMPL_TYPE = 'RP' THEN 'RECALL PETITION,RESULT OF A RECALL PETITION'
WHEN CMPL_TYPE = 'VOQ' THEN 'NHTSA VEHICLE OWNERS QUESTIONNAIRE'
ELSE CMPL_TYPE END AS CMPL_TYPE_DESC,
YEARTXT,
MAKETXT,
MODELTXT,
FAILDATE,
MILES,
LDATE,
CRASH,
FIRE,
INJURED,
DEATHS,
VEHICLES_TOWED_YN,
MEDICAL_ATTN,
POLICE_RPT_YN,
OCCURENCES,
DATEA

FROM complaints

WHERE
"""

        sql_final = sql + self.sqlCriteria(yearsList, modelsList, compsList)

        conn = sqlite3.connect(r'D:\NHTSA\nhtsa.db')

        df_spyre = pd.read_sql_query(sql_final, conn)
        conn.close()

        df_spyre.to_excel(r'D:\webapps\nhtsa\files\nhtsa_output.xlsx', index=False)

        html = """Click <a href="http://vclo49529/nhtsa/files/nhtsa_output.xlsx">here</a> for the Excel file output.<br><br>
        <strong>CRITERIA: </strong>""" + self.sqlCriteria(yearsList, modelsList, compsList) + " LIMIT 50000"

        return html

    def readMe(self, params):

        html = """<html>To select multiple items, hold down CTRL key.<br><br>
<strong>WARNING: </strong>Due to limitation of system, there is currently no way to distinguish between 
TL and TLX or RL and RLX.<br><br>
After clicking on "Export to Excel" button, navigate to "ExcelOutput" tab and click on URL for the Excel output.<br><br>
Please choose option to "Save" <strong>NOT</strong> "Open" the Excel file.<br><br>
<strong>NOTE: </strong>Excel file will not contain more than 50K rows.
        </html>"""

        return html

    def getCustomCSS(self):
        """ Define custom CSS formatting here if you don't like the defaults.
            Menu title is made with HTML <h1> tag:
                Over-written text-transform because I didn't want the menu title to be all caps
                Over-written font-size because the menu title was too big"""

        css = """h1 {
                    text-transform: none;
                    font-size: 22px;
                }
              """
        return css


if __name__ == '__main__':
    app = NhtsaApp()
    app.launch(host="10.60.27.75", port=9998)
