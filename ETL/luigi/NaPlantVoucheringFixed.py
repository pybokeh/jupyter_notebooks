# PURPOSE: To prepare data that will be used to voucher supplier ("ZF") on behalf of North American plants
#          based on claims without part analysis, and therefore, using fixed percentages.
#
# Tooling / Technology Stack:
#   - Python 3.6
#   - Pandas for data extraction and transformation
#   - pyodbc for accessing databases
#   - Luigi data pipelining framework for ease of data tracking and validation

from datetime import datetime
from getpass import getpass
import luigi
import numpy as np
import os
import pandas as pd
import pyodbc


class MyGlobals(luigi.Config):
    """Define 'global' parameter values here
    
    Global Variables
    ----------------
    mydate: Python Date
        today's date used as part of folder where outputs will be saved
    data_folder: str
        base folder location where outputs will be saved
    start_voucher_date: str
        start voucher date
    end_voucher_date: str
        end voucher date
    fixed_model_years: str
        comma delimited model years that will be fixed (aka parts will no longer be analyzed)
    fixed_end_date: str
        end date that the CQ TPLs data was used for calculating fixed percentages, usually same as end voucher date
    """

    mydate = datetime.today()
    data_folder = 'outputs/text_files/NorthAmericanPlants/FIXED/' + datetime.strftime(mydate, "%Y-%m-%d") + '/'

    start_voucher_date = input("Enter start voucher date (YYYY-MM-DD): ")
    end_voucher_date = input("Enter end voucher date (YYYY-MM-DD): ")
    part_cost_factor = input("Enter part cost factor (0.#): ")
    handling_cost_factor = input("Enter handling cost factor (0.#): ")
    honda_labor_rate = input("Enter Honda hourly labor rate: ")
    acura_labor_rate = input("Enter Acura hourly labor rate: ")
    fixed_model_years = input("Enter fixed model years separated by comma: ")
    fixed_end_date = input("Enter fixed end date (YYYY-MM-DD): ")


class CreateReadMe(luigi.Task):
    """Task to create a README.txt file containing the input parameters that the user entered.
       It is recommended that the user reads this to confirm that they have entered the correct parameters
       prior to validating the data.
    """

    def output(self):
        return luigi.LocalTarget(MyGlobals().data_folder + 'README.txt')

    def run(self):
        message = "Start Voucher Date: " + MyGlobals().start_voucher_date + "\n" + \
                  "End Voucher Date: " + MyGlobals().end_voucher_date + "\n" + \
                  "Honda hourly labor rate: " + MyGlobals().honda_labor_rate + "\n" + \
                  "Acura hourly labor rate: " + MyGlobals().acura_labor_rate + "\n" + \
                  "Part cost factor (0.##): " + MyGlobals().part_cost_factor + "\n" + \
                  "Handling cost factor (0.##): " + MyGlobals.handling_cost_factor + "\n" + \
                  "Fixed model years: " + MyGlobals.fixed_model_years + "\n" + \
                  "Fixed end date: " + MyGlobals.fixed_end_date

        with self.output().open('w') as outfile:
            outfile.write(message)


class GetCqTpls(luigi.ExternalTask):
    """Task to obtain CQ TPLs that will be used to calculate fixed percentages.  'fixed_end_date' global variable that
       the user provided will be used to determine the data set range to use.
       NOTE: Access to MMP-SQLP-CQP is required
    """

    def requires(self):
        return CreateReadMe()

    def output(self):
        return luigi.LocalTarget(MyGlobals().data_folder + 'ZF_TPLs.csv')

    def run(self):
        #username = getpass('Enter your Windows NT user id: ')
        #password = getpass('Enter your Windows NT password: ')
        username = os.environ['windowsuser']
        password = os.environ['windowspwd']

        cnxn_string = 'DSN=MMP-SQLP-CQP;UID=' + username + ';PWD=' + password

        cnxn = pyodbc.connect(cnxn_string)
        cursor = cnxn.cursor()

        # NOTE: this is a parameterized SQL requiring the fixed_end_date from the user
        sql = open(r'\\mmpapp02\mq_db\wrp\ZF_ATM_WRP_Project\version4\sql\Getting_Fixed_Percentages_Query.txt').read()

        try:
            print('###  Connecting to CQ server...###')
            cq_tpls = pd.read_sql(sql, cnxn, index_col=None,
                                  parse_dates=['SUBMITTED_DATE','REOPENED_SUBMITTED_DATE','ANALYZED_DATE'],
                                  params=[MyGlobals().fixed_end_date, MyGlobals().fixed_end_date,
                                          MyGlobals().fixed_end_date, MyGlobals().fixed_end_date,
                                          MyGlobals().fixed_end_date, MyGlobals().fixed_end_date])

            # Close connections
            cursor.close()
            cnxn.close()
        except pyodbc.Error as err:
            cursor.close()
            cnxn.close()
            print('ERROR: Problems connecting to CQ server:')
            print(err)
        print('###  Finished obtaining CQ TPLs for fixed percentage calculations  ###')

        cq_tpls['MODEL_NAME'] = cq_tpls['MODEL_NAME'].replace('TL', 'TLX').str.strip().str.upper()
        cq_tpls['MODEL_YEAR'] = cq_tpls['MODEL_YEAR'].str.strip()

        with self.output().open('w') as outfile:
            cq_tpls.to_csv(outfile, index=False)


