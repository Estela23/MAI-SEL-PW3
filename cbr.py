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
    
    def _compute_similarity(self, constraints, cocktail):
        """ Compute the similiraty between a set of constraints and a particular cocktail.

        Args:
            constraints (dict): dictionary containing a set of constraints
            cocktail (Element): cocktail Element

        Returns:
            [type]: [description]
        """
        sim = 0
        for key in constraints:
            if constraints[key]:
                if key == "ingredients":
                    for ingredient in constraints[key]:
                        ingredient_alc_type = [k for k in self.alcohol_dict if ingredient in self.alcohol_dict[k]][0]
                        for i in cocktail.find(key):
                            if constraints[key] == i.text:
                                sim += 1
                            elif ingredient_alc_type == i.attrib['alc_type']:
                                sim += 0.5
                elif key == "alc_type":
                    for atype in constraints[key]:
                        sim += sum([1 for i in cocktail.find("ingredients") if atype == i.attrib['alc_type']])
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
        # Filter elements that correspond to the category constraint
        if len(constraints['category']):
            searching_list = [child for child in self.cocktails if child.find('category').text == constraints['category']]
        
        # If category constraint is empty, the outcome of the searching phase is the whole dataset
        else:
            searching_list = [child for child in self.cocktails]
        
        # Compute similarity with each of the cocktails of the searching list
        sim_list = [self._compute_similarity(constraints, c) for c in searching_list]

        # Retrieve case with higher similarity
        # TODO: what to do if more than one have same similarity?
        #       if using the first, the result will depend on initialization
        #       if using a random one, it won't be deterministic
        retrieved_case = searching_list[np.argmax(np.array(sim_list))]
        retrieved_case_name = retrieved_case.find('name').text
        
        return retrieved_case

    def adaptation(self):
        return