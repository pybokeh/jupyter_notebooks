# PURPOSE: To prepare data that will be used to voucher supplier ("ZF") on behalf of export plants
#
# Tooling / Technology Stack:
#   - Python 3.6
#   - Pandas for data extraction and transformation
#   - pyodbc for accessing databases
#   - Luigi for batch data processing for better data tracking, validation, and debugging
#   - tkinter GUI library to obtain the file paths to all the Excel input files

from datetime import datetime
from getpass import getpass
from pathlib import Path
import luigi
from luigi.format import UTF8
import numpy as np
import os
import pandas as pd
import pyodbc
from tkinter import Tk
from tkinter import filedialog, Label
from tkinter import ttk


class MyGlobals(luigi.Config):
    """Define 'global' parameter values here:
    
    Global Variables
    ----------------
    mydate: Python Date
        Today's date
    export_plant: str
        Export plant code (example: HUM, GHAC, etc)
    data_folder: str
        Folder location where output files will be saved
    start_voucher_date: str
        The start voucher date
    end_voucher_date: str
        The end voucher date
    claims_filepath: str
        The file path to the FQS claims Excel file
    prod_filepath: str
        The file path to the FQS production Excel file
    """

    # Today's date will be used as part of the folder name's destination
    mydate = datetime.today()
    export_plant = input("Enter export plant code (ex: HUM, GHAC, etc): ").upper()
    data_folder = 'outputs/text_files/ExportPlants/' + export_plant + '/' + datetime.strftime(mydate, "%Y-%m-%d") + '/'

    start_voucher_date = input("Enter start voucher date (YYYY-MM-DD): ")
    end_voucher_date = input("Enter end voucher date (YYYY-MM-DD): ")

    root = Tk()
    root.title("Obtain input files:")
    root.geometry('640x200')

    lbl_message = Label(root, text="Close this window after choosing all 2 files to continue with the rest of the automation.")
    lbl_message.grid(column=0, row=0)

    claims_filepath = filedialog.askopenfilename(initialdir="C:\\Users\\ma17151\\Downloads",
                                                 title="Select FQS Claims file",
                                                 filetypes=(("*.xlsx", "*.xlsx"), ("all files", "*.*")))

    prod_filepath = filedialog.askopenfilename(initialdir="C:\\Users\\ma17151\\Downloads",
                                               title="Select FQS Production file",
                                               filetypes=(("*.xlsx", "*.xlsx"), ("all files", "*.*")))

    root.mainloop()


class CreateReadMe(luigi.Task):
    """Task to create a README.txt file containing the input parameters that the user entered.
       It is recommended that after the automation process is complete,
       the user reads this file to confirm the parameters.
    """

    def output(self):
        return luigi.LocalTarget(MyGlobals().data_folder + 'README.txt')

    def run(self):
        message = "Export Plant: " + MyGlobals().export_plant + "\n" + \
                  "Start Voucher Date: " + MyGlobals().start_voucher_date + "\n" + \
                  "End Voucher Date: " + MyGlobals().end_voucher_date

        with self.output().open('w') as outfile:
            outfile.write(message)


class GetFqsExcel(luigi.Task):
    """Task that reads two local Excel files containing FQS-3 sourced warranty claims and production data.
       ZF has requested engine build date, which requires executing a 2nd FQS-3 query.
       NOTE: Download the FQS-3 Excel file as non-UTF8 format and then use Window's utf-8 encoding.  
       The UTF8 encoding used by FQS-3 is jacked up.  Discovered it is not standard or true utf-8."""

    def requires(self):
        return CreateReadMe()

    def output(self):
        """Define destination of your output file based on the global parameter set above"""

        return luigi.LocalTarget(MyGlobals().data_folder + 'claims_fqs.csv', format=UTF8)

    def run(self):
        """Define business logic for this task.
           Read Excel file as a tab-delimited file"""

        claims = pd.read_excel(MyGlobals().claims_filepath, encoding='utf-8',
                               parse_dates=['HM Claim Recognition Date (yyyy/mm/dd)',
                                                                         'Repair Order Date (yyyy/mm/dd)',
                                                                         'Production Date (yyyy/mm/dd)'],
                               dtype={'Failed Part No. (1-5)': str, 'Transmission Serial No.': str,
                                      'Local Claim No.': str, 'HM Claim No.': str, 'Repair Dealer No.': str})

        production = pd.read_excel(MyGlobals().prod_filepath, encoding='utf-8',
                                   parse_dates=['AE-OFF Date'])[['VIN', 'AE-OFF Date']]

        claims_fqs = pd.merge(claims, production, how='left', left_on='VIN', right_on='VIN')

        # Save the processed data at the location specified by this class' output() method
        with self.output().open('w') as outfile:
            claims_fqs.to_csv(outfile, index=False, encoding='utf-8')


