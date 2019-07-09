from pathlib import Path
from tqdm import tqdm
import click
import dask.dataframe as dd
from dask.distributed import Client
import pandas as pd
import pandas_profiling

client = Client(processes=False)

@click.command()
@click.option('--ext', prompt='Enter file extension (csv, xlsx)', help='File extension you want to limit files with')
def profile_directory(ext):
    """ A function that profiles files with a specified file extension in the current folder that this .py file resides in.
    """

    # Create a list of files filtered down to a specific file extension that a user provided with the --ext flag or
    # at the prompt
    flist = sorted([p for p in Path('.').glob("*." + ext) if p.is_file()])

    # For each file for a given file extension, read it, then profile it, then output profile report
    for file in tqdm(flist):
        if ext == 'csv':
            ddf = dd.read_csv(file)
            df = ddf.compute()
            df.profile_report(title="Pandas Profiling Report - " + file.name, 
                correlations={'pearson': False, 'spearman': False, 'kendall': False, 'phi_k': False, 'recoded': False}).to_file(output_file=file.stem+".html")
        elif ext == 'xlsx':
            df = pd.read_excel(file)
            df.profile_report(title="Pandas Profiling Report - " + file.name,
                correlations={'pearson': False, 'spearman': False, 'kendall': False, 'phi_k': False, 'recoded': False}).to_file(output_file=file.stem+".html")

if __name__ == '__main__':
    profile_directory()