class GetFixedPercentages(luigi.Task):
    """Task to obtain fixed percentages from the MS Access database.  Depending on what's agreed upon,
       we can roll up fixed percentages at the year, model, and part # level OR
       we can roll up fixed percentages at the year and part # level"""

    def requires(self):
        return GetCqTpls()

    def output(self):
        return luigi.LocalTarget(MyGlobals().data_folder + 'ZF_Fixed_Percentages.csv')

    def run(self):


        conn_str = (
            r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'
            # r'DBQ=\\mmpapp02\mq_db\wrp\ZF_ATM_WRP_Project\DAT\WRP_DAT_ZF.accdb;'
            r'DBQ=\\mmpapp02\mq_db\wrp\ZF_ATM_WRP_Project\version4\databases\WRP_DAT_ZF.accdb;'
        )
        cnxn = pyodbc.connect(conn_str)
        cursor = cnxn.cursor()

        sql = """
        SELECT
            MODEL_YEAR,
            SHORT_PART_NO,
            SUPP_FIXED_PERC,
            ANALYSIS_END_MTH

        FROM
            tbl_Fixed_Percentages_Yr_Part 
        """

        try:
            fixed_percentages = pd.read_sql(sql, cnxn)

            # Close connections
            cursor.close()
            cnxn.close()
            print(sql)
        except:
            print("Error connecting to database")
            cursor.close()
            cnxn.close()


        with self.output().open('w') as outfile:
            fixed_percentages.to_csv(outfile, index=False)