class FilterClaims(luigi.Task):
    """Task that filters the initial FQS-3 claims down to:
       - ZF models
       - replaced part Qty > 0
       - within start and end voucher dates"""

    def requires(self):
        """For this task to process, it needs the following task(s) to be completed first:"""

        return GetFqsExcel()

    def output(self):
        """Specify location of where output file will be saved"""

        return luigi.LocalTarget(MyGlobals().data_folder + 'ZF_Claims.csv', format=UTF8)

    def run(self):
        """Obtain claims as input from the GetFqsExcel() task"""

        claims_fqs = pd.read_csv(self.input().open('r'), encoding='utf-8',
                                 parse_dates=['HM Claim Recognition Date (yyyy/mm/dd)',
                                              'Repair Order Date (yyyy/mm/dd)', 'Production Date (yyyy/mm/dd)'],
                                 dtype={'Failed Part No. (1-5)': str, 'Transmission Serial No.': str,
                                        'Local Claim No.': str, 'HM Claim No.': str, 'Repair Dealer No.': str})

        # Criteria to filter the initial FQS-3 Excel down to ZF models only with the specified voucher period
        # and replaced part qty > 0
        # & (claims_fqs['Transmission Type Code'].str.startswith('Q')) \
        criteria = (claims_fqs['HM Claim Recognition Date (yyyy/mm/dd)'] >= MyGlobals().start_voucher_date) \
            & (claims_fqs['HM Claim Recognition Date (yyyy/mm/dd)'] <= MyGlobals().end_voucher_date) \
            & (claims_fqs['Manufacturing plant code name'].str.startswith(MyGlobals().export_plant)) \
            & (claims_fqs['Transmission Class(Description)'].str.startswith('9AT')) \
            & (claims_fqs['Quantity of Replaced Parts'] > 0)
        
        claims_ZF = claims_fqs[criteria]

        with self.output().open('w') as outfile:
            claims_ZF.to_csv(outfile, index=False)


class AddWrpIdColumn(luigi.Task):
    """Task to add WRPID column so that it is known when the voucher was invoiced and for which plant"""

    def requires(self):
        return FilterClaims()

    def output(self):
        return luigi.LocalTarget(MyGlobals().data_folder + 'ZF_WRPID_Column.csv', format=UTF8)

    def run(self):
        claims_ZF = pd.read_csv(self.input().open('r'), encoding='utf-8',
                                parse_dates=['HM Claim Recognition Date (yyyy/mm/dd)',
                                             'Repair Order Date (yyyy/mm/dd)', 'Production Date (yyyy/mm/dd)'],
                                dtype={'Failed Part No. (1-5)': str, 'Transmission Serial No.': str,
                                       'Local Claim No.': str,
                                       'HM Claim No.': str,
                                       'Repair Dealer No.': str})

        year = MyGlobals().end_voucher_date[2:4]
        month = MyGlobals().end_voucher_date[5:7]

        claims_ZF = claims_ZF.assign(WRPID='WRP219' + MyGlobals().export_plant + month + year)

        with self.output().open('w') as outfile:
            claims_ZF.to_csv(outfile, index=False)


class AddReplPart5(luigi.Task):
    """Task to add REPLPART5 column which is needed to obtain its corresponding reference percentage"""

    def requires(self):
        return AddWrpIdColumn()

    def output(self):
        return luigi.LocalTarget(MyGlobals().data_folder + 'ZF_ReplPart5.csv', format=UTF8)

    def run(self):
        claims_ZF = pd.read_csv(self.input().open('r'), encoding='utf-8',
                                parse_dates=['HM Claim Recognition Date (yyyy/mm/dd)',
                                             'Repair Order Date (yyyy/mm/dd)', 'Production Date (yyyy/mm/dd)'],
                                dtype={'Failed Part No. (1-5)': str, 'Transmission Serial No.': str,
                                       'Local Claim No.': str, 'HM Claim No.': str, 'Repair Dealer No.': str})

        claims_ZF = claims_ZF.assign(
            REPL_PART5=claims_ZF['Replacement Part No. (1-13)'].str[:5])

        with self.output().open('w') as outfile:
            claims_ZF.to_csv(outfile, index=False)


class AddEndVoucherDate(luigi.Task):
    """Task to add END_VOUCHER_DATE column"""

    def requires(self):
        return AddReplPart5()

    def output(self):
        return luigi.LocalTarget(MyGlobals().data_folder + 'ZF_End_Voucher_Date.csv', format=UTF8)

    def run(self):
        claims_ZF = pd.read_csv(self.input().open('r'), encoding='utf-8',
                                parse_dates=['HM Claim Recognition Date (yyyy/mm/dd)',
                                             'Repair Order Date (yyyy/mm/dd)', 'Production Date (yyyy/mm/dd)'],
                                dtype={'Failed Part No. (1-5)': str, 'Transmission Serial No.': str,
                                       'Local Claim No.': str, 'HM Claim No.': str, 'Repair Dealer No.': str,
                                       'REPL_PART5': str})

        claims_ZF = claims_ZF.assign(END_VOUCHER_DATE=datetime.strptime(MyGlobals().end_voucher_date,
                                                                        "%Y-%m-%d"))

        with self.output().open('w') as outfile:
            claims_ZF.to_csv(outfile, index=False)


