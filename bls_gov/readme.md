# Bureau of Labor Statistics

#### To use the custom blsutils package found in the src direcctory:
Navigate to `src` directory then issue the following command:

`pip install -e .`

This package assumes that you've acquired the developer API key from `bls.gov` and that 
you have the bls series ID that you want to plot.

Example usage:
```python
from blsutils import plot_bls_series_id
from pathlib import Path
import configparser

config = configparser.ConfigParser()
config.read(Path.home() / '.config' / 'config.ini')
bls_key = config['bls']['secretkey']

plot_bls_series_id(
    series_id='CUSR0000SS47014',
    series_descr='Gasoline, unleaded regular in U.S. city average, all urban consumers, seasonally adjusted',
    bls_key=bls_key
)
```

If you want the actual, low-level Python code used to create the plots, look at the [BLS_API.ipynb](BLS_API.ipynb) 
notebook or the `blsutils` package found in the `src` directory.
