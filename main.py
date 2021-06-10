import pandas as pd
import numpy as np
from lxml import etree
print("running with lxml.etree")

# Read .CSV
dataset = pd.read_csv("data_cocktails.csv", encoding='utf_8')
dataset = dataset.drop(dataset.columns[0], axis=1)
dataset = dataset.drop(dataset.columns[-2:], axis=1)
# print(dataset.columns)
print(dataset.heead(10))


# Method to insert ingredient
def insert_ingredient(id, instance, ingredients):
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


# Start creating XML tree
cocktails = etree.Element("cocktails")
# print(len(dataset["strInstructions"].unique()))
previous_cocktail = ""

# Loop over all instances of the dataset
for idx, instance in enumerate(dataset.values):
    # If the cocktail is the same
    if instance[0] == previous_cocktail:
        insert_ingredient(ingredient_index, instance, ingredients)
        ingredient_index += 1
    # If another cocktail appears
    else:
        # Create the preparation xml structure for the previous cocktail
        # (If we are not in the first cocktail)
        if idx != 0:
            previous_preparation = dataset.iloc[idx-1]["strInstructions"]
            # Cocktail preparation for the first cocktail (steps by numbers)
            if idx == 2:
                prep = etree.SubElement(cocktail, "preparation")
                steps = []
                step1, steps23 = str(previous_preparation).split("2.")
                step2, step3 = steps23.split("3.")
                steps.append(step1)
                steps.append("2. " + step2.capitalize())
                steps.append("3. " + step3.capitalize())
                for steptext in steps:
                    step = etree.SubElement(prep, "step")
                    step.text = str(steptext)
            else:
                prep = etree.SubElement(cocktail, "preparation")
                # Cocktail preparation for a cocktail whose steps contain points (.)
                if "." in str(previous_preparation):
                    steps = str(previous_preparation).split(". ")
                    for s in steps:
                        step = etree.SubElement(prep, "step")
                        step.text = s.capitalize()
                # Cocktail preparation for a cocktail whose steps contain commas (,)
                else:
                    step = etree.SubElement(prep, "step")
                    step.text = str(previous_preparation).capitalize()

        # Creating xml structure for new cocktail
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

    # If final instance, create the preparation xml structure for the final cocktail
    if idx == (dataset.shape[0]-1):
        prep = etree.SubElement(cocktail, "preparation")
        if "." in str(instance[6]):
            steps = str(instance[6]).split(". ")
            for s in steps:
                step = etree.SubElement(prep, "step")
                step.text = s.capitalize()
        else:
            step = etree.SubElement(prep, "step")
            step.text = str(instance[6]).capitalize()

    previous_cocktail = instance[0]

# Write in file
# print(etree.tostring(cocktails, pretty_print=True).decode())
et = etree.ElementTree(cocktails)
et.write('case_library.xml', pretty_print=True, encoding="UTF-8")