class AddTransSerialNo(luigi.Task):
    """Task to add TRANS_SERIAL_NO.  The transmission serial number is broken up in 2 columns in FQS-3.
        So we're just simply concatenating the 2 columns together."""

    def requires(self):
        return AddEndVoucherDate()

    def output(self):
        return luigi.LocalTarget(MyGlobals().data_folder + 'ZF_Trans_Serial_No.csv', format=UTF8)

    def run(self):
        claims_ZF = pd.read_csv(self.input().open('r'), encoding='utf-8',
                                parse_dates=['HM Claim Recognition Date (yyyy/mm/dd)',
                                             'Repair Order Date (yyyy/mm/dd)', 'Production Date (yyyy/mm/dd)'],
                                dtype={'Failed Part No. (1-5)': str, 'Transmission Serial No.': str,
                                       'Local Claim No.': str, 'HM Claim No.': str, 'Repair Dealer No.': str,
                                       'REPL_PART5': str})

        claims_ZF = claims_ZF.assign(TRANS_SERIAL_NO=claims_ZF['Transmission Type Code'] +
                                     # Excel removed leading zeroes from serial no, so need to add them back in
                                     claims_ZF['Transmission Serial No.'].apply(lambda x: x.zfill(7)))

        with self.output().open('w') as outfile:
            claims_ZF.to_csv(outfile, index=False)


class AddAsnReceiveDate(luigi.Task):
    """Task to add ASN_RECEIVE_DATE column.  This date is needed as it is the start of ZF mission warranty.
       When we have missing ASN_RECEIVE_DATEs, forward fill using previous ASN receive date.
       This is in ZF's favor, but Honda is ok with this method as it will be impossible to obtain
       all ASN receive dates from ZF Germany.  Cannot use Engine Off minus 4 days because there is time lag
       for transmissions to arrive at IPS for parts shipped outside of North America.
       Later will create 'TransDTF' column which is defined as RO date minus ASN received date.
       NOTE: You will need access to DSS server."""

    def requires(self):
        return AddTransSerialNo()

    def output(self):
        return luigi.LocalTarget(MyGlobals().data_folder + 'ZF_ASN_REC_DATE.csv', format=UTF8)

    def run(self):
        claims_ZF = pd.read_csv(self.input().open('r'), encoding='utf-8',
                                parse_dates=['HM Claim Recognition Date (yyyy/mm/dd)', 'AE-OFF Date',
                                             'Repair Order Date (yyyy/mm/dd)', 'Production Date (yyyy/mm/dd)'],
                                dtype={'Failed Part No. (1-5)': str, 'Transmission Serial No.': str,
                                       'Local Claim No.': str, 'HM Claim No.': str, 'Repair Dealer No.': str,
                                       'REPL_PART5': str})

        #username_m = getpass("Enter your IBM mainframe user id: ")
        #password_m = getpass("Enter your IBM mainframe password: ")
        username_m = os.environ['windowsuser']
        password_m = os.environ['mainframepwd']

        cnxn_string = 'DSN=DSSOGW01;UID=' + username_m + ';PWD=' + password_m

        cnxn = pyodbc.connect(cnxn_string)
        cursor = cnxn.cursor()

        sql = """
        SELECT
            RTRIM(TRANS_SERIAL_NO) AS TRANS_SERIAL_NO,
            ASN_RECEIVE_DATE

        FROM
            WAR.WRTRN1
            
        WHERE
            TRANS_SERIAL_NO LIKE 'Q%'
        """

        try:
            print("Obtaining ASN records 20,000 rows at a time due to large size of data.  Please wait...")
            asn = pd.DataFrame()
            for chunk in pd.read_sql(sql, cnxn, index_col=None, parse_dates=['ASN_RECEIVE_DATE'], chunksize=20000):
                asn = pd.concat([asn, chunk])

            # Close connections
            cursor.close()
            cnxn.close()
        except:
            cursor.close()
            cnxn.close()
            print("Error connecting to DSN server")
        print("Finished obtaining ASN records")

        # LEFT JOIN to the ASN data to the claims_ZF data to add on the ASN_RECEIVE_DATE
        claims_ZF = pd.merge(claims_ZF, asn, how='left', left_on='TRANS_SERIAL_NO', right_on='TRANS_SERIAL_NO')

        # Forward-Fill missing ASN_RECEIVE_DATEs with the date from a previous row
        claims_ZF.sort_values(by=['TRANS_SERIAL_NO'], inplace=True)
        claims_ZF['ASN_RECEIVE_DATE'].fillna(method='ffill', inplace=True)

        # Use engine off date minus 4 days when we have missing ASN_RECEIVE_DATEs (we reverted back to using FFILL)
        # claims_ZF['ASN_RECEIVE_DATE'].fillna(value=claims_ZF['AE-OFF Date'] - pd.Timedelta('4 days'), inplace=True)

        with self.output().open('w') as outfile:
            claims_ZF.to_csv(outfile, index=False)


