import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from cbr import CBR
import utils

DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'Data')


# constraints = {'name': 'SEL-cocktail', 'category': ['shot'], 'glass_type': ['old-fashioned glass'],
#                'ingredients': ['cranberry juice', 'malibu rum'], 'alc_type': ['sweet liqueur', 'vodka'],
#                'basic_taste': [], 'exc_ingredients': ['amaretto', 'pineapple juice'], 'exc_alc_type': ['cachaca'],
#                'exc_basic_taste': ['spicy']}

# Load constraints from JSON
constraints = utils.load_constraints(os.path.join(DATA_PATH, 'my_constraints.json'))

# Create cocktails CBR
cocktails_cbr = CBR(os.path.join(DATA_PATH, 'case_library.xml'), verbose=True)
print('Cocktails CBR initialized')

print('\nConstraints:')
print(constraints)

# Retrive cocktail wight given constraints
c = cocktails_cbr._retrieval(constraints)
print(f'\n{c.find("name").text} cocktail retrieved')
print('\nOriginal Ingredients:')
cocktails_cbr.print_ingredients(c)
print('\nOriginal Preparation:')
cocktails_cbr.print_preparation(c)

adapted_cocktail, n_changes = cocktails_cbr._adaptation(constraints, c)
print(f'\n{adapted_cocktail.find("name").text} cocktail adapted after {n_changes} changes')

# Check adapted failure
adapted_failure = cocktails_cbr._check_adapted_failure(adapted_cocktail)

print('\nAdapted Ingredients:')
cocktails_cbr.print_ingredients(adapted_cocktail)
print('\nAdapted Preparation:')
cocktails_cbr.print_preparation(adapted_cocktail)
print("\nAdapted_case category: " + adapted_cocktail.find("category").text)

# Evaluate constraints
evaluation, eval_results = cocktails_cbr._evaluate_constraints_fulfillment(constraints, adapted_cocktail)

if evaluation:
    print('\nAll contstraints fullfilled!')
else:
    print('\nConstraints error:')
    print('\n'.join(eval_results))

    assert evaluation

