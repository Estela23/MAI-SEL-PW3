"""

PW3 - SEL - 2021
CBR for a cocktail recipe creator

Authors:    Xavier Cucurull Salamero <xavier.cucurull@estudiantat.upc.edu>
            Daniel Hinjos García <daniel.hinjos@estudiantat.upc.edu>
            Fernando Vázquez Novoa <fernando.vazquez.novoa@estudiantat.upc.edu>
            Estela Vázquez-Monjardín Lorenzo <estela.vazquez-monjardin@estudiantat.upc.edu>
"""

from lxml import etree
import numpy as np
import random

class CBR:
    def __init__(self, cbl_filename):
        tree = etree.parse(cbl_filename)
        self.cocktails = tree.getroot()
        self.alcohol_types = set()
        self.basic_tastes = set()
        
        self._init_structure()
    
    def _init_structure(self):
        """ Initialize library structure
        
        Parse cocktails tree and extract relevant information such as 
        the unique categories, alcohol types, ingredients, etc.
        """

        # Get unique values for alcohol types
        self.alcohol_types.update([i.attrib['alc_type'] for i in self.cocktails.findall('cocktail/ingredients/ingredient')])
        self.alcohol_types.remove('')    # remove empty type

        # Get unique values for basic taste
        self.basic_tastes.update([i.attrib['basic_taste'] for i in self.cocktails.findall('cocktail/ingredients/ingredient')])
        self.basic_tastes.remove('')     # remove empty type

        self.alcohol_dict = {atype: set() for atype in self.alcohol_types}
        self.basic_dict = {btype: set() for btype in self.basic_tastes}

        # Get ingredients of each alcohol type
        for atype in self.alcohol_types:
                self.alcohol_dict[atype].update(set([i.text for i in self.cocktails.findall('cocktail/ingredients/ingredient') 
                                                if i.attrib['alc_type'] == atype]))
                
        # Get ingredients of each basic taste
        for btaste in self.basic_tastes:
                self.basic_dict[btaste].update(set([i.text for i in self.cocktails.findall('cocktail/ingredients/ingredient') 
                                                if i.attrib['basic_taste'] == btaste]))     

    def _process(self, constraints):
        """ CBR principal flow, where the different stages of the CBR will be called

        Args:
            constraints (dict): dictionary containing a set of constraints

        Returns: adapted case and new database

        """
        # RETRIEVAL PHASE
        retrieved_case = self.retrieval(constraints)
        # ADAPTATION PHASE
        adapted_case = self.adaptation(retrieved_case)
        # EVALUATION PHASE
        # LEARNING PHASE
        # TODO: Add the rest of the phases in the future

        return adapted_case, self.cocktails

    def _update_case_library(self, new_case):
        # TODO: update the structure when new cases are added

    def _compute_similarity(self, constraints, cocktail):
        """ Compute the similiraty between a set of constraints and a particular cocktail.

        Start with similarity 0. Then, evaluate each constraint one by one and increase
        similarity according to the feature weight.

        Args:
            constraints (dict): dictionary containing a set of constraints
            cocktail (Element): cocktail Element

        Returns:
            [type]: [description]
        """
        # Start with similarity 0
        sim = 0

        # Get cocktails ingredients and alc_type
        c_ingredients = [i.text for i in cocktail.findall('ingredients/ingredient')]
        c_ingredients_atype = [i.attrib['alc_type'] for i in cocktail.findall('ingredients/ingredient')]
        c_ingredients_btype = [i.attrib['basic_taste'] for i in cocktail.findall('ingredients/ingredient')]

        # Evaluate each constraint one by one
        for key in constraints:
            if constraints[key]:

                # Ingredient constraing has highest importance
                if key == "ingredients":
                    for ingredient in constraints[key]:
                        # Get ingredient alcohol_type, if any
                        ingredient_alc_type = [k for k in self.alcohol_dict if ingredient in self.alcohol_dict[k]]
                        if ingredient_alc_type:
                            itype = "alcohol"
                            ingredient_alc_type = ingredient_alc_type[0]
                        # If the ingredient is not alcoholic, get its basic_taste
                        else:
                            itype = "non-alcohol"
                            ingredient_basic_taste = [k for k in self.basic_dict if ingredient in self.basic_dict[k]][0]

                        # Add 1 if constraint ingredient is used in cocktail
                        if ingredient in c_ingredients:
                            sim += 1

                        # Add 0.5 if constraint ingredient alc_type is used in cocktail
                        elif itype == "alcohol" and ingredient_alc_type in c_ingredients_atype:
                            sim += 1 * 0.5

                        # Add 0.5 if constraint ingredient basic_taste is used in cocktail
                        elif itype == "non-alcohol" and ingredient_basic_taste in c_ingredients_btype:
                            sim += 1 * 0.5

                # Add 0.8 because alochol_type has a lot of importance, but less than the ingredient constraints
                elif key == "alc_type":
                    for atype in constraints[key]:
                        sim += sum([1 * 0.8 for i in cocktail.find("ingredients") if atype == i.attrib['alc_type']])

                # Add 0.8 because basic_taste has a lot of importance, but less than the ingredient constraints
                elif key == "basic_taste":
                    for btype in constraints[key]:
                        sim += sum([1 * 0.8 for i in cocktail.find("ingredients") if btype == i.attrib['basic_taste']])

                # Add 0.4 if glasstype is a match. Glasstype is not very relevant for the case
                elif key == "glasstype":
                    if constraints[key] == cocktail.find(key).text:
                        sim += 1 * 0.4

                # If one of the excluded elements in the constraint is found in the cocktail, similarity is reduced
                elif key == "exc_ingredients":
                    for ingredient in constraints[key]:
                        # Get excluded_ingredient alcohol_type, if any
                        exc_ingredient_alc_type = [k for k in self.alcohol_dict if ingredient in self.alcohol_dict[k]]
                        if exc_ingredient_alc_type:
                            itype = "alcohol"
                            exc_ingredient_alc_type = exc_ingredient_alc_type[0]
                        # If the excluded_ingredient is not alcoholic, get its basic_taste
                        else:
                            itype = "non-alcohol"
                            exc_ingredient_basic_taste = [k for k in self.basic_dict if ingredient in self.basic_dict[k]][0]

                        # Decrease similarity by -2 if ingredient excluded is found in cocktail
                        if ingredient in c_ingredients:
                            sim -= 2

                        # Decrease similarity by -1 if if excluded ingredient alc_type is used in cocktail
                        elif itype == "alcohol" and exc_ingredient_alc_type in c_ingredients_atype:
                            sim -= 1

                        # Decrease similarity by -1 if if excluded ingredient basic_taste is used in cocktail
                        elif itype == "non-alcohol" and exc_ingredient_basic_taste in c_ingredients_btype:
                            sim -= 1
        return sim

    def retrieval(self, constraints):
        """ Retrieve most appropriate cocktail given the provided constraints.
        
        It does a structured search by first filtering by the category.
        Then, the architecture is like a flat memory.

        Args:
            constraints (ditc): dictionary of constraints
        """
        # SEARCHING PHASE
        # Filter elements that correspond to the category constraint
        if len(constraints['category']):
            searching_list = [child for child in self.cocktails if child.find('category').text == constraints['category']]
        # If category constraint is empty, the outcome of the searching phase is the whole dataset
        else:
            searching_list = [child for child in self.cocktails]

        # SELECTION PHASE
        # Compute similarity with each of the cocktails of the searching list
        sim_list = [self._compute_similarity(constraints, c) for c in searching_list]

        # Retrieve case with higher similarity
        max_indices = np.argwhere(np.array(sim_list) == np.amax(np.array(sim_list))).flatten().tolist()
        # If there is more than one case with the same highest similarity (ties), one will be selected randomly
        if len(max_indices) > 1:
            index_retrieved = random.choice(max_indices)
        else:
            index_retrieved = max_indices[0]
        retrieved_case = searching_list[index_retrieved]
        retrieved_case_name = retrieved_case.find('name').text
        print("Retrieved case: " + str(retrieved_case_name))

        return retrieved_case

    def adaptation(self):
        return


# To test RETRIEVAL step
#constraints = {'category': 'Cocktail', 'glasstype': 'Beer glass', 'ingredients': ['Amaretto'],
#                'alc_type': ['Rum'], 'basic_type': ['Sweet'], 'exc_ingredients': ['Vodka']}

#cbr = CBR("Data/case_library.xml")
#case_retrieved = cbr.retrieval(constraints)