class AddTransDTF(luigi.Task):
    """Task to create TransDTF ("transmission days to failure") column = RO date minus ASN received date"""

    def requires(self):
        return AddAsnReceiveDate()

    def output(self):
        return luigi.LocalTarget(MyGlobals().data_folder + 'ZF_Trans_DTF.csv', format=UTF8)

    def run(self):
        claims_ZF = pd.read_csv(self.input().open('r'), encoding='utf-8',
                                parse_dates=['HM Claim Recognition Date (yyyy/mm/dd)', 'AE-OFF Date',
                                             'Repair Order Date (yyyy/mm/dd)',
                                             'Production Date (yyyy/mm/dd)','ASN_RECEIVE_DATE'],
                                dtype={'Failed Part No. (1-5)': str, 'Transmission Serial No.': str,
                                       'Local Claim No.': str, 'HM Claim No.': str, 'Repair Dealer No.': str,
                                       'REPL_PART5': str})

        claims_ZF = claims_ZF.assign(TransDTF=(claims_ZF['Repair Order Date (yyyy/mm/dd)'] -
                                                       claims_ZF['ASN_RECEIVE_DATE']).apply(lambda x: x.days))

        with self.output().open('w') as outfile:
            claims_ZF.to_csv(outfile, index=False)


class AddEquotePartNum(luigi.Task):
    """Task to add E-Quote formatted part number column which has the format of: '20021' + trans type code"""

    def requires(self):
        return AddTransDTF()

    def output(self):
        return luigi.LocalTarget(MyGlobals().data_folder + 'ZF_Equote_Part_No.csv', format=UTF8)

    def run(self):
        claims_ZF = pd.read_csv(self.input().open('r'), encoding='utf-8',
                                parse_dates=['HM Claim Recognition Date (yyyy/mm/dd)', 'AE-OFF Date',
                                             'Repair Order Date (yyyy/mm/dd)', 'Production Date (yyyy/mm/dd)',
                                             'ASN_RECEIVE_DATE'],
                                dtype={'Failed Part No. (1-5)': str, 'Transmission Serial No.': str,
                                       'Local Claim No.': str, 'HM Claim No.': str, 'Repair Dealer No.': str,
                                       'Replacement Part No. (1-13)': str, 'REPL_PART5': str})

        claims_ZF = claims_ZF.assign(EQUOTE_PART_NUM='20021' +
                                             claims_ZF['Transmission Type Code'].str.slice(start=1, stop=4))

        with self.output().open('w') as outfile:
            claims_ZF.to_csv(outfile, index=False)


