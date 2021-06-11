from lxml import etree
from collections import namedtuple
import os

DATA_PATH = 'Data'

# Declaring namedtuple() 
Ingredient = namedtuple('Ingredient', ['name', 'identifier', 'alc_type', 'basic_taste', 'measure', 'quantity', 'unit'])


class Cocktail:
    def __init__(self, name, category, glasstype, ingredients, preparation, evaluation, origin):
        self.name = name
        self.category = category
        self.glasstype = glasstype
        self.ingredients = ingredients
        self.preparation = preparation
        self.evaluation = evaluation
        self.origin = origin

    def print_preparation(self):
        for s in self.preparation:
            for i in self.ingredients:
                s = s.replace(i.identifier, i.name)
            print(s)

    def print_ingredients(self):
        for i in self.ingredients:
            print(f'{i.measure} {i.name}')
            # print(f'{i.measure} {i.name} ({i.quantity} {i.unit})')


def load_library(file):
    """ Load an XML library of cocktails.

    Args:
        file (string): filename of the XML file

    Returns:
        list: containing objects of type Cocktail
    """

    tree = etree.parse(file)
    cocktails = tree.getroot()
    cocktails_list = []

    for c in cocktails:
        #  Get cocktail information
        name = c.find('name').text
        category = c.find('category').text
        glasstype = c.find('glasstype').text
        evaluation = c.find('evaluation').text
        origin = c.find('origin').text
        ingredients = c.find('ingredients')
        preparation = c.find('preparation')
        preparation_steps = [s.text for s in preparation]

        # Get information about each ingredient
        ingredients_list = []
        for i in ingredients:
            ing = Ingredient(i.text, i.get('id'), i.get('alc_type'), i.get('basic_taste'), i.get('measure'),
                             i.get('quantity'), i.get('unit'))

            ingredients_list.append(ing)

        #  Create and append cocktail object
        cocktails_list.append(Cocktail(name, category, glasstype, ingredients_list,
                                       preparation_steps, evaluation, origin))

    return cocktails_list


def export_library(cocktails, out_name):
    """ Export a library of cocktails to XML.

    Args:
        cocktails (list): containing objects of type Cocktail
        out_name (string): name of the output file
    """

    root = etree.Element("cocktails")

    for c in cocktails:
        # Create xml structure for new cocktail
        cocktail = etree.SubElement(root, "cocktail")

        name = etree.SubElement(cocktail, "name")
        name.text = c.name

        category = etree.SubElement(cocktail, "category")
        category.text = c.category

        glasstype = etree.SubElement(cocktail, "glasstype")
        glasstype.text = c.glasstype

        evaluation = etree.SubElement(cocktail, "evaluation")
        evaluation.text = c.evaluation

        origin = etree.SubElement(cocktail, "origin")
        origin.text = c.origin

        ingredients = etree.SubElement(cocktail, "ingredients")
        for i in c.ingredients:
            ingr = etree.SubElement(ingredients, "ingredient", id=i.identifier,
                                    alc_type=i.alc_type, basic_taste=i.basic_taste, measure=i.measure,
                                    quantity=i.quantity, unit=i.unit)

            ingr.text = i.name

        prep = etree.SubElement(cocktail, "preparation")
        for s in c.preparation:
            step = etree.SubElement(prep, "step")
            step.text = s

        # Write in file
        et = etree.ElementTree(root)
        et.write(os.path.join(DATA_PATH, f'{out_name}.xml'), pretty_print=True, encoding="UTF-8")


if __name__ == "__main__":
    # Example
    xml_file = os.path.join(DATA_PATH, 'case_library.xml')
    cbl = load_library(xml_file)
    export_library(cbl, 'output')
