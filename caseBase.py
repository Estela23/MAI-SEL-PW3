from lxml import etree
from collections import namedtuple
import os

DATA_PATH = 'Data'

# Declaring namedtuple() 
Ingredient = namedtuple('Ingredient', ['name', 'identifier', 'alc_type', 'basic_taste', 'measure', 'quantity', 'unit']) 

class Cocktail:
    def __init__(self, name, category, glass_type, ingredients, preparation):
        self.name = name
        self.category = category
        self.glass_type = glass_type
        self.ingredients = ingredients
        self.preparation = preparation
        
    def print_preparation(self):
        for s in self.preparation:
            for i in self.ingredients:
                s = s.replace(i.identifier, i.name)
            print(s)
            
def load_library(file):
    tree = etree.parse(file)
    cocktails = tree.getroot()
    cocktails_list = []

    for c in cocktails:
        # Get cocktail information
        name = c.find('name').text
        category = c.find('category').text
        glass_type = c.find('glasstype').text
        ingredients = c.find('ingredients')
        preparation = c.find('preparation')
        preparation_steps = [s.text for s in preparation]

        # Get information about each ingredient
        ingredients_list = []
        for i in ingredients:
            ing = Ingredient(i.text, i.get('id'), i.get('alc_type'), i.get('basic_taste'), i.get('measure'), 
                            i.get('quantity'), i.get('unit'))
            
            ingredients_list.append(ing)
        
        # Create and append cocktail object
        cocktails_list.append(Cocktail(name, category, glass_type, ingredients_list, preparation_steps))

    return cocktails_list    

# def export_library():
# TODO

if __name__ == "__main__":
    xml_file = os.path.join(DATA_PATH, 'case_library.xml')
    cbl = load_library(xml_file)