# Select only the rows where the number of visits is greater than or equal to 3
ex3df[ex3df.visits>=3]

# Select the rows where the age is missing, i.e. is NaN
ex3df[ex3df.age.isnull()]

# Select the rows where the animal is a cat and the age is less than 3.
ex3df[(ex3df.age < 3) & (ex3df.animal == 'cat')]

# Select the rows the age is between 2 and 4 (inclusive).
ex3df[(ex3df.age >= 2) & (ex3df.age <= 4)]

# Change the index to use this list:
idx = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j']
ex3df.index = idx

# Change the age in row 'f' to 1.5.
#ex3df['age']['f'] = 1.5  # This will generate a warning; see http://pandas.pydata.org/pandas-docs/stable/indexing.html#indexing-view-versus-copy
ex3df.loc['f', 'age'] = 1.5

# Append a new row 'k' to df with your choice of values for each column. 
ex3df.loc['k'] = (10, 'hippo', 0, 1)

# Then delete that row to return the original DataFrame.
ex3df.drop(['k'], inplace=True)



