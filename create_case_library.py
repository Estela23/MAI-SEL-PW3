import pandas as pd
import numpy as np
import os
import re
from lxml import etree

DATA_PATH = 'Data'


# Method to insert ingredient
def insert_ingredient(ingr_id, instance, ingredients):
    """ Insert an ingredient to the ingredients parent element.

    Args:
        ingr_id (int): ingredient identifier
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

    ingr = etree.SubElement(ingredients, "ingredient", id=f"ingr{ingr_id+1}",
                            alc_type=str(alc_type), basic_taste=basic_taste, measure=str(measure),
                            quantity=str(quantity), unit=str(unit))

    ingr.text = str(instance[3]).lower()


def add_preparation(preparation, cocktail_el, ingredients):
    """ Add preparation steps to the cocktail element

    Args:
        preparation (string): string containing the preparation steps
        cocktail_el (Element): cocktail element
        ingredients (list): containing the cocktail ingredients name
    """
    prep = etree.SubElement(cocktail_el, "preparation")
    
    # Divide preparation steps and add them individually
    steps = str(preparation).split(". ")
    
    for s in steps:
        # Replace ingredient in steps
        for ingr_id, ingredient in enumerate(ingredients):
            ingr_pattern = r"\b({})\b".format(ingredient)
            s = re.sub(ingr_pattern, f"ingr{ingr_id+1}", s, flags=re.IGNORECASE)
            
        step = etree.SubElement(prep, "step")
        step.text = s.capitalize()


def create_xml_library(csv):
    # Read .CSV
    dataset = pd.read_csv(csv_file, encoding='utf_8')
    dataset = dataset.drop(dataset.columns[0], axis=1)
    dataset = dataset.drop(dataset.columns[-2:], axis=1)

    # Start creating XML tree
    cocktails = etree.Element("cocktails")
    previous_cocktail = ""
    ingredients_list = []
    ingredient_index = 0
    ingredients = None
    cocktail = None

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
            # If we are not in the first cocktail
            if idx != 0:
                # Add preparation xml structure for the previous cocktail
                previous_preparation = dataset.iloc[idx-1]["strInstructions"]  
                add_preparation(previous_preparation, cocktail, ingredients_list)
                utility = etree.SubElement(cocktail, "utility")
                utility.text = str(1.0)
                derivation = etree.SubElement(cocktail, "derivation")
                derivation.text = "Original"
                evaluation = etree.SubElement(cocktail, "evaluation")
                evaluation.text = 'Success'  # cases from dataset are successful by default

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

    # Add the preparation xml structure for the final cocktail
    preparation = instance[6] 
    add_preparation(preparation, cocktail, ingredients_list)
    utility = etree.SubElement(cocktail, "utility")
    utility.text = str(1.0)
    derivation = etree.SubElement(cocktail, "derivation")
    derivation.text = "Original"
    evaluation = etree.SubElement(cocktail, "evaluation")
    evaluation.text = 'Success'  # cases from dataset are successful by default

    # Write in file
    et = etree.ElementTree(cocktails)
    et.write(os.path.join(DATA_PATH, 'case_library.xml'), pretty_print=True, encoding="UTF-8")


if __name__ == "__main__":
    csv_file = os.path.join(DATA_PATH, 'data_cocktails.csv')
    create_xml_library(csv_file)
