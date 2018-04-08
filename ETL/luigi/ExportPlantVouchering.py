from datetime import datetime
import luigi
import pandas as pd


class MyGlobals(luigi.Config):
    """Define 'global' parameter values here"""

    mydate = datetime.today()
    data_folder = 'outputs/text_files/'

    #labor_rate = input("Enter labor rate in GBP: ")
    #part_factor = input("Enter part cost factor (0.#): ")
    #handling_factor = input("Enter handling cost factor (0.#): ")
    start_voucher_date = input("Enter start voucher date (YYYY-MM-DD): ")
    end_voucher_date = input("Enter end voucher date (YYYY-MM-DD): ")


class GetFqsExcel(luigi.Task):
    """Task that reads a local Excel file containing FQS-3 sourced warranty claims"""

    def output(self):
        return luigi.LocalTarget(MyGlobals().data_folder + 'claims_fqs.csv')


    def run(self):
        claims_fqs = pd.read_csv('/home/pybokeh/temp/REQUEST_RESULT.xls', encoding='utf-8', skiprows=99, sep='\t',
                    converters={'HM Claim Recognition Date (yyyy/mm/dd)': lambda x: datetime.strptime(x, "%Y%m%d"),
                                'Repair Order Date (yyyy/mm/dd)': lambda x: datetime.strptime(x, "%Y%m%d"),
                                'Production Date (yyyy/mm/dd)': lambda x: datetime.strptime(x, "%Y%m%d")},
                    dtype={'Failed Part No. (1-5)': str, 'Transmission Serial No.': str, 'Local Claim No.': str,
                           'HM Claim No.': str, 'Repair Dealer No.': str})

        with self.output().open('w') as outfile:
            claims_fqs.to_csv(outfile, index=False, encoding='utf-8')


class FilterClaims(luigi.Task):
    """Tasks that filters the initial FQS-3 claims down to:
       - ZF models
       - replaced part Qty > 0
       - within start and end voucher dates"""

    def requires(self):
        return GetFqsExcel()


    def output(self):
        return luigi.LocalTarget(MyGlobals.data_folder + 'HUM_ZF.csv')


    def run(self):
        claims_fqs = pd.read_csv(self.input().open('r'))

        criteria = (claims_fqs['HM Claim Recognition Date (yyyy/mm/dd)'] >= MyGlobals().start_voucher_date) \
            & (claims_fqs['HM Claim Recognition Date (yyyy/mm/dd)'] <= MyGlobals().end_voucher_date) \
            & (claims_fqs['Transmission Type Code'].str.startswith('Q')) \
            & (claims_fqs['Quantity of Replaced Parts'] > 0)
        
        HUM_ZF = claims_fqs[criteria]

        with self.output().open('w') as outfile:
            HUM_ZF.to_csv(outfile, index=False)


if __name__ == '__main__':
    luigi.build([FilterClaims()], local_scheduler=True)
