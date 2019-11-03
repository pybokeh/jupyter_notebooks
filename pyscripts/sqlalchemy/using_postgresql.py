from sqlalchemy import create_engine
from sqlalchemy import Table, MetaData
from sqlalchemy.orm import sessionmaker
import pandas as pd

db_string = 'postgres+psycopg2://user:password@localhost:5432/my_database'

engine = create_engine(db_string)

Session = sessionmaker(bind=engine)

s = Session()

metadata = MetaData(engine)

# Map a Python variable to an existing 'teacher' table
teachers = Table('teachers', metadata, autoload=True)

# Perform an equivalnet SELECT * from tables
query = s.query(teachers)

# Output resultset as a pandas dataframe
df = pd.read_sql(query.statement, query.session.bind)
print(df.head())

# Close session
s.close()