class AddMassProUSD(luigi.Task):
    """Task to add mass production part cost at time of failure (RO date).
       DEPENDENCY: Requires access to DSN server."""

    def requires(self):
        return AddEquotePartNum()

    def output(self):
        return luigi.LocalTarget(MyGlobals().data_folder + 'ZF_MassProUSD.csv', format=UTF8)

    def run(self):
        claims_ZF = pd.read_csv(self.input().open('r'), encoding='utf-8',
                                parse_dates=['HM Claim Recognition Date (yyyy/mm/dd)', 'AE-OFF Date',
                                             'Repair Order Date (yyyy/mm/dd)', 'Production Date (yyyy/mm/dd)',
                                             'ASN_RECEIVE_DATE'],
                                dtype={'Failed Part No. (1-5)': str, 'Transmission Serial No.': str,
                                       'Local Claim No.': str, 'HM Claim No.': str, 'Repair Dealer No.': str,
                                       'Replacement Part No. (1-13)': str, 'REPL_PART5': str})

        #username_m = getpass("Enter your IBM mainframe user id: ")
        #password_m = getpass("Enter your IBM mainframe password: ")
        username_m = os.environ['windowsuser']
        password_m = os.environ['mainframepwd']

        cnxn_string = 'DSN=DSNOGW01;UID=' + username_m + ';PWD=' + password_m

        cnxn = pyodbc.connect(cnxn_string)
        cursor = cnxn.cursor()

        sql = """
        SELECT
            *

        FROM (

        SELECT
            EXREP1.NEW_STATUS,
            EXCOD1.COD_NAME,
            EXWRK1.L1_DSG_CHG_PRT_NO,
            LEFT(EXWRK1.L1_DSG_CHG_PRT_NO,8) AS PART8,
            EXPLT1.PLNT_ACRNYM,
            EXPLT1.PLNT_DESC,
            /** Identify duplicate values using row_number() function, partitioned by part8 and modified date **/
            row_number() OVER(PARTITION BY LEFT(EXWRK1.L1_DSG_CHG_PRT_NO,8), DATE(EXREP1.DATE_MODIFIED) ORDER BY EXWRK1.Q_CAL_FINAL_TOT_CS) AS ROW_NUM,
            EXWRK1.Q_CAL_FINAL_TOT_CS,
            EXQOT1.Q_EFF_START_DT,
            EXQOT1.Q_EFF_END_DT,
            DATE(EXREP1.DATE_MODIFIED) AS APPROVED_DATE

        FROM
            EQX.EXWRK1 EXWRK1

            INNER JOIN EQX.EXQPL1 EXQPL1 ON
                EXWRK1.SUPLR_STG_ID = EXQPL1.SUPLR_STG_ID

            INNER JOIN EQX.EXPLT1 EXPLT1 ON
                EXPLT1.PLNT_ID = EXQPL1.PLNT_ID

            INNER JOIN EQX.EXREP1 EXREP1 ON
                EXWRK1.WRK_ID = EXREP1.WRK_ID

            INNER JOIN EQX.EXQOT1 EXQOT1 ON
                EXWRK1.SUPLR_STG_ID = EXQOT1.SUPLR_STG_ID

            LEFT JOIN EQX.EXSPP1 EXSPP1 ON
                EXWRK1.SUPLR_NO = EXSPP1.SUPLR_NO

            /** Code value can be used more than once based on COD_DOMAIN.  Only want the ones related to 'WORK_LIST_STATUS' **/
            LEFT JOIN (
                SELECT *

                FROM
                    EQX.EXCOD1

                WHERE
                    COD_DOMAIN = 'WORK_LIST_STATUS'
            ) EXCOD1 ON
                EXREP1.NEW_STATUS = EXCOD1.COD_VALUE

        WHERE
            EXWRK1.SUPLR_NO = '518227'
            AND EXWRK1.L1_DSG_CHG_PRT_NO LIKE '200215%'
            AND EXCOD1.COD_NAME = 'Quote Approved MP'

        ORDER BY
            PART8,
            DATE(EXREP1.DATE_MODIFIED),
            row_number() OVER(PARTITION BY LEFT(EXWRK1.L1_DSG_CHG_PRT_NO,8), DATE(EXREP1.DATE_MODIFIED) ORDER BY EXWRK1.Q_CAL_FINAL_TOT_CS)

        ) AS TEMP

        WHERE
            ROW_NUM = 1
        """

        try:
            print("Obtaining E-Quote mass pro part costs...")
            equote = pd.read_sql(sql, cnxn, index_col=None, parse_dates=['APPROVED_DATE'])
            cursor.close()
            cnxn.close()
        except:
            # Close connections
            cursor.close()
            cnxn.close()
            print("Error connecting to DSN server")
        print("Finished obtaining E-Quote mass pro part costs")

        def getMassProCost(row):
            return equote[(equote['PART8'] == row['EQUOTE_PART_NUM']) & (equote['APPROVED_DATE'] == 
                          equote[(equote['PART8'] == row['EQUOTE_PART_NUM'])
                          & (equote['APPROVED_DATE'] <= row['Repair Order Date (yyyy/mm/dd)'])]['APPROVED_DATE']
                          .max())].sort_values(by=['Q_CAL_FINAL_TOT_CS'])['Q_CAL_FINAL_TOT_CS'].values[0]

        claims_ZF['MassProCost_USD'] = claims_ZF.apply(getMassProCost, axis='columns')
        claims_ZF = claims_ZF.assign(MassProCostX205_USD=claims_ZF['MassProCost_USD'] * 2.05)

        with self.output().open('w') as outfile:
            claims_ZF.to_csv(outfile, index=False)


class AddRowNum(luigi.Task):
    """Task to add ROW_NUM column to aide in identifying duplicate rows and we will need to eventually 'zero out'
       duplicate values to prevent double-charging of supplier."""

    def requires(self):
        return AddMassProUSD()

    def output(self):
        return luigi.LocalTarget(MyGlobals().data_folder + 'ZF_Row_Num.csv', format=UTF8)

    def run(self):
        claims_ZF = pd.read_csv(self.input().open('r'), encoding='utf-8',
                                parse_dates=['HM Claim Recognition Date (yyyy/mm/dd)', 'AE-OFF Date',
                                             'Repair Order Date (yyyy/mm/dd)', 'Production Date (yyyy/mm/dd)',
                                             'ASN_RECEIVE_DATE'],
                                dtype={'Failed Part No. (1-5)': str, 'Transmission Serial No.': str,
                                       'Local Claim No.': str, 'HM Claim No.': str, 'Repair Dealer No.': str,
                                       'Replacement Part No. (1-13)': str, 'REPL_PART5': str})

        claims_ZF['ROW_NUM'] = claims_ZF.sort_values(by=['Replacement Part No. (1-13)']).groupby(['HM Claim No.']).cumcount() + 1

        with self.output().open('w') as outfile:
            claims_ZF.to_csv(outfile, index=False)