class GetClaClaimsFixed(luigi.Task):
    """Task to obtain CLA (approved) claims with or without TPLs and add supplier percent responsibility
       NOTE: Currently, using supplier percent responsibility at the year, model and part #
       NOTE: Access to MMP-SQLP-CQP is required
    """

    def requires(self):
        return GetFixedPercentages()

    def output(self):
        return luigi.LocalTarget(MyGlobals().data_folder + 'ZF_CLA_Claims.csv')

    def run(self):
        fixed_percentages = pd.read_csv(self.input().open('r'), dtype={'SHORT_PART_NO': 'category', 'MODEL_YEAR': 'category'})

        #username = getpass('Enter your Windows NT user id: ')
        #password = getpass('Enter your Windows NT password: ')
        username = os.environ['windowsuser']
        password = os.environ['windowspwd']

        cnxn_string = 'DSN=MMP-SQLP-CQP;UID=' + username + ';PWD=' + password

        cnxn = pyodbc.connect(cnxn_string)
        cursor = cnxn.cursor()

        # sql = open(r'\\mmpapp02\mq_db\wrp\ZF_ATM_WRP_Project\version2\sql\Main_Query_V2_All_TPLs.txt').read()
        # Use parameter-less version of the main query
        sql = open(r'\\mmpapp02\mq_db\wrp\ZF_ATM_WRP_Project\version4\sql\Main_Query_All_TPLs.txt').read()

        try:
            print("Obtaining CLA claim records with and without TPLs.  May take a few minutes...")
            claims = pd.read_sql(sql, cnxn, parse_dates=['SUBMITTED_DATE','REOPENED_SUBMITTED_DATE','REPAIR_ORDER_DATE',
                                                         'AF_OFF_DATE','ENGINE_BUILD_DATE'], 
                                                         index_col=None)

            # Close connections
            cursor.close()
            cnxn.close()
        except:  # When failure occurs, ensure connections are closed
            print("Error connecting to CQ server")
            cursor.close()
            cnxn.close()
        print("Finished obtaining CLA claim records with and without TPLs")

        # Convert claims with bad E-Quote part # format as Nulls and then forward fill missing E-Quote replaced part #
        claims.loc[claims['REPLACED_PART_EQUOTE_FMT']=='20021   ', 'REPLACED_PART_EQUOTE_FMT'] = np.nan
        claims.sort_values(by=['MOD_NAME','MODEL_YEAR','AF_OFF_DATE'], inplace=True)
        claims['REPLACED_PART_EQUOTE_FMT'].fillna(method='ffill', inplace=True)

        # TRANS_SERIAL_NO has trailing white spaces, so strip them out
        claims['TRANS_SERIAL_NO'] = claims['TRANS_SERIAL_NO'].str.strip()

        # Merge claims with fixed_percentages data to add SUPP_FIXED_PERC
        # Currently, using fixed percentages at the year, model, and part # level
        claims = pd.merge(claims, fixed_percentages, how='left', left_on=['MODEL_YEAR', 'REPLACED_PART5'],
                          right_on=['MODEL_YEAR', 'SHORT_PART_NO'], indicator=True)

        # Delete redundant columns as a result of the pd.merge()
        # del claims['MODEL_NAME']
        # del claims['SHORT_PART_NO']

        # To avoid confusion, delete this column
        # del claims['SUPP_RES_PER']

        with self.output().open('w') as outfile:
            claims.to_csv(outfile, index=False)


class AddWrpId(luigi.Task):
    """Task to add WRPID column - WRPID column identifies the end MMYY that the voucher was invoiced for"""

    def requires(self):
        return GetClaClaimsFixed()

    def output(self):
        return luigi.LocalTarget(MyGlobals().data_folder + 'ZF_CLA_Claim_WRP_ID.csv')

    def run(self):
        claims = pd.read_csv(self.input().open('r'),
                             parse_dates=['REPAIR_ORDER_DATE', 'AF_OFF_DATE', 'ENGINE_BUILD_DATE'],
                             dtype={'WAR_ORIG_DISTR_CDE': 'category', 'WAR_RESP_DISTR_CDE': 'category'})

        year = MyGlobals().end_voucher_date[2:4]
        month = MyGlobals().end_voucher_date[5:7]

        claims = claims.assign(WRPID='WRP219F' + month + year)

        with self.output().open('w') as outfile:
            claims.to_csv(outfile, index=False)


class AddHrlyRate(luigi.Task):
    """Task that adds the nameplate hourly rate, Honda and Acura"""

    def requires(self):
        return AddWrpId()

    def output(self):
        return luigi.LocalTarget(MyGlobals().data_folder + 'ZF_CLA_Claims_Hourly_Rate.csv')

    def run(self):
        claims = pd.read_csv(self.input().open('r'),
                             parse_dates=['REPAIR_ORDER_DATE', 'AF_OFF_DATE', 'ENGINE_BUILD_DATE'],
                             dtype={'WAR_ORIG_DISTR_CDE': 'category', 'WAR_RESP_DISTR_CDE': 'category'})

        claims['HRLY_RATE_USD'] = np.where(claims['NAMEPLATE'] == 'ACURA', int(MyGlobals().acura_labor_rate),
                                           int(MyGlobals().honda_labor_rate))

        with self.output().open('w') as outfile:
            claims.to_csv(outfile, index=False)


