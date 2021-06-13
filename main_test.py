from cbr import CBR
import os

DATA_PATH = 'Data'


constraints = {'name': 'SEL-cocktail', 'category': ['shot'], 'glass_type': ['old-fashioned glass'], 'ingredients': ['cranberry juice', 'malibu rum'],
               'alc_type': ['sweet liqueur', 'vodka'], 'basic_taste': [], 'exc_ingredients': ['pineapple juice']}


# Create cocktails CBR
cocktails_cbr = CBR(os.path.join(DATA_PATH, 'case_library.xml'), verbose=True)
print('Cocktails CBR initialized')

print('\nConstraints:')
print(constraints)

# Retrive cocktail wight given constraints
c = cocktails_cbr._retrieval(constraints)
print(f'\n{c.find("name").text} cocktail retrieved')

print('\nOriginal Ingredients:')
cocktails_cbr._print_ingredients(c)
print('\nOriginal Preparation:')
cocktails_cbr._print_preparation(c)

adapted_cocktail = cocktails_cbr._adaptation(constraints, c)
print(f'\n{adapted_cocktail.find("name").text} cocktail adapted')

print('\nAdapted Ingredients:')
cocktails_cbr._print_ingredients(adapted_cocktail)
print('\nAdapted Preparation:')
cocktails_cbr._print_preparation(adapted_cocktail)

# Evaluate constraints
evaluation, eval_results = cocktails_cbr._evaluate_constraints_fullfillment(constraints, adapted_cocktail)

if evaluation:
    print('\nAll contstraints fullfilled!')
else:
    print('\nConstraints error:')
    print('\n'.join(eval_results))

    assert(evaluation)


# Evalutation

# Learning
cocktails_cbr._learning(c, adapted_cocktail)
