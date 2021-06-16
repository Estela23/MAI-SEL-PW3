import pandas as pd
import os
from matplotlib import pyplot as plt
import numpy as np
import json

def load_constraints(filename):
    """ Parse JSON with constraints

    Args:
        filename (str): filename of the json

    Returns:
        dict: containing the set of constraints
    """
    with open(filename) as json_file:
        data = json.load(json_file)
        
    if len(data.keys()) == 0:
        print("Empty JSON, please add some constraint")
        exit(1)
     
    elif 'constraints' in data:
        if len(data['constraints'].keys()) == 0:
            print("No constraints specified, please specify some.")
            return None
        else:
            return(data['constraints'])
        
def interactive_menu(cbr):
    """ Interactive CLI menu to get constraints.

    Args:
        cbr (CBR): used to check validity of inputs

    Returns:
         dict: containing the set of constraints
    """
    constraints = {'category': [], 'glass_type': [], 'alc_type': [], 'exc_alc_type': [],
                   'basic_taste': [], 'exc_basic_taste': [], 'ingredients': [], 'exc_ingredients': []}

    # Categories
    print("\nWhat kinds of drink do you wish? (Introduce number of category)")
    print("Introduce End to finish category selection.")
    for idx, cat in enumerate(cbr.categories):
        print(str(idx)+". "+cat)
    while True:
        type_drink = input().lower()
        if type_drink == "end" or type_drink=='':
            break
        elif not type_drink.isdigit():
            print("Not a number, repeat selection.")
        elif int(type_drink) < 0 or int(type_drink) >= len(cbr.categories):
            print("Not valid type of drink, repeat selection.")
        else:
            constraints['category'].append(list(cbr.categories)[int(type_drink)])
    
    # Glasses    
    print("\nIntroduce which glasses do you wish: (Introduce name of the glass)")
    print("Introduce End to finish glass selection.")
    for idx, cat in enumerate(cbr.glass_types):
        print(str(idx)+". "+cat)
    while True:
        type_glass = input().lower()
        if type_glass == "end":
            break
        elif int(type_glass) < 0 or int(type_glass) >= len(cbr.glass_types):
            print("Not valid type of glass, repeat selection.")
        else:
            constraints['glass_type'].append(list(cbr.glass_types)[int(type_glass)])
    
    # Alcohol types to use
    print("\nIntroduce types of alcohol you wish to use: (Introduce the number of the alcohol type)")
    print("Introduce End to finish alcohol selection.")
    for idx, cat in enumerate(cbr.alcohol_types):
        print(str(idx)+". "+cat)
    while True:
        type_alcohol = input().lower()
        if type_alcohol == "end":
            break
        elif int(type_alcohol) < 0 or int(type_alcohol) >= len(cbr.alcohol_types):
            print("Not valid alcohol type.")
        else:
            constraints['alc_type'].append(list(cbr.alcohol_types)[int(type_alcohol)])
    
    # Alcohol types to avoid
    print("\nIntroduce types of alcohol you wish to avoid: (Introduce the number of the alcohol type)")
    print("Introduce End to finish alcohol selection.")
    for idx, cat in enumerate(cbr.alcohol_types):
        print(str(idx)+". "+cat)
    while True:
        type_alcohol = input().lower()
        if type_alcohol == "end":
            break
        elif int(type_alcohol) < 0 or int(type_alcohol) >= len(cbr.alcohol_types):
            print("Not valid alcohol type.")
        else:
            constraints['exc_alc_type'].append(list(cbr.alcohol_types)[int(type_alcohol)]) 
            
    # Basic tastes to use        
    print("\nIntroduce tastes you wish to use: (Introduce the number of the basic taste)")
    print("Introduce End to finish taste selection.")
    for idx, cat in enumerate(cbr.basic_tastes):
        print(str(idx)+". "+cat)
    while True:
        basic_taste = input().lower()
        if basic_taste == "end":
            break
        elif int(basic_taste) < 0 or int(basic_taste) >= len(cbr.basic_tastes):
            print("Not valid basic taste.")
        else:
            constraints['basic_taste'].append(list(cbr.basic_tastes)[int(basic_taste)])
    
    # Basic tastes to avoid
    print("\nIntroduce tastes you wish to avoid: (Introduce the number of the basic taste)")
    print("Introduce End to finish taste selection.")
    for idx, cat in enumerate(cbr.basic_tastes):
        print(str(idx)+". "+cat)
    while True:
        basic_taste = input().lower()
        if basic_taste == "end":
            break
        elif int(basic_taste) < 0 or int(basic_taste) >= len(cbr.basic_tastes):
            print("Not valid basic taste.")
        else:
            constraints['exc_basic_taste'].append(list(cbr.basic_tastes)[int(basic_taste)])
                     
    # Ingredients to use
    print("\nIntroduce ingredients to the drink:")
    print("Introduce End to finish ingredients selection.")
    while True:
        ingredients_inp = input().lower()
        if ingredients_inp == "end":
            break
        elif ingredients_inp in cbr.ingredient_names:
            constraints['exc_ingredients'].append(ingredients_inp)
        else:
            print("Error, we do not have this ingredient.")
            
   # Ingredients to avoid
    print("\nIntroduce which ingredients you do not wish on your drink:")
    print("Introduce End to finish the exclusion of ingredients.")
    while True:
        excluded_ingredients = input().lower()
        if excluded_ingredients == "end":
            break
        elif excluded_ingredients in cbr.ingredient_names:
            if excluded_ingredients in constraints['ingredients']:
                print("Error, this ingredient is set as a constraint.")
            else:
                constraints['exc_ingredients'].append(excluded_ingredients)
        else:
            print("Error, we do not have this ingredient.")
            
    return constraints