class AddCalculatedCosts(luigi.Task):
    """Task that adds calculated cost columns"""

    def requires(self):
        return AddHrlyRate()

    def output(self):
        return luigi.LocalTarget(MyGlobals().data_folder + 'ZF_CLA_Claims_Calculated_Costs.csv')

    def run(self):
        claims = pd.read_csv(self.input().open('r'),
                             parse_dates=['REPAIR_ORDER_DATE', 'ENGINE_BUILD_DATE', 'AF_OFF_DATE'],
                             dtype={'WAR_ORIG_DISTR_CDE': 'category', 'WAR_RESP_DISTR_CDE': 'category'})

        # claims = claims.assign(CALCULATED_PART_COST_USD=claims['DLR_NET_PRCE_AMT_USD'] *
                                                        # float(MyGlobals().part_cost_factor))

        claims = claims.assign(CALCULATED_PART_COST_USD=claims['MIN_PART_COST_USD'])

        claims['CALCULATED_FLAT_RATE_LABOR_COST_USD'] = np.where(claims['NAMEPLATE'] == 'ACURA',
                                                                 claims['FLAT_RATE_HRS_QTY'] * int(MyGlobals().acura_labor_rate),
                                                                 claims['FLAT_RATE_HRS_QTY'] * int(MyGlobals().honda_labor_rate))

        claims = claims.assign(CALCULATED_DIAGNOSTIC_LABOR_COST_USD=(claims['CLAIM_LABOR_HRS_QTY'] *
                                                                     claims['HRLY_RATE_USD']) - (claims['FLAT_RATE_HRS_QTY'] *
                                                                                                 claims['HRLY_RATE_USD']))

        claims = claims.assign(CALCULATED_HDLG_CHG_AMT_USD=claims['DLR_NET_PRCE_AMT_USD'] *
                                                           float(MyGlobals().handling_cost_factor))

        # part cost + labor cost + handling cost + sublet/freight/tax (CLA labor - WHA labor)
        claims['CALCULATED_TOTAL_COST_USD'] = np.where(claims['ACTUAL_LABOR_CHG_AMT_USD'] == 0,
                                                       claims['CALCULATED_PART_COST_USD'] + claims['CALCULATED_HDLG_CHG_AMT_USD'],
                                                       claims['CALCULATED_PART_COST_USD'] + claims['CALCULATED_FLAT_RATE_LABOR_COST_USD'] +
                                                       claims['CALCULATED_DIAGNOSTIC_LABOR_COST_USD'] + claims['CALCULATED_HDLG_CHG_AMT_USD'] +
                                                       claims['FRGT_SUBL_TAX_AMT_USD']
                                                       )

        claims = claims.assign(CALCULATED_TOTAL_LABOR_COST_USD=claims['CALCULATED_FLAT_RATE_LABOR_COST_USD'] +
                                                               claims['CALCULATED_DIAGNOSTIC_LABOR_COST_USD'])

        with self.output().open('w') as outfile:
            claims.to_csv(outfile, index=False)


class AddAsnReceiveDate(luigi.Task):
    """Task to add ASN_RECEIVE_DATE column.  This date is needed as it is the start of ZF mission warranty.
       Later will create 'TransDTF' column which is defined as RO date minus ASN received date.
       NOTE: You will need access to DSSOGW01 server."""

    def requires(self):
        return AddCalculatedCosts()

    def output(self):
        return luigi.LocalTarget(MyGlobals().data_folder + 'ZF_CLA_Claims_ASN_Receive_Date.csv')

    def run(self):
        claims = pd.read_csv(self.input().open('r'),
                             parse_dates=['REPAIR_ORDER_DATE', 'AF_OFF_DATE', 'ENGINE_BUILD_DATE'],
                             dtype={'WAR_ORIG_DISTR_CDE': 'category', 'WAR_RESP_DISTR_CDE': 'category'})

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
        except:  # When failure occurs, ensure connections are closed
            cursor.close()
            cnxn.close()
            print("Error connecting to DSN server")
        print("Finished obtaining ASN records")

        # LEFT JOIN to the ASN data to the CLA claims data to add on the ASN_RECEIVE_DATE
        claims = pd.merge(claims, asn, how='left', left_on='TRANS_SERIAL_NO', right_on='TRANS_SERIAL_NO')

        # Forward-Fill missing ASN_RECEIVE_DATEs with the date from a previous row
        # claims.sort_values(by=['MOD_NAME','MODEL_YEAR','AF_OFF_DATE'], inplace=True)
        # claims['ASN_RECEIVE_DATE'].fillna(method='ffill', inplace=True)

        with self.output().open('w') as outfile:
            claims.to_csv(outfile, index=False)


