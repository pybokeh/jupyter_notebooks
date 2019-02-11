# Calculate the mean age for each different type of animal.
print(ex3df.groupby('animal').age.mean())

# Count the number of each type of animal.
print(ex3df.animal.value_counts())

# Sort the data first by the values in the 'age' column in decending order,
# then by the value in the 'visits' column in ascending order.
ex3df.sort_values(by=['age', 'visits'], ascending=[False, True])

# In the 'animal' column, change the 'snake' entries to 'python'.
ex3df.loc[ex3df.animal == 'snake', 'animal'] = 'python'

# The 'priority' column contains the values 'yes' and 'no'. Replace this column with a column of boolean values: 
#'yes' should be True and 'no' should be False.
ex3df['priority'] = ex3df.apply(lambda row: True if row.priority == 'yes' else False, axis=1)



