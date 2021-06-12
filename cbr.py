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

# TODO create a method of the CBR that updates the structure when new cases are added
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

    def compute_similarity(self, constraints, cocktail):
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
        c_ingredients_btype = [i.attrib['basic_type'] for i in cocktail.findall('ingredients/ingredient')]

        # Evaluate each constraint one by one
        for key in constraints:
            if constraints[key]:
                # Ingredient constraing has highest importance
                if key == "ingredients":
                    for ingredient in constraints[key]:
                        # Get ingredient alcohol type
                        ingredient_alc_type = [k for k in self.alcohol_dict if ingredient in self.alcohol_dict[k]][0]
                        # Get ingredient alcohol type
                        ingredient_basic_type = [k for k in self.basic_dict if ingredient in self.basic_dict[k]][0]

                        # Add 1 if constraint ingredient is used in cocktail
                        if ingredient in c_ingredients:
                            sim += 1

                        # Add 0.5 if constraint ingredient alc_type is used in cocktail
                        elif ingredient_alc_type in c_ingredients_atype:
                            sim += 0.5

                        # Add 0.5 if constraint ingredient basic_type is used in cocktail
                        elif ingredient_basic_type in c_ingredients_btype:
                            sim += 0.5

                # Alochol type is the second most important
                elif key == "alc_type":
                    for atype in constraints[key]:
                        sim += sum([1 for i in cocktail.find("ingredients") if atype == i.attrib['alc_type']])

                elif key == "basic_taste":
                    for btype in constraints[key]:
                        sim += sum([1 for i in cocktail.find("ingredients") if btype == i.attrib['basic_type']])
                        
                # TODO: tener en cuenta más restricciones como "spicy/cream taste" para los basic_taste

                else:
                    if constraints[key] == cocktail.find(key).text:
                        sim += 1
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


constraints = {'category': 'Cocktail', 'glasstype': 'Beer glass', 'ingredients': ['Amaretto'],
                'alc_type': ['Rum'], 'basic_type': ['Sweet'], 'exc_ingredients': ['Vodka']}
