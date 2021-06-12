import xml.etree.ElementTree as ET


def menu_interactivo():
    constraints = {'alc_type': [], 'ingredients': [], 'exc_ingredients': []}
    tree = ET.parse('Data/case_library.xml')
    cocktails = tree.getroot()
    categories = set([child.find('category').text for child in cocktails])
    glasses = set([child.find('glasstype').text for child in cocktails])
    while True:
        print("What kind of drink do you wish?")
        type_drink = input()
        if type_drink not in categories:
            print("Not valid type of drink, repeat selection.")
        else:
            constraints['category'] = type_drink
            break
    while True:
        print("What kind of glass do you wish?")
        type_glass = input()
        if type_glass not in glasses:
            print("Not valid type of glass, repeat selection.")
        else:
            constraints['glass_type'] = type_glass
            break
    while True:
        print("Introduce types of alcohol you wish to use:")
        print("Introduce End to finish alcohol selection.")
        type_alcohol = input()
        if type_alcohol == "End":
            break
        else:
            constraints['alc_type'].append(type_alcohol)
    while True:
        print("Introduce ingredients to the drink:")
        print("Introduce End to finish ingredients selection.")
        ingredients = input()
        if ingredients == "End":
            break
        else:
            constraints['ingredients'].append(ingredients)
    while True:
        print("Introduce which ingredients you not wish on your drink:")
        print("Introduce End to finish the exclusion of ingredients.")
        excluded_ingredients = input()
        if excluded_ingredients == "End":
            break
        else:
            constraints['exc_ingredients'].append(excluded_ingredients)
    print(constraints)
    return constraints