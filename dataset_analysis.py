import pandas as pd
import os
from matplotlib import pyplot as plt
import numpy as np
import seaborn as sns

DATA_PATH = 'Data'

csv_file = os.path.join(DATA_PATH, 'data_cocktails.csv')
dataset = pd.read_csv(csv_file, encoding='utf_8')
dataset = dataset.drop(dataset.columns[0], axis=1)
dataset = dataset.drop(dataset.columns[-2:], axis=1)
dataset.fillna('',inplace=True)

print('Dataset unique values')
print(dataset.nunique())

categories = dataset['strCategory'].unique()
print(f'\nCategories ({len(categories)}):')
print(', '.join(categories).replace(' / ', '/'))

alc_type = dataset['Alc_type'].unique()
alc_type = alc_type[alc_type!='']
print(f'\nAlcohol Type ({len(alc_type)}):')
print(', '.join(alc_type).replace(' / ', '/'))

basic_taste = dataset['Basic_taste'].unique()
basic_taste = basic_taste[basic_taste!='']
print(f'\nBasic Taste ({len(basic_taste)}):')
print(', '.join(basic_taste).replace(' / ', '/'))

ingredients = dataset['strIngredients'].unique()
ingredients = ingredients[ingredients!='']
print(f'\nIngredients ({len(ingredients)}):')
print(', '.join(ingredients).replace(' / ', '/'))

glass = dataset['strGlass'].unique()
glass = glass[glass!='']
print(f'\nGlass ({len(glass)}):')
print(', '.join(glass).replace(' / ', '/'))


alc_ingr = dataset[dataset['Alc_type']!=''][['Alc_type', 'strIngredients']]
non_alc_ingr = dataset[dataset['Alc_type']==''][['Basic_taste', 'strIngredients']]


# Number of recipes by Alcohol type
alc_ingr['Alc_type'].value_counts()

# Number of unique ingredients type for each Alcohol type