def evaluation_menu(cbr, adapted_cocktail):
    """ Print ingredients and preparation of adapted cocktail
    and ask suer to rate it with a given score between 0 and 10.

    Args:
        cbr (CBR): initialized CBR
        adapted_cocktail (Element): cocktail Element adapted from user constraints.

    Returns:
        float: score
    """
    # Print adapted case
    print('\n=====================================================================')
    print(f'Adapted cocktail: {adapted_cocktail.find("name").text}')
    print('\nIngredients:')
    cbr.print_ingredients(adapted_cocktail)
    print('\nPreparation:')
    cbr.print_preparation(adapted_cocktail) 

    # Ask user for evaluation
    print("\nHow good was the cocktail?")
    print("Please, introduce a score between 0 and 10 (You can use decimals)")
    score = float(input())
    
    return score
    
def dataset_analysis():
    """ Perform an exploratory data analysis to extract information
    about the dataset and to save different histograms.
    """
    DATA_PATH = 'Data'

    csv_file = os.path.join(DATA_PATH, 'data_cocktails.csv')
    dataset = pd.read_csv(csv_file, encoding='utf_8')
    dataset = dataset.drop(dataset.columns[0], axis=1)
    dataset = dataset.drop(dataset.columns[-2:], axis=1)
    dataset.fillna('', inplace=True)

    #################################################################
    ###########        Print information about dataset       ########
    #################################################################

    print('Dataset unique values')
    print(dataset.nunique())

    categories = dataset['strCategory'].unique()
    print(f'\nCategories ({len(categories)}):')
    print(', '.join(categories).replace(' / ', '/'))

    alc_type = dataset['Alc_type'].unique()
    alc_type = alc_type[alc_type != '']
    print(f'\nAlcohol Type ({len(alc_type)}):')
    print(', '.join(alc_type).replace(' / ', '/'))

    basic_taste = dataset['Basic_taste'].unique()
    basic_taste = basic_taste[basic_taste != '']
    print(f'\nBasic Taste ({len(basic_taste)}):')
    print(', '.join(basic_taste).replace(' / ', '/'))

    ingredients = dataset['strIngredients'].unique()
    ingredients = ingredients[ingredients != '']
    print(f'\nIngredients ({len(ingredients)}):')
    print(', '.join(ingredients).replace(' / ', '/'))

    glass = dataset['strGlass'].unique()
    glass = glass[glass != '']
    print(f'\nGlass ({len(glass)}):')
    print(', '.join(glass).replace(' / ', '/'))


    #################################################################
    ###########              Plot histograms                 ########
    #################################################################

    # Set general font size
    # plt.rcParams['font.size'] = '16'

    alc_ingr = dataset[dataset['Alc_type'] != ''][['Alc_type', 'strIngredients']]
    non_alc_ingr = dataset[dataset['Alc_type'] == ''][['Basic_taste', 'strIngredients']]

    # Popular Alcohol type
    counts_type_alc = alc_ingr['Alc_type'].value_counts()
    # sorted_counts_type_alc = [counts_type_alc[type] for type in alc_type]

    plt.bar([i for i in range(len(alc_type))], counts_type_alc, color="tab:green")
    plt.xticks(range(len(alc_type)), counts_type_alc.axes[0].values, rotation=45, horizontalalignment='right', fontsize=10)
    plt.title("Number of times an alcohol appears in a recipe")
    plt.tight_layout()
    plt.savefig(os.path.join(DATA_PATH, 'Representations/popular_alcohol_types'))
    plt.clf()

    # Popular basic taste
    counts_type_basic = non_alc_ingr['Basic_taste'].value_counts()

    plt.bar([i for i in range(len(basic_taste))], counts_type_basic, color="tab:green")
    plt.xticks(range(len(basic_taste)), counts_type_basic.axes[0].values, rotation=45, horizontalalignment='right', fontsize=10)
    plt.title("Number of times a basic taste appears in a recipe")
    plt.tight_layout()
    plt.savefig(os.path.join(DATA_PATH, 'Representations/popular_basic_tastes'))
    plt.clf()

    # Number of unique ingredients type for each Alcohol type
    different_type_alc = [alc_ingr[alc_ingr['Alc_type'] == this_type]['strIngredients'].nunique() for this_type in alc_type]
    info_unique_alc_types = [t for t in zip(*sorted(zip(different_type_alc, alc_type), reverse=True))]

    plt.bar([i for i in range(len(alc_type))], info_unique_alc_types[0], color="tab:green")
    plt.xticks(range(len(alc_type)), info_unique_alc_types[1], rotation=45, horizontalalignment='right', fontsize=10)
    plt.title("Number of unique ingredients for each type of alcohol")
    plt.tight_layout()
    plt.savefig(os.path.join(DATA_PATH, 'Representations/unique_alcohols_by_type'))
    plt.clf()

    # Number of unique ingredients type for each Basic taste type
    different_type_non_alc = [non_alc_ingr[non_alc_ingr['Basic_taste'] == this_type]['strIngredients'].nunique() for this_type in basic_taste]
    info_unique_non_alc_types = [t for t in zip(*sorted(zip(different_type_non_alc, basic_taste), reverse=True))]

    plt.bar([i for i in range(len(basic_taste))], info_unique_non_alc_types[0], color="tab:green")
    plt.xticks(range(len(basic_taste)), info_unique_non_alc_types[1], rotation=45, horizontalalignment='right', fontsize=10)
    plt.title("Number of unique ingredients for each type of non alcoholic beverage")
    plt.tight_layout()
    plt.savefig(os.path.join(DATA_PATH, 'Representations/unique_beverages_by_type'))
    plt.clf()

    # Number of cocktails by category
    category_drinks = [dataset[dataset['strCategory'] == category]['strIngredients'].nunique() for category in categories]
    info_unique_categories = [t for t in zip(*sorted(zip(category_drinks, categories), reverse=True))]

    plt.bar([i for i in range(len(categories))], info_unique_categories[0], color="tab:green")
    plt.xticks(range(len(categories)), info_unique_categories[1], rotation=45, horizontalalignment='right', fontsize=10)
    plt.title("Number of unique cocktails for each category")
    plt.tight_layout()
    plt.savefig(os.path.join(DATA_PATH, 'Representations/unique_cocktails_by_category'))
    plt.clf()