class FillAsnDate(luigi.Task):
    """Task to fill missing ASN_RECEIVE_DATE using ENG_BUILD_DATE minus 4 days and to also add TransDTF column"""

    def requires(self):
        return AddAsnReceiveDate()

    def output(self):
        return luigi.LocalTarget(MyGlobals().data_folder + 'ZF_CLA_Claims_Fill_ASN_Date.csv')

    def run(self):
        claims = pd.read_csv(self.input().open('r'), parse_dates=['REPAIR_ORDER_DATE','AF_OFF_DATE', 'ENGINE_BUILD_DATE',
            'ASN_RECEIVE_DATE'], dtype={'WAR_ORIG_DISTR_CDE': 'category', 'WAR_RESP_DISTR_CDE': 'category'})

        claims['ASN_RECEIVE_DATE'].fillna(value=claims['ENGINE_BUILD_DATE'] - pd.Timedelta('4 days'), inplace=True)

        claims = claims.assign(TransDTF = (claims['REPAIR_ORDER_DATE'] - claims['ASN_RECEIVE_DATE']).apply(lambda x: x.days))

        with self.output().open('w') as outfile:
            claims.to_csv(outfile, index=False)


class AddMassProUSD(luigi.Task):
    """Task to add mass production part cost at time of failure (RO date).
       DEPENDENCY: Requires access to DSNOGW01 server."""

    def requires(self):
        return FillAsnDate()

    def output(self):
        return luigi.LocalTarget(MyGlobals().data_folder + 'ZF_CLA_Claims_MassProUSD.csv')

    def run(self):
        claims = pd.read_csv(self.input().open('r'), parse_dates=['REPAIR_ORDER_DATE','AF_OFF_DATE','ENGINE_BUILD_DATE'],
            dtype={'WAR_ORIG_DISTR_CDE': 'category', 'WAR_RESP_DISTR_CDE': 'category'})

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
            return equote[(equote['PART8'] == row['REPLACED_PART_EQUOTE_FMT']) & (equote['APPROVED_DATE'] == 
                                        equote[(equote['PART8'] == row['REPLACED_PART_EQUOTE_FMT'])
                                        & (equote['APPROVED_DATE'] <= row['REPAIR_ORDER_DATE'])]['APPROVED_DATE']
                                        .max())].sort_values(by=['Q_CAL_FINAL_TOT_CS'])['Q_CAL_FINAL_TOT_CS'].values[0]

        print("Applying mass pro part cost x 205% calculations.  Please wait...")
        claims['MassProCost_USD'] = claims.apply(getMassProCost, axis='columns')
        claims = claims.assign(MassProCostX205_USD=claims['MassProCost_USD'] * 2.05)
        print("Finished applying mass pro part cost x 205% calculations.")

        with self.output().open('w') as outfile:
            claims.to_csv(outfile, index=False)


class AddRowNum(luigi.Task):
    """Task to add ROW_NUM column.  This column will be used to identify duplicate records due to claim adjustments."""

    def requires(self):
        return AddMassProUSD()

    def output(self):
        return luigi.LocalTarget(MyGlobals().data_folder + 'ZF_CLA_Claims_Row_Num.csv')

    def run(self):
        claims = pd.read_csv(self.input().open('r'), parse_dates=['REPAIR_ORDER_DATE', 'AF_OFF_DATE',
                             'ENGINE_BUILD_DATE'], dtype={'WAR_ORIG_DISTR_CDE': 'category', 'WAR_RESP_DISTR_CDE': 'category'})

        claims['ROW_NUM'] = claims.sort_values(by=['RECORD_DESC'], ascending=False) \
                                .groupby(['VIN_DLR_CLM_SK']).cumcount() + 1

        with self.output().open('w') as outfile:
                claims.to_csv(outfile, index=False)


class AddClaimLevelTotalCost(luigi.Task):
    """Task to add actual claim level total cost column due to claim adjustments"""

    def requires(self):
        return AddRowNum()

    def output(self):
        return luigi.LocalTarget(MyGlobals().data_folder + 'ZF_CLA_Claims_Claim_Level_Total_Cost.csv')

    def run(self):
        claims = pd.read_csv(self.input().open('r'),
                             parse_dates=['REPAIR_ORDER_DATE', 'AF_OFF_DATE', 'ENGINE_BUILD_DATE'],
                             dtype={'WAR_ORIG_DISTR_CDE': 'category', 'WAR_RESP_DISTR_CDE': 'category'})

        pivot = pd.pivot_table(claims, index='VIN_DLR_CLM_SK', values='ACTUAL_TOTAL_CHG_AMT_USD', aggfunc='sum')
        pivot.columns = ['ACTUAL_CLAIM_LEVEL_TOTAL_CHG_AMT_USD']
        pivot.reset_index(level=0, inplace=True)

        claims = pd.merge(claims, pivot, how='left', left_on='VIN_DLR_CLM_SK', right_on='VIN_DLR_CLM_SK')

        with self.output().open('w') as outfile:
                claims.to_csv(outfile, index=False)


