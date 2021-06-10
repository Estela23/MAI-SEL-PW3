from lxml import etree
import numpy as np

# Import XML tree
tree = etree.parse('case_library.xml')
cocktails = tree.getroot()

# Obtaining contraints/input:
constraints = {'category': 'Cocktail', 'glasstype': 'Beer glass', 'ingredients': ['Vodka', 'Amaretto'],
               'alc_type': ['Rum']}

# SEARCHING PHASE
# Constructing hierarchical tree
#categories = set([child.find('category').text for child in cocktails])
#print(categories)

searching_list = [child for child in cocktails if child.find('category').text == constraints['category']]
print(searching_list)

# SELECTION PHASE
def compute_similarity(input, case):
    sim = 0
    for key in input:
        if input[key]:
            if key == "ingredients" or key == "alc_type":
                for i in case.find("ingredients"):
                    if input[key] == i.text:
                        sim += 1
                    if input[key] == i.attrib['alc_type']:
                        sim += 1
            else:
                if input[key] == case.find(key).text:
                    sim += 1
    return sim

sim_list = [compute_similarity(constraints, c) for c in searching_list]

retrieved_case = searching_list[np.argmax(np.array(sim_list))]
retrieved_case_name = retrieved_case.find('name').text
print(retrieved_case_name)