class CreateReferencePercentages(luigi.Task):
    """Task that creates the reference market percentage data based on TPLs through end voucher date"""

    def requires(self):
        return AddRowNum()

    def output(self):
        return luigi.LocalTarget(MyGlobals().data_folder + 'ZF_Reference_Market_Percentages.csv', format=UTF8)

    def run(self):
        #username = getpass("Enter your Windows NT user ID: ")
        #password = getpass("Enter your Windows NT password: ")
        username = os.environ['windowsuser']
        password = os.environ['windowspwd']

        cnxn_string = 'DSN=MMP-SQLP-CQP;UID=' + username + ';PWD=' + password

        cnxn = pyodbc.connect(cnxn_string)
        cursor = cnxn.cursor()

        sql = open(r'\\mmpapp02\mq_db\wrp\ZF_ATM_WRP_Project\version4\sql\Getting_Fixed_Percentages_Query.txt').read()

        try:
            print('Obtaining CQ TPL data...')
            df_tpl = pd.read_sql(sql, cnxn, index_col=None, parse_dates=['ANALYZED_DATE'],
                                 params=[MyGlobals().end_voucher_date, MyGlobals().end_voucher_date,
                                         MyGlobals().end_voucher_date, MyGlobals().end_voucher_date,
                                         MyGlobals().end_voucher_date, MyGlobals().end_voucher_date]
                                 )

            # Close connections
            cursor.close()
            cnxn.close()
            print('Finished obtaining CQ TPL data')
        except:
            cursor.close()
            cnxn.close()
            print('Error connecting to CQ server')


        # Ensure CQ TPL data is <= end voucher date
        criteria = df_tpl['ANALYZED_DATE'] <= MyGlobals().end_voucher_date
        cq_tpl_final = df_tpl[criteria]

        # Save the raw CQ data for ZF
        with open(Path.cwd() / MyGlobals().data_folder / 'ZF_CQ_TPL_Raw_Data.csv', 'w') as outfile:
            cq_tpl_final.to_csv(outfile, index=False)

        pivot = pd.pivot_table(data=cq_tpl_final, index=['MODEL_YEAR','SHORT_PART_NO'], columns='CONCLUSION_DESC_TXT',
                               aggfunc='count', fill_value=0)

        pivot = pivot['ANALYZED_DATE']
        pivot.reset_index(level=[0,1], inplace=True)
        pivot = pivot.assign(TOTAL_QTY=pivot['Cause Unknown'] + pivot['Customer abuse'] + pivot['Dealer Error'] +
                             pivot['Honda Mfg. Defect'] + pivot['Honda Supplied Part'] + pivot['NTF'] + 
                             pivot['Spec. Related-Honda Drawing'] + pivot['Spec. Related-Supplier Drawing'] + 
                             pivot['Supplier Mfg. Defect'])
                             
        pivot = pivot.assign(SUPP_RESP_QTY = pivot['Cause Unknown'] * 0.5 + pivot['Customer abuse'] * 0 + pivot['Dealer Error'] * 0 +
                             pivot['Honda Mfg. Defect'] * 0 + pivot['Honda Supplied Part'] * 0 + pivot['NTF'] * 0 + 
                             pivot['Spec. Related-Honda Drawing'] * 0.1 + pivot['Spec. Related-Supplier Drawing'] * 0.8 + 
                             pivot['Supplier Mfg. Defect'] * 1)

        pivot = pivot.assign(SUPP_RESP_PERC=pivot['SUPP_RESP_QTY'] / pivot['TOTAL_QTY'])

        # Also save the pivoted CQ TPL data that shows the CQ conclusion categories and their corresponding percentages
        with open(Path.cwd() / MyGlobals().data_folder / 'ZF_CQ_TPL_Pivoted.csv', 'w') as outfile:
            pivot.to_csv(outfile, index=False)


        ref_market_percentages = pivot[['MODEL_YEAR', 'SHORT_PART_NO', 'SUPP_RESP_PERC']]

        with self.output().open('w') as outfile:
            ref_market_percentages.to_csv(outfile, index=False)