class ZeroedOutClaimCosts(luigi.Task):
    """Task to 'zero out' cost amounts for duplicate rows to prevent double-charging of supplier"""

    def requires(self):
        return AddClaimLevelTotalCost()

    def output(self):
        return luigi.LocalTarget(MyGlobals().data_folder + 'ZF_CLA_Claims_Zeroed_Out_Costs.csv')

    def run(self):
        claims = pd.read_csv(self.input().open('r'),
                             parse_dates=['REPAIR_ORDER_DATE', 'AF_OFF_DATE', 'ENGINE_BUILD_DATE'],
                             dtype={'WAR_ORIG_DISTR_CDE': 'category', 'WAR_RESP_DISTR_CDE': 'category'})

        claims['ACTUAL_CLAIM_LEVEL_TOTAL_CHG_AMT_USD'] = np.where(claims['ROW_NUM'] == 1,
                                                                  claims['ACTUAL_CLAIM_LEVEL_TOTAL_CHG_AMT_USD'], 0)
        claims['FLAT_RATE_HRS_QTY'] = np.where(claims['ROW_NUM'] == 1, claims['FLAT_RATE_HRS_QTY'], 0)
        claims['CALCULATED_PART_COST_USD'] = np.where(claims['ROW_NUM'] == 1, claims['CALCULATED_PART_COST_USD'], 0)
        claims['CALCULATED_FLAT_RATE_LABOR_COST_USD'] = np.where(claims['ROW_NUM'] == 1,
                                                                 claims['CALCULATED_FLAT_RATE_LABOR_COST_USD'], 0)
        claims['CALCULATED_DIAGNOSTIC_LABOR_COST_USD'] = np.where(claims['ROW_NUM'] == 1,
                                                                  claims['CALCULATED_DIAGNOSTIC_LABOR_COST_USD'], 0)
        claims['CALCULATED_HDLG_CHG_AMT_USD'] = np.where(claims['ROW_NUM'] == 1,
                                                         claims['CALCULATED_HDLG_CHG_AMT_USD'], 0)
        claims['CALCULATED_TOTAL_LABOR_COST_USD'] = np.where(claims['ROW_NUM'] == 1, 
                                                             claims['CALCULATED_TOTAL_LABOR_COST_USD'], 0)
        claims['CALCULATED_TOTAL_COST_USD'] = np.where(claims['ROW_NUM'] == 1, 
                                                       claims['CALCULATED_TOTAL_COST_USD'], 0)
        claims['DIAGNOSTIC_LABOR_HRS_QTY'] = np.where(claims['ROW_NUM'] == 1, claims['DIAGNOSTIC_LABOR_HRS_QTY'], 0)
        claims['FRGT_SUBL_TAX_AMT_USD'] = np.where(claims['ROW_NUM'] == 1, claims['FRGT_SUBL_TAX_AMT_USD'], 0)
        claims['MassProCost_USD'] = np.where(claims['ROW_NUM'] == 1, claims['MassProCost_USD'], 0)
        claims['MassProCostX205_USD'] = np.where(claims['ROW_NUM'] == 1, claims['MassProCostX205_USD'], 0)

        with self.output().open('w') as outfile:
                claims.to_csv(outfile, index=False)


