from lxml import etree
import numpy as np


# Import Case Library (XML)
# Import XML tree
tree = etree.parse('Data/case_library.xml')
cocktails = tree.getroot()

# Obtaining contraints/input:
# TODO: this should come from a JSON or from an input on the command line
constraints = {'category': 'Cocktail', 'glasstype': 'Beer glass', 'ingredients': ['Vodka', 'Amaretto'],
                'alc_type': ['Rum']}

# TODO create a CBR class
# TODO create a method of the CBR that initializes the structure
# TODO create a method of the CBR that updates the structure when new cases are added

# SEARCHING PHASE
# Constructing hierarchical tree
alcohol_types = set()
basic_tastes = set()

# Get unique values for alcohol types
alcohol_types.update([i.attrib['alc_type'] for i in cocktails.findall('cocktail/ingredients/ingredient')])
alcohol_types.remove('')    # remove empty type

# Get unique values for basic taste
basic_tastes.update([i.attrib['basic_taste'] for i in cocktails.findall('cocktail/ingredients/ingredient')])
basic_tastes.remove('')     # remove empty type

alcohol_dict = {atype: set() for atype in alcohol_types}
basic_dict = {btype: set() for btype in basic_tastes}

# Get ingredients of each alcohol type
for atype in alcohol_types:
        alcohol_dict[atype].update(set([i.text for i in cocktails.findall('cocktail/ingredients/ingredient') 
                                        if i.attrib['alc_type'] == atype]))
        
 # Get ingredients of each basic taste
for btaste in basic_tastes:
        basic_dict[btaste].update(set([i.text for i in cocktails.findall('cocktail/ingredients/ingredient') 
                                        if i.attrib['basic_taste'] == btaste]))       

# Filter elements that correspond to the category constraint
searching_list = [child for child in cocktails if child.find('category').text == constraints['category']]
# If category constraint is empty, the outcome of the searching phase is the whole dataset
if not searching_list:
    searching_list = [child for child in cocktails]
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