class AddReferencePercentages(luigi.Task):
    """Task to add reference market percentage column"""

    def requires(self):
        return {'claims': AddRowNum(), 'tpl': CreateReferencePercentages()}

    def output(self):
        return luigi.LocalTarget(MyGlobals().data_folder + 'ZF_Reference_Market_Percentages_Added.csv', format=UTF8)

    def run(self):
        claims_ZF = pd.read_csv(self.input()['claims'].open('r'), encoding='utf-8',
                                parse_dates=['HM Claim Recognition Date (yyyy/mm/dd)', 'AE-OFF Date',
                                             'Repair Order Date (yyyy/mm/dd)', 'Production Date (yyyy/mm/dd)',
                                             'ASN_RECEIVE_DATE'],
                                dtype={'Failed Part No. (1-5)': str, 'Transmission Serial No.': str,
                                       'Local Claim No.': str, 'HM Claim No.': str, 'Repair Dealer No.': str,
                                       'Replacement Part No. (1-13)': str, 'Model Year': int, 'REPL_PART5': str})

        cq_tpl = pd.read_csv(self.input()['tpl'].open('r'),
                             dtype={'MODEL_YEAR': int, 'SHORT_PART_NO': str, 'SUPP_RESP_PERC': float})

        claims_merged = pd.merge(claims_ZF, cq_tpl, how='left', left_on=['Model Year', 'REPL_PART5'], 
                                 right_on=['MODEL_YEAR', 'SHORT_PART_NO'])

        del claims_merged['MODEL_YEAR']
        del claims_merged['SHORT_PART_NO']

        with self.output().open('w') as outfile:
            claims_merged.to_csv(outfile, index=False)


class CreateDummyReplpart5(luigi.Task):
    """Task whereby a part # that does not have a corresponding reference percentage, its part # is replaced by
       the transmissioin assembly part # (06200)"""

    def requires(self):
        return AddReferencePercentages()

    def output(self):
        return luigi.LocalTarget(MyGlobals().data_folder + 'ZF_Claims_Dummy_Replpart5_Added.csv', format=UTF8)

    def run(self):
        claims_ZF = pd.read_csv(self.input().open('r'), encoding='utf-8',
                                parse_dates=['HM Claim Recognition Date (yyyy/mm/dd)', 'AE-OFF Date',
                                             'Repair Order Date (yyyy/mm/dd)', 'Production Date (yyyy/mm/dd)',
                                             'ASN_RECEIVE_DATE'],
                                dtype={'Failed Part No. (1-5)': str, 'Transmission Serial No.': str,
                                       'Local Claim No.': str, 'HM Claim No.': str, 'Repair Dealer No.': str,
                                       'Replacement Part No. (1-13)': str, 'REPL_PART5': str})

        claims_ZF = claims_ZF.assign(REPL_PART5_NEW=np.where(claims_ZF['SUPP_RESP_PERC'].isnull(), '06200',
                                     claims_ZF['REPL_PART5']
                                     ))

        with self.output().open('w') as outfile:
            claims_ZF.to_csv(outfile, index=False)


class AddReferencePercentagesFinal(luigi.Task):
    """Task to add reference market percentage column"""

    def requires(self):
        return {'claims': CreateDummyReplpart5(), 'tpl': CreateReferencePercentages()}

    def output(self):
        return luigi.LocalTarget(MyGlobals().data_folder + 'ZF_Reference_Market_Percentages_FINAL_Added.csv',
                                 format=UTF8)

    def run(self):
        claims_ZF = pd.read_csv(self.input()['claims'].open('r'), encoding='utf-8',
                                parse_dates=['HM Claim Recognition Date (yyyy/mm/dd)', 'AE-OFF Date',
                                             'Repair Order Date (yyyy/mm/dd)', 'Production Date (yyyy/mm/dd)',
                                             'ASN_RECEIVE_DATE'],
                                dtype={'Failed Part No. (1-5)': str, 'Transmission Serial No.': str,
                                       'Local Claim No.': str, 'HM Claim No.': str, 'Repair Dealer No.': str,
                                       'Replacement Part No. (1-13)': str, 'Model Year': int, 'REPL_PART5': str,
                                       'REPL_PART5_NEW': str})

        cq_tpl = pd.read_csv(self.input()['tpl'].open('r'),
                             dtype={'MODEL_YEAR': int, 'SHORT_PART_NO': str, 'SUPP_RESP_PERC': float})

        claims_merged = pd.merge(claims_ZF, cq_tpl, how='left', left_on=['Model Year', 'REPL_PART5_NEW'],
                                 right_on=['MODEL_YEAR', 'SHORT_PART_NO'], suffixes=['', '_NEW'])

        claims_merged.drop(['MODEL_YEAR', 'SHORT_PART_NO'], axis='columns', inplace=True)

        with self.output().open('w') as outfile:
            claims_merged.to_csv(outfile, index=False)


