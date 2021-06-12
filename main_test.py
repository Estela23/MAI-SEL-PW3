from cbr import CBR
import os

DATA_PATH = 'Data'

constraints = {'category': 'Cocktail', 'glass_type': 'Beer glass', 'ingredients': ['Vodka', 'Orange Juice'],
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

#ingredient = 'Yellow Chartreuse'
#ingredient_alc_type = [k for k in cocktails_cbr.alcohol_dict if ingredient in cocktails_cbr.alcohol_dict[k]][0]

# 155 Belmont	
# Vodka and Orange Juice

# 50/50
# Vanilla vodka and Orange Juice