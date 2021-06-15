import argparse
import json
import os
import time
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from lxml import etree
from create_case_library import insert_ingredient, add_preparation

from cbr import CBR
from create_case_library import create_xml_library


def create_xml_library_tests(csv):
    # Read .CSV
    dataset = pd.read_csv(csv, encoding='utf_8')
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
                previous_preparation = dataset.iloc[idx - 1]["strInstructions"]
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
            category.text = instance[1].lower()
            glasstype = etree.SubElement(cocktail, "glasstype")
            glasstype.text = instance[2].lower()
            ingredients = etree.SubElement(cocktail, "ingredients")
            insert_ingredient(ingredient_index, instance, ingredients)
            ingredient_index += 1
            ingredients_list = [instance[3].lower()]

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

    # Order by category
    new_cocktails = etree.Element("cocktails")
    categories = set([c.find('category').text for c in cocktails])
    for cat in categories:
        cat_cases = [c for c in cocktails if c.find("category").text == cat]
        for case in cat_cases:
            new_cocktails.append(case)

    # Write in file
    et = etree.ElementTree(new_cocktails)
    et.write('../Data/case_library.xml', pretty_print=True, encoding="UTF-8")


def parse_arguments():
    """ Define program input arguments and parse them.
    """
    # Create the parser and add arguments
    parser = argparse.ArgumentParser()
    parser.add_argument(dest='path', type=str, help="path where the csv file is")
    parser.add_argument(dest='tests', type=str, help="path where the json test file is")

    # Parse arguments
    args = parser.parse_args()

    return args


def perform_tests(args):
    create_xml_library_tests(args.path)
    cbr = CBR("../Data/case_library.xml")
    get_new_case_times = []
    evaluated_learn_new_case_times = []
    with open(args.tests) as json_file:
        data = json.load(json_file)
        for key, value in data.items():
            # Get test constraints of each case
            constraints = value
            # Get new case
            start_ra = time.time()
            retrieved_case, adapted_case, original = cbr.get_new_case(constraints)
            end_ra = time.time()
            get_new_case_times.append(end_ra - start_ra)

            # Evaluate if cocktail is derived (not original)
            start_el = time.time()
            if not original:
                cbr.evaluate_new_case(retrieved_case, adapted_case, 8.0)
            end_el = time.time()
            evaluated_learn_new_case_times.append(end_el - start_el)

            total_times = np.array(get_new_case_times) + np.array(evaluated_learn_new_case_times)

        mean_ra_time = np.mean(np.array(get_new_case_times))
        mean_el_time = np.mean(np.array(evaluated_learn_new_case_times))
        mean_total_time = np.mean(total_times)
        print(f"The average time needed for retrieval and adaptation steps is : {mean_ra_time}")
        print(f"The average time needed for evaluation and adaptation steps is: {mean_el_time}")
        print(f"The average total time for the complete CBR cycle over a new case is : {mean_total_time}")

        experiments = [i for i in range(len(total_times))]
        plt.plot(experiments, total_times, color="red", label="Total time")
        plt.plot(experiments, np.array(get_new_case_times), color="green", label="Retrieval and Adaptation")
        plt.plot(experiments, np.array(evaluated_learn_new_case_times), color="blue", label="Evaluation and Learning")
        plt.title("Times needed in each phase for 100 experiments")
        plt.xlabel("Queries performed")
        plt.ylabel("Time in seconds")
        plt.legend(loc="upper left")
        plt.show()

    with open("results.txt", 'w') as output:
        print(get_new_case_times, file=output)
        print(evaluated_learn_new_case_times, file=output)


if __name__ == "__main__":
    # Input arguments
    args = parse_arguments()

    # tests
    perform_tests(args)
