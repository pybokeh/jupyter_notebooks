import warnings
from speedml import Speedml
import pandas as pd

sml = Speedml('train.csv', 
              'test.csv', 
              target = 'Survived',
              uid = 'PassengerId')



sml.plot.continuous('Age')
plt.show()