class AddTotalCostsTimesPercentage(luigi.Task):
    """Task to add actual claim level total cost and calculated total cost columns multiplied by the fixed percentage"""

    def requires(self):
        return ZeroedOutClaimCosts()

    def output(self):
        return luigi.LocalTarget(MyGlobals().data_folder + 'ZF_CLA_Claims_After_Perc.csv')

    def run(self):
        claims = pd.read_csv(self.input().open('r'),
                             parse_dates=['REPAIR_ORDER_DATE', 'AF_OFF_DATE', 'ENGINE_BUILD_DATE'],
                             dtype={'WAR_ORIG_DISTR_CDE': 'category', 'WAR_RESP_DISTR_CDE': 'category'})

        claims = claims.assign(ACTUAL_CLAIM_LEVEL_TOTAL_CHG_AMT_USD_AFTER_PERC=claims['ACTUAL_CLAIM_LEVEL_TOTAL_CHG_AMT_USD'] *
                               claims['SUPP_FIXED_PERC'])
        claims = claims.assign(CALCULATED_TOTAL_COST_USD_AFTER_PERC = claims['CALCULATED_TOTAL_COST_USD'] * 
                               claims['SUPP_FIXED_PERC'])

        with self.output().open('w') as outfile:
                claims.to_csv(outfile, index=False)


class AddInitialFinalWrpAmount(luigi.Task):
    """Task to create initial and final WRP amount in USD: min(actual total$, calculated$, MassProx2.05)"""

    def requires(self):
        return AddTotalCostsTimesPercentage()

    def output(self):
        return luigi.LocalTarget(MyGlobals().data_folder + 'ZF_CLA_Claims_Initial_Final_WRP_Amount.csv')

    def run(self):
        claims = pd.read_csv(self.input().open('r'),
                             parse_dates=['REPAIR_ORDER_DATE', 'AF_OFF_DATE', 'ENGINE_BUILD_DATE'],
                             dtype={'WAR_ORIG_DISTR_CDE': 'category', 'WAR_RESP_DISTR_CDE': 'category'})

        claims = claims.assign(WRP_VOUCHER_AMT_USD_INITIAL=claims[['ACTUAL_CLAIM_LEVEL_TOTAL_CHG_AMT_USD_AFTER_PERC',
                               'CALCULATED_TOTAL_COST_USD_AFTER_PERC', 'MassProCostX205_USD']].min(axis='columns'))
        claims = claims.assign(WRP_VOUCHER_AMT_USD_FINAL = claims['WRP_VOUCHER_AMT_USD_INITIAL'])

        with self.output().open('w') as outfile:
                claims.to_csv(outfile, index=False)


class CreateVoucherFixed(luigi.Task):
    """Task to create fixed voucher based on criteria:
            (claims without TPLs
               or claims with TPLs with blank conclusion ("limbo TPLs")
            )
            and must be normal warranty claims (campaign code=N)
            and must have fixed percentage
            and actual claim level total cost > 0.1
            and vehicle miles <= 70000
            and TransDTF <= 1460 (4 years)
            and WAR_CLAIM_DATE >= voucher start date
            and WAR_CLAIM_DATE <= voucher end date"""

    def requires(self):
        return AddInitialFinalWrpAmount()

    def output(self):
        return luigi.LocalTarget(MyGlobals().data_folder + 'ZF_CLA_Claims_Fixed_Voucher.csv')

    def run(self):
        claims = pd.read_csv(self.input().open('r'),
                             parse_dates=['REPAIR_ORDER_DATE', 'AF_OFF_DATE', 'ENGINE_BUILD_DATE'],
                             dtype={'WAR_ORIG_DISTR_CDE': 'category', 'WAR_RESP_DISTR_CDE': 'category'})

        # Claims without TPLs
        criteria1 = (claims['TRANSFER_PART_LIST_ITEM_DETAIL_SK'].isnull())
        # Claims with TPLs but blank conclusion text (these are your "limbo TPLs")
        criteria2 = (claims['CONCLUSION_DESC_TXT'].isnull()) & claims['TRANSFER_PART_LIST_ITEM_DETAIL_SK'] > 0
        # 'Normal' warranty claims ONLY
        criteria3 = claims['CAMPAIGN_CODE'] == 'N'
        # Claims with applicable fixed percentages
        criteria4 = claims['_merge'] == 'both'
        # Claims with actual charge amounts
        criteria5 = claims['ACTUAL_CLAIM_LEVEL_TOTAL_CHG_AMT_USD'] > 0.1
        # Claims meeting warranty limits
        criteria6 = claims['VEH_MILEAGE'] <= 70000
        criteria7 = claims['TransDTF'] <= 1460
        # Limit to voucher period
        criteria8 = claims['WAR_CLAIM_DATE'] >= int(MyGlobals().start_voucher_date[:4] +
                                                    MyGlobals().start_voucher_date[5:7])
        criteria9 = claims['WAR_CLAIM_DATE'] <= int(MyGlobals().end_voucher_date[:4] +
                                                    MyGlobals().end_voucher_date[5:7])

        voucher_fixed = claims[(criteria1 | criteria2)  # claims without TPLs or claims with TPLs with blank conclusion
                                & criteria3  # Normal warranty claims
                                & criteria4  # Have fixed percentages
                                & criteria5  # Have actual claim level total charge amout > 0.10
                                & criteria6  # Vehicle miles <= 70000
                                & criteria7  # TransDTF <= 1460
                                & criteria8  # WAR_CLAIM_DATE >= voucher start date
                                & criteria9]  # WAR_CLAIM_DATE <= voucher end date

        # Create FIXED_YES_NO column
        voucher_fixed = voucher_fixed.assign(_merge='YES')
        voucher_fixed.rename({'_merge': 'FIXED_YES_NO'}, axis='columns', inplace=True)

        with self.output().open('w') as outfile:
                voucher_fixed.to_csv(outfile, index=False)


