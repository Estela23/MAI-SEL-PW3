from lxml import etree
import numpy as np


def retrieval_step():
    # Import XML tree
    tree = etree.parse('Data/case_library.xml')
    cocktails = tree.getroot()

    # Obtaining contraints/input:
    constraints = {'category': 'Cocktail', 'glasstype': 'Beer glass', 'ingredients': ['Vodka', 'Amaretto'],
                   'alc_type': ['Rum']}

    # SEARCHING PHASE
    # Constructing hierarchical tree
    alcohol_types = set([child.find('ingredients').find('ingredient').attrib['alc_type'] for child in cocktails])
    basic_types = set([child.find('ingredients').find('ingredient').attrib['basic_taste'] for child in cocktails])

    alcohol_dict = {}
    for atype in alcohol_types:
        brands = set([child.find('ingredients').find('ingredient').text for child in cocktails
                      if child.find('ingredients').find('ingredient').attrib['alc_type'] == atype])
        alcohol_dict.update({atype: brands})

    basic_dict = {}
    for atype in basic_types:
        brands = set([child.find('ingredients').find('ingredient').text for child in cocktails
                      if child.find('ingredients').find('ingredient').attrib['basic_taste'] == atype])
        basic_dict.update({atype: brands})

    # categories = [child.find('category').text for child in cocktails]
    # categories = set([child.find('category').text for child in cocktails])
    # print(categories)

    searching_list = [child for child in cocktails if child.find('category').text == constraints['category']]
    print([child.find("name").text for child in searching_list])

    # SELECTION PHASE
    def compute_similarity(input, case):
        sim = 0
        for key in input:
            if input[key]:
                if key == "ingredients":
                    for ingredient in input[key]:
                        ingredient_alc_type = [k for k in alcohol_dict if ingredient in alcohol_dict[k]][0]
                        for i in case.find(key):
                            if input[key] == i.text:
                                sim += 1
                            elif ingredient_alc_type == i.attrib['alc_type']:
                                sim += 0.5
                elif key == "alc_type":
                    for atype in input[key]:
                        sim += sum([1 for i in case.find("ingredients") if atype == i.attrib['alc_type']])
                # TODO: tener en cuenta más restricciones como "spicy/cream taste" para los basic_taste
                else:
                    if input[key] == case.find(key).text:
                        sim += 1
        return sim

    sim_list = [compute_similarity(constraints, c) for c in searching_list]

    retrieved_case = searching_list[np.argmax(np.array(sim_list))]
    retrieved_case_name = retrieved_case.find('name').text
    print(retrieved_case_name)

    return constraints, retrieved_case
