import pandas as pd
import numpy as np
import os
from lxml import etree

DATA_PATH = 'Data'

# Method to insert ingredient
def insert_ingredient(id, instance, ingredients):
    """ Insert an ingredient to the ingredients parent element.

    Args:
        id (int): ingredient identifier
        instance (list): row of data from the dataset
        ingredients (Element): parent element
    """
    alc_type = ""
    if isinstance(instance[4], str):
        alc_type = instance[4]
    basic_taste = ""
    if isinstance(instance[5], str):
        basic_taste = instance[5]
    measure = ""
    if isinstance(instance[-3], str):
        measure = instance[-3]
    if np.isnan(instance[-1]) and np.isnan(instance[-2]):
        quantity = ""
        unit = ""
    elif np.isnan(instance[-1]):
        quantity = instance[-2]
        unit = "ml"
    else:
        quantity = instance[-1]
        unit = "gr"

    ingr = etree.SubElement(ingredients, "ingredient", id=str("ingr" + str(id + 1)),
                            alc_type=str(alc_type), basic_taste=basic_taste, measure=str(measure),
                            quantity=str(quantity), unit=str(unit))

    ingr.text = str(instance[3])

def add_preparation(preparation, cocktail_el, ingredients):
    """ Add preparation steps to the cocktail element

    Args:
        preparation (string): string containing the preparation steps
        cocktail_el (Element): cocktail element
        ingredients (list): containing the cocktail ingredients name
    """
    return

def create_xml_library(csv):
    # Read .CSV
    dataset = pd.read_csv(csv_file, encoding='utf_8')
    dataset = dataset.drop(dataset.columns[0], axis=1)
    dataset = dataset.drop(dataset.columns[-2:], axis=1)


    # Start creating XML tree
    cocktails = etree.Element("cocktails")
    previous_cocktail = ""
    ingredients_list = []

    # Loop over all instances of the dataset
    for idx, instance in enumerate(dataset.values):
        # If the cocktail is the same
        if instance[0] == previous_cocktail:
            # Add ingredient
            insert_ingredient(ingredient_index, instance, ingredients)
            ingredient_index += 1
            ingredients_list.append(instance[3])
            
        # If another cocktail appears
        else:
            # Create the preparation xml structure for the previous cocktail
            # (If we are not in the first cocktail)
            if idx != 0:
                previous_preparation = dataset.iloc[idx-1]["strInstructions"]  
                prep = etree.SubElement(cocktail, "preparation")
                
                # Divide preparation steps and add them individually
                steps = str(previous_preparation).split(". ")
                for s in steps:
                    step = etree.SubElement(prep, "step")
                    step.text = s.capitalize()

            # Create xml structure for new cocktail
            ingredient_index = 0
            cocktail = etree.SubElement(cocktails, "cocktail")
            name = etree.SubElement(cocktail, "name")
            name.text = instance[0]
            category = etree.SubElement(cocktail, "category")
            category.text = instance[1]
            glasstype = etree.SubElement(cocktail, "glasstype")
            glasstype.text = instance[2]
            ingredients = etree.SubElement(cocktail, "ingredients")
            insert_ingredient(ingredient_index, instance, ingredients)
            ingredient_index += 1
            ingredients_list = [instance[3]]
        
        previous_cocktail = instance[0]

    # Create the preparation xml structure for the final cocktail
    preparation = instance[6] 
    prep = etree.SubElement(cocktail, "preparation")

    # Divide preparation steps and add them individually
    steps = str(preparation).split(". ")
    for s in steps:
        step = etree.SubElement(prep, "step")
        step.text = s.capitalize()

    # Write in file
    et = etree.ElementTree(cocktails)
    et.write(os.path.join(DATA_PATH, 'case_library.xml'), pretty_print=True, encoding="UTF-8")
    
if __name__ == "__main__":
    csv_file = os.path.join(DATA_PATH, 'data_cocktails.csv')
    create_xml_library(csv_file)