class AddAlreadyPaid(luigi.Task):
    """Task to add column that aids in identifying claims that were already paid."""

    def requires(self):
        return CreateVoucherFixed()
    
    def output(self):
        return luigi.LocalTarget(MyGlobals().data_folder + 'ZF_CLA_Claims_Fixed_Voucher_Already_Paid.csv')

    def run(self):
        claims = pd.read_csv(self.input().open('r'),
                             parse_dates=['REPAIR_ORDER_DATE', 'AF_OFF_DATE', 'ENGINE_BUILD_DATE'],
                             dtype={'WAR_ORIG_DISTR_CDE': 'category', 'WAR_RESP_DISTR_CDE': 'category'})

        conn_str = (
            r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'
            # r'DBQ=\\mmpapp02\mq_db\wrp\ZF_ATM_WRP_Project\DAT\WRP_DAT_ZF.accdb;'
            r'DBQ=\\mmpapp02\mq_db\wrp\ZF_ATM_WRP_Project\version4\databases\WRP_DAT_ZF.accdb;'
        )
        cnxn = pyodbc.connect(conn_str)
        cursor = cnxn.cursor()

        sql = """
        SELECT
            *

        FROM
            tbl_Already_Paid_Claims
        """

        try:
            already_paid_claims = pd.read_sql(sql, cnxn)

            # Close connections
            cursor.close()
            cnxn.close()
            print(sql)
        except:
            print("Error connecting to database")
            cursor.close()
            cnxn.close()

        voucher_fixed = pd.merge(claims, already_paid_claims, how='left', left_on='VIN_DLR_CLM_SK',
                                 right_on='VIN_DLR_CLM_SK', indicator=True)

        with self.output().open('w') as outfile:
            voucher_fixed.to_csv(outfile, index=False)


class CreateVoucherFixedFinal(luigi.Task):
    """Task to create 'FINAL' voucher which now excludes claims that were already paid by the supplier"""

    def requires(self):
        return AddAlreadyPaid()

    def output(self):
        return luigi.LocalTarget(MyGlobals().data_folder + 'ZF_CLA_Claims_Fixed_Voucher_FINAL.csv')

    def run(self):
        voucher_fixed = pd.read_csv(self.input().open('r'),
                                    parse_dates=['REPAIR_ORDER_DATE', 'AF_OFF_DATE', 'ENGINE_BUILD_DATE'],
                                    dtype={'WAR_ORIG_DISTR_CDE': 'category', 'WAR_RESP_DISTR_CDE': 'category'})

        # Limit to voucher records that were NOT already paid
        criteria = voucher_fixed['_merge'] == 'left_only'
        voucher_fixed = voucher_fixed[criteria]

        # Delete redundant or unnecessary columns
        del voucher_fixed['WRP_ID']
        del voucher_fixed['WRP_RECOVERY_COST_AFTER_PERC_USD_FINAL']
        del voucher_fixed['_merge']

        # Rename WRPID_x to WRPID
        voucher_fixed.rename({'WRPID_x': 'WRPID'}, axis='columns', inplace=True)

        with self.output().open('w') as outfile:
                voucher_fixed.to_csv(outfile, index=False)


if __name__ == '__main__':
    luigi.build([CreateVoucherFixedFinal()], local_scheduler=True)
