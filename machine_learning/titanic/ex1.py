import warnings
from speedml import Speedml
import matplotlib.pyplot as plt
warnings.simplefilter("ignore", category=DeprecationWarning)
#warnings.warn("deprecated", DeprecationWarning)

sml = Speedml('train.csv', 
              'test.csv', 
              target = 'Survived',
              uid = 'PassengerId')



sml.plot.continuous('Age')
plt.show()