class AddWrpVoucherAmounts(luigi.Task):
    """Task to multiply the actual total cost and calcualted total cost by the supplier responsible percentage.
       Then chooses the minimum of:
           (approved total cost after perc, MassProx205_USD)
    """

    def requires(self):
        return AddReferencePercentagesFinal()

    def output(self):
        return luigi.LocalTarget(MyGlobals().data_folder + 'ZF_Initial_Final_WRP_Amounts.csv', format=UTF8)

    def run(self):
        claims_ZF = pd.read_csv(self.input().open('r'), encoding='utf-8',
                                parse_dates=['HM Claim Recognition Date (yyyy/mm/dd)', 'AE-OFF Date',
                                             'Repair Order Date (yyyy/mm/dd)', 'Production Date (yyyy/mm/dd)',
                                             'ASN_RECEIVE_DATE'],
                                dtype={'Failed Part No. (1-5)': str, 'Transmission Serial No.': str,
                                       'Local Claim No.': str, 'HM Claim No.': str, 'Repair Dealer No.': str,
                                       'Replacement Part No. (1-13)': str, 'Model Year': int, 'REPL_PART5': str,
                                       'REPL_PART5_NEW': str})

        claims_ZF = claims_ZF.assign(Approved_Total_Amount_USD_After_Perc=claims_ZF['Approved Total Amount (USD)'] *
                                     claims_ZF['SUPP_RESP_PERC_NEW'])
                                    

        claims_ZF = claims_ZF.assign(WRP_VOUCHER_AMT_USD_INITIAL=claims_ZF[['Approved_Total_Amount_USD_After_Perc',
                                     'MassProCostX205_USD']].min(axis='columns'))

        claims_ZF = claims_ZF.assign(WRP_VOUCHER_AMT_USD_FINAL = claims_ZF['WRP_VOUCHER_AMT_USD_INITIAL'])

        with self.output().open('w') as outfile:
            claims_ZF.to_csv(outfile, index=False)


class AddWarrantyRestrictions(luigi.Task):
    """Task to only include records with WRP_VOUCHER_AMT_USD_INITIAL > 0.1
       and TransDTF <= 1460 (4 years) and vehicle miles <= 70000"""

    def requires(self):
        return AddWrpVoucherAmounts()

    def output(self):
        return luigi.LocalTarget(MyGlobals().data_folder + 'ZF_Warranty_Limits_Added.csv', format=UTF8)

    def run(self):
        claims_ZF = pd.read_csv(self.input().open('r'), encoding='utf-8',
                                parse_dates=['HM Claim Recognition Date (yyyy/mm/dd)', 'AE-OFF Date',
                                             'Repair Order Date (yyyy/mm/dd)', 'Production Date (yyyy/mm/dd)',
                                             'ASN_RECEIVE_DATE'],
                                dtype={'Failed Part No. (1-5)': str, 'Transmission Serial No.': str,
                                       'Local Claim No.': str, 'HM Claim No.': str, 'Repair Dealer No.': str,
                                       'Replacement Part No. (1-13)': str, 'Model Year': int, 'REPL_PART5': str,
                                       'REPL_PART5_NEW': str})

        criteria1 = claims_ZF['WRP_VOUCHER_AMT_USD_INITIAL'] > 0.1
        criteria2 = claims_ZF['TransDTF'] <= 1460
        criteria3 = claims_ZF['Mileage (Mile)'] <= 70000

        # Since we've removed the calculated costs columns, we only need to keep records with row # = 1
        criteria4 = claims_ZF['ROW_NUM'] == 1

        claims_final = claims_ZF[criteria1 & criteria2 & criteria3 & criteria4]

        with self.output().open('w') as outfile:
            claims_final.to_csv(outfile, index=False)


class CleanUpColumnNames(luigi.Task):
    """Task to remove periods or blank spaces from the column names"""

    def requires(self):
        return AddWarrantyRestrictions()

    def output(self):
        return luigi.LocalTarget(MyGlobals().data_folder + 'ZF_Clean_Column_Names.csv', format=UTF8)

    def run(self):
        claims_ZF = pd.read_csv(self.input().open('r'), encoding='utf-8',
                                parse_dates=['HM Claim Recognition Date (yyyy/mm/dd)', 'AE-OFF Date',
                                             'Repair Order Date (yyyy/mm/dd)', 'Production Date (yyyy/mm/dd)',
                                             'ASN_RECEIVE_DATE'],
                                dtype={'Failed Part No. (1-5)': str, 'Transmission Serial No.': str,
                                       'Local Claim No.': str, 'HM Claim No.': str, 'Repair Dealer No.': str,
                                       'Replacement Part No. (1-13)': str, 'Model Year': int, 'REPL_PART5': str,
                                       'REPL_PART5_NEW': str})

        # Remove periods or blank spaces from the column namems
        column_names = [column.replace('.', '').replace(' ','_') for column in claims_ZF.columns]
        claims_ZF.columns = column_names

        with self.output().open('w') as outfile:
            claims_ZF.to_csv(outfile, index=False)


if __name__ == '__main__':
    luigi.build([CleanUpColumnNames()], local_scheduler=True)