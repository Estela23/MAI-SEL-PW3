from cbr import CBR
import os

DATA_PATH = 'Data'

constraints = {'category': ['Cocktail'], 'glass_type': ['Beer glass'], 'ingredients': ['Vodka', 'Orange Juice'],
                'alc_type': ['Rum'], 'exc_ingredients': []}

# Create cocktails CBR
cocktails_cbr = CBR(os.path.join(DATA_PATH, 'case_library.xml'))
print('Cocktails CBR initialized')

print('\nConstraints:')
print(constraints)

# Retrive cocktail wight given constraints
c = cocktails_cbr.retrieval(constraints)
print(f'\n{c.find("name").text} cocktail retrieved')

print('\nOriginal Ingredients:')
cocktails_cbr._print_ingredients(c)
print('\nOriginal Preparation:')
cocktails_cbr._print_preparation(c)

adapted_cocktail = cocktails_cbr.adaptation_step(constraints, c)
print(f'\n{adapted_cocktail.find("name").text} cocktail adapted')

print('\nAdapted Ingredients:')
cocktails_cbr._print_ingredients(adapted_cocktail)
print('\nAdapted Preparation:')
cocktails_cbr._print_preparation(adapted_cocktail)

# Evaluate constraints
evaluation, eval_results = cocktails_cbr._evaluate_constraints_fullfillment(constraints, adapted_cocktail)

if evaluation:
    print('\nAll contstraints fullfilled!')
else:
    print('\nConstraints error:')
    print('\n'.join(eval_results))