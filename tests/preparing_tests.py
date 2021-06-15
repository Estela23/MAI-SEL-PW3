import random
from cbr import CBR
import os
import json

DATA_PATH = '../Data'

# Create cocktails CBR
cocktails_cbr = CBR(os.path.join(DATA_PATH, 'case_library.xml'), verbose=True)

n_tests = 10

names = [f"cocktail_{i}" for i in range(n_tests)]

n_constraints = 8

all_tests = {}

for i in range(n_tests):

    my_dict = {"name": names[i]}

    n_categories, n_glasses, n_alc_types, n_basic_tastes, n_ingredients, n_exc_ingredients, n_exc_alc_types, \
        n_exc_basic_tastes = [random.randint(0, 3) for i in range(n_constraints)]

    my_dict["category"] = random.sample(cocktails_cbr.categories, n_categories)
    my_dict["glass_type"] = random.sample(cocktails_cbr.glass_types, n_glasses)
    my_dict["alc_type"] = random.sample(cocktails_cbr.alcohol_types, n_alc_types)
    my_dict["basic_taste"] = random.sample(cocktails_cbr.basic_tastes, n_basic_tastes)

    ingredients = random.sample([ingr for ingr in cocktails_cbr.ingredients_list], n_ingredients)
    if ingredients:
        my_dict["ingredients"] = [ingr.name for ingr in ingredients]
    else:
        my_dict["ingredients"] = []

    exc_ingredients = random.sample([ingr for ingr in cocktails_cbr.ingredients_list], n_exc_ingredients)
    if exc_ingredients:
        my_dict["exc_ingredients"] = [ingr.name for ingr in exc_ingredients]
    else:
        my_dict["exc_ingredients"] = []

    my_dict["exc_alc_type"] = random.sample(cocktails_cbr.alcohol_types, n_exc_alc_types)
    my_dict["exc_basic_taste"] = random.sample(cocktails_cbr.basic_tastes, n_exc_basic_tastes)

    # Check contradictions between positive and negative constraints
    # For each excluded ingredient
    for ingr in exc_ingredients:
        # Direct contradiction with the requested ingredients
        if ingr.name in my_dict["ingredients"]:
            my_dict["exc_ingredients"].remove(ingr.name)

    # For each excluded alcohol type
    for a_type in my_dict["exc_alc_type"]:
        # Direct contradiction with the requested alcohol types
        if a_type in my_dict["alc_type"]:
            my_dict["exc_alc_type"].remove(a_type)
        # Indirect contradiction when some of the requested ingredients has this alcohol type
        elif a_type in [ingr.alc_type for ingr in exc_ingredients]:
            my_dict["exc_alc_type"].remove(a_type)

    # For each excluded basic taste
    for b_taste in my_dict["exc_basic_taste"]:
        # Direct contradiction with the requested basic tastes
        if b_taste in my_dict["basic_taste"]:
            my_dict["exc_basic_taste"].remove(b_taste)
        # Indirect contradiction when some of the requested ingredients has this basic taste
        elif b_taste in [ingr.basic_taste for ingr in exc_ingredients]:
            my_dict["exc_basic_taste"].remove(b_taste)

    # Save this set of constraints to the whole dict
    all_tests[f"constraints_{i}"] = my_dict

# Save all the tests' constraints to a json file
with open('tests_constraints.json', 'w') as tests_file:
    json.dump(all_tests, tests_file)