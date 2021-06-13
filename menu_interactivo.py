import xml.etree.ElementTree as ET


def interactive_menu():
    constraints = {'glass_type': [], 'alc_type': [], 'basic_taste': [], 'ingredients': [], 'exc_ingredients': []}
    tree = ET.parse('Data/case_library.xml')
    cocktails = tree.getroot()
    alc_type = set([child.attrib['alc_type'] for child in cocktails.findall('cocktail/ingredients/ingredient')])
    ingredients = set([child.text for child in cocktails.findall('cocktail/ingredients/ingredient')])
    categories = set([child.text for child in cocktails.findall('cocktail/category')])
    glasses = set([child.text for child in cocktails.findall('cocktail/glasstype')])
    basic_tastes = set([child.attrib['basic_taste'] for child in cocktails.findall('cocktail/ingredients/ingredient')])
    while True:
        print("What kind of drink do you wish? (Introduce number of category)")
        for idx, cat in enumerate(categories):
            print(str(idx)+". "+cat)
        type_drink = input()
        if int(type_drink) < 0 or int(type_drink) >= len(categories):
            print("Not valid type of drink, repeat selection.")
        else:
            constraints['category'] = list(categories)[int(type_drink)]
            break
    while True:
        print("Introduce which glasses do you wish: (Introduce name of the glass)")
        print("Introduce End to finish glass selection.")
        for idx, cat in enumerate(glasses):
            print(str(idx)+". "+cat)
        type_glass = input()
        if type_glass == "End":
            break
        elif type_glass not in glasses:
            print("Not valid type of glass, repeat selection.")
        else:
            constraints['glass_type'].append(type_glass)
    while True:
        print("Introduce types of alcohol you wish to use: (Introduce the name of the alcohol type)")
        print("Introduce End to finish alcohol selection.")
        for idx, cat in enumerate(alc_type):
            print(str(idx)+". "+cat)
        type_alcohol = input()
        if type_alcohol == "End":
            break
        elif type_alcohol in alc_type:
            constraints['alc_type'].append(type_alcohol)
        else:
            print("Not valid alcohol type.")
    while True:
        print("Introduce tastes you wish to use: (Introduce the name of the basic taste)")
        print("Introduce End to finish taste selection.")
        for idx, cat in enumerate(basic_tastes):
            print(str(idx)+". "+cat)
        basic_taste = input()
        if basic_taste == "End":
            break
        elif basic_taste in basic_tastes:
            constraints['basic_taste'].append(basic_taste)
        else:
            print("Not valid taste selection.")
    while True:
        print("Introduce ingredients to the drink:")
        print("Introduce End to finish ingredients selection.")
        ingredients_inp = input()
        if ingredients_inp == "End":
            break
        elif ingredients_inp in ingredients:
            constraints['exc_ingredients'].append(ingredients_inp)
        else:
            print("Error, we do not have this ingredient.")
    while True:
        print("Introduce which ingredients you do not wish on your drink:")
        print("Introduce End to finish the exclusion of ingredients.")
        excluded_ingredients = input()
        if excluded_ingredients == "End":
            break
        elif excluded_ingredients in ingredients:
            if excluded_ingredients in constraints['ingredients']:
                print("Error, this ingredient is set as a constraint.")
            else:
                constraints['exc_ingredients'].append(excluded_ingredients)
        else:
            print("Error, we do not have this ingredient.")

    return constraints