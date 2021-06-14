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
import itertools
from collections import namedtuple
from copy import deepcopy
import re

# Declare Ingredient namedtuple() 
Ingredient = namedtuple('Ingredient', ['name', 'identifier', 'alc_type', 'basic_taste', 'measure', 'quantity', 'unit'])


class CBR:
    """ Class that implements our Case Based Reasoning algorithm.
    """
    
    def __init__(self, cbl_filename, threshold_eval=8.0, verbose=False):
        """ Initialize CBR.

        Args:
            cbl_filename (string): filename of the XML case library
            verbose (boolean, optional): defines if execution messages are printed in the terminal. 
                                         Defaults to False.
        """
        self.cbl_filename = cbl_filename
        self.tree = etree.parse(cbl_filename)
        self.cocktails = self.tree.getroot()
        self.alcohol_types = set()
        self.basic_tastes = set()
        self.glass_types = set()
        self.categories = set()
        self.cocktail_names = set()
        self.ingredients_list = []
        self.ingredient_names = []
        self.threshold_eval = threshold_eval

        self._init_structure()
        
        self.verboseprint = print if verbose else lambda *a, **k: None

    def _init_structure(self):
        """ Initialize library structure
        
        Parse cocktails tree and extract relevant information such as 
        the unique categories, alcohol types, ingredients, etc.
        """
        # Get unique categories
        self.categories = set([c.find('category').text for c in self.cocktails])

        # Get unique cocktail names
        self.cocktail_names = set([c.find('name').text for c in self.cocktails])

        # Get unique values for glass type
        self.glass_types = set([c.find('glasstype').text for c in self.cocktails])
        
        # Get unique values for alcohol types
        self.alcohol_types.update(
            [i.attrib['alc_type'] for i in self.cocktails.findall('cocktail/ingredients/ingredient')])
        self.alcohol_types.remove('')  # remove empty type

        # Get unique values for basic taste
        self.basic_tastes.update(
            [i.attrib['basic_taste'] for i in self.cocktails.findall('cocktail/ingredients/ingredient')])
        self.basic_tastes.remove('')  # remove empty type
        
        # Get dicts of alcohol types and basic tastes
        self.alcohol_dict = {atype: set() for atype in self.alcohol_types}
        self.basic_dict = {btype: set() for btype in self.basic_tastes}

        # Get ingredients of each alcohol type
        for atype in self.alcohol_types:
            self.alcohol_dict[atype].update(
                set([i.text for i in self.cocktails.findall('cocktail/ingredients/ingredient')
                     if i.attrib['alc_type'] == atype]))

        # Get ingredients of each basic taste
        for btaste in self.basic_tastes:
            self.basic_dict[btaste].update(
                set([i.text for i in self.cocktails.findall('cocktail/ingredients/ingredient')
                     if i.attrib['basic_taste'] == btaste]))
            
        # Get all ingredients
        self.ingredients_list = [Ingredient(i.text, i.get('id'), i.get('alc_type'), i.get('basic_taste'), 
                                            i.get('measure'), i.get('quantity'), i.get('unit')) 
                                 for i in self.cocktails.findall('cocktail/ingredients/ingredient')]
        self.ingredient_names = [i.name for i in self.ingredients_list]

        # Define history for all cases in case library, containing number of successes and failures
        self.cases_history = {}
        [self.cases_history.update({c.find("name").text:[0,0]}) for c in self.cocktails]

        # Define a structure that stores all the cases of the dataset divided by category
        self.categories = set([c.find("category").text for c in self.cocktails])
        self.library_by_category = {}
        [self.library_by_category.update({cat: [c for c in self.cocktails
                                                if c.find('category').text == cat]}) for cat in self.categories]

        # Define weight structure
        self.similarity_weights = {}
        self.similarity_cases = ["ingr_match", "ingr_alc_type_match", "ingr_basic_taste_match", "alc_type_match",
                                 "basic_taste_match", "glasstype_match", "exc_ingr_match", "exc_ingr_alc_type_match",
                                 "exc_ingr_basic_taste_match", "exc_alc_type", "exc_basic_taste"]
        self.similarity_weights_values = [1.0, 0.6, 0.6, 0.8, 0.8, 0.4, -1.0, -0.6, -0.6, -1.0, -1.0]
        [self.similarity_weights.update({sim_case: sim_weight})
         for sim_case, sim_weight in zip(self.similarity_cases, self.similarity_weights_values)]

    def _set_similarity_weights(self, new_weights):
        """ Method to set new similarity weights

        Args:
            new_weights (list): list containing new similarity weights

        Returns:

        """
        if len(new_weights) != len(self.similarity_weights_values):
            print("ERROR: You have to introduce a list of {} total similarity weights"
                  .format(len(self.similarity_weights_values)))
            return

        new_weights_dict = {}
        [new_weights_dict.update({sim_case: sim_weight})
         for sim_case, sim_weight in zip(self.similarity_cases, new_weights)]

        self.similarity_weights.update(new_weights_dict)
        return

    def _get_similarity_weights(self):
        """ Method to obtain the current similarity weights

        Returns: similarity_weights (list): current similarity weights

        """
        print(self.similarity_weights)
        return self.similarity_weights

    def _print_ingredients(self, cocktail):
        """ Print the ingredients (with measures) of the given cocktail.

        Args:
            cocktail (Element): cocktail Element
        """
        ingr_str = ""
        
        for i in cocktail.findall('ingredients/ingredient'):
            print(f'{i.get("measure")} {i.text}')
            ingr_str += f'{i.get("measure")} {i.text}\n'
        
        return ingr_str
            
    def _print_preparation(self, cocktail):
        """ Print the preparation steps (with ingredient names) of the given cocktail.

        Args:
            cocktail (Element): cocktail Element
        """
        prep_str = ""
        
        for s in cocktail.findall('preparation/step'):
            step = s.text
            for i in cocktail.findall('ingredients/ingredient'):
                ingr_pattern = r"\b({})\b".format(i.get('id'))
                step = re.sub(ingr_pattern, i.text, step)
            prep_str += f'{step}\n'
            print(step)
            
        return prep_str

    def _evaluate_constraints_fulfillment(self, constraints, cocktail):
        """ Check that a cocktail fulfills all the requiered constraints.

        Args:
            constraints (dict): constraints to fulfill
            cocktail (Element): cocktail Element to evaluate
        """
        ckt_category = cocktail.find('category').text
        ckt_glass = cocktail.find('glasstype').text
        ckt_ingredients = [i.text for i in cocktail.findall('ingredients/ingredient')]
        ckt_alc_types = [i.get('alc_type') for i in cocktail.findall('ingredients/ingredient')]
        ckt_basic_tastes = [i.get('basic_taste') for i in cocktail.findall('ingredients/ingredient')]

        cnst_categories = constraints.get('category')
        cnst_glass = constraints.get('glass_type')
        cnst_ingredients = constraints.get('ingredients')
        cnst_alc_types = constraints.get('alc_type')
        cnst_basic_tastes = constraints.get('basic_taste')
        cnst_exc_ingredients = constraints.get('exc_ingredients')
        cnst_exc_alc_types = constraints.get('exc_alc_type')
        cnst_exc_basic_tastes = constraints.get('exc_basic_taste')

        evaluation = []
        evaluation_results = []

        # Check cocktail category
        if cnst_categories:
            if ckt_category in cnst_categories:
                evaluation.append(True)
            else:
                evaluation.append(False)
                evaluation_results.append('Category constraint failed')

        # Check glass type
        if cnst_glass:
            if ckt_glass in cnst_glass:
                evaluation.append(True)
            else:
                evaluation.append(False)
                evaluation_results.append('Glass constraint failed')

        # Check that cocktail contains ingredients
        if cnst_ingredients:
            if all(i in ckt_ingredients for i in cnst_ingredients):
                evaluation.append(True)
            else:
                evaluation.append(False)
                evaluation_results.append('Ingredients constraint failed')

        # Check that cocktail does not contain any of the excluded ingredients
        if cnst_exc_ingredients:
            if not any(i in ckt_ingredients for i in cnst_exc_ingredients):
                evaluation.append(True)
            else:
                evaluation.append(False)
                evaluation_results.append('Excluded ingredients constraint failed')

        # Check alc_type
        if cnst_alc_types:
            if all(i in ckt_alc_types for i in cnst_alc_types):
                evaluation.append(True)
            else:
                evaluation.append(False)
                evaluation_results.append('Alcohol types constraint failed')

        # Check that cocktail does not contain any of the excluded alcohol types
        if cnst_exc_alc_types:
            if not any(i in ckt_alc_types for i in cnst_exc_alc_types):
                evaluation.append(True)
            else:
                evaluation.append(False)
                evaluation_results.append('Excluded alcohol types constraint failed')

        # Check basic_taste
        if cnst_basic_tastes:
            if all(i in ckt_basic_tastes for i in cnst_basic_tastes):
                evaluation.append(True)
            else:
                evaluation.append(False)
                evaluation_results.append('Basic tastes constraint failed')

        # Check that cocktail does not contain any of the excluded alcohol types
        if cnst_exc_basic_tastes:
            if not any(i in ckt_basic_tastes for i in cnst_exc_basic_tastes):
                evaluation.append(True)
            else:
                evaluation.append(False)
                evaluation_results.append('Excluded basic tastes constraint failed')

        return False not in evaluation, evaluation_results

    def _process(self, constraints):
        """ CBR principal flow, where the different stages of the CBR will be called

        Args:
            constraints (dict): dictionary containing a set of constraints

        Returns: adapted case and new database

        """
        # RETRIEVAL PHASE
        retrieved_case = self._retrieval(constraints)
        # ADAPTATION PHASE
        adapted_case, n_changes = self._adaptation(retrieved_case)
        # EVALUATION PHASE
        adapted_case, ev_score = self._evaluation(adapted_case)
        # LEARNING PHASE
        self._learning(retrieved_case, adapted_case, ev_score)
        # TODO: Add the rest of the phases in the future

        return adapted_case, self.cocktails

    def _learning(self, retrieved_case, adapted_case, ev_score):
        """ Learning phase in order to decide if the evaluated case is a success or a failure, and act consequently

        Args:
            retrieved_case (Element): case resulting from retrieval phase
            adapted_case (Element): case resulting from adaptation phase, which has been evaluated

        Returns:

        """
        # MANAGING UTILITY SCORE OF THE RETRIEVED CASE
        # Update the cases_history of the retrieved case based on the status
        # If the adapted case is a success, according to the human oracle
        if adapted_case.find('evaluation').text == "Success":
            self.cases_history[retrieved_case.find("name").text][0] += 1
        # If the adapted case is a failure, according to the human oracle
        elif adapted_case.find('evaluation').text == "Failure":
            self.cases_history[retrieved_case.find("name").text][1] += 1

        # Compute utility score for retrieved_case
        utility_score = (self.cases_history[retrieved_case.find("name").text][0] - \
                        self.cases_history[retrieved_case.find("name").text][1] + 1) / 2

        # If utility score is 0.0, remove retrieved_case from case library, from cases_history and from library_by_category
        if utility_score == 0.0:
            self.cocktails.remove(retrieved_case)
            rem = self.cases_history.pop([retrieved_case.find("name").text], None)
            if rem == None:
                print("ERROR: You are trying to delete a cocktail that doesn't exist in the cases_history structure")
            self.library_by_category[retrieved_case.find("category").text] = self.library_by_category[retrieved_case.find("category").text].remove(retrieved_case)
       
        # Otherwise, update retrieved case utility score if the computed utility score has changed
        elif str(utility_score) != retrieved_case.find("utility").text:
            for c in self.cocktails:
                if c.find("name").text == retrieved_case.find("name").text:
                    c.find("utility").text = str(utility_score)
                    break

        # Initialize utility of adapted_case to 1.0 always
        # TODO: what to do with failures when multiplying by ev_score
        adapted_case.find("utility").text = str(1.0 * ev_score)

        # Add new adapted_case to case library
        self._update_case_library(adapted_case)
        self.cocktail_names.update(adapted_case.find('name').text)
        
        # Update case_history with the adapted case:
        self.cases_history.update({adapted_case.find('name').text: [0, 0]})
        
        # Update library_by_category
        self.library_by_category[adapted_case.find("category").text] = self.library_by_category[adapted_case.find("category").text].append(adapted_case)

        # TODO: Decide what to do with failures
        '''
        # FOR WHEN DECIDING WHAT TO DO WITH FAILURES
        if adapted_case.find('evaluation').text == "Success":
            # Update case_history with the adapted case:
            self.cases_history.update({adapted_case.find('name').text: [0,0]})
            # Add new adapted_case to case library
            self._update_case_library(adapted_case)
        else:
            # TODO: Decide what to do with failures
            print()
        '''

        return

    def _update_case_library(self, new_case):
        """ Update the case_library with a new case

        Args:
            new_case (Element): new cocktail element to be added to the case library

        """
        index_to_insert = self.cocktails.index(self.library_by_category[new_case.find("category").text][-1])
        self.cocktails.insert(index_to_insert+1, new_case)
        et = etree.ElementTree(self.cocktails)
        et.write(self.cbl_filename, pretty_print=True, encoding="UTF-8")

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

                # Ingredient constraint has highest importance
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

                        # Increase similarity if constraint ingredient is used in cocktail
                        if ingredient in c_ingredients:
                            sim += 1 * self.similarity_weights["ingr_match"]

                        # Increase similarity if constraint ingredient alc_type is used in cocktail
                        elif itype == "alcohol" and ingredient_alc_type in c_ingredients_atype:
                            sim += 1 * self.similarity_weights["ingr_alc_type_match"]

                        # Incrase similarity if constraint ingredient basic_taste is used in cocktail
                        elif itype == "non-alcohol" and ingredient_basic_taste in c_ingredients_btype:
                            sim += 1 * self.similarity_weights["ingr_basic_taste_match"]

                # Increase similarity if alc_type is a match. Alc_type has a lot of importance,
                # but less than the ingredient constraints
                elif key == "alc_type":
                    for atype in constraints[key]:
                        sim += sum([1 * self.similarity_weights["alc_type_match"]
                                    for i in cocktail.find("ingredients") if atype == i.attrib['alc_type']])

                # Increase similarity if basic_taste is a match. Basic_taste has a lot of importance,
                # but less than the ingredient constraints
                elif key == "basic_taste":
                    for btype in constraints[key]:
                        sim += sum([1 * self.similarity_weights["basic_taste_match"]
                                    for i in cocktail.find("ingredients") if btype == i.attrib['basic_taste']])

                # Increase similarity if glasstype is a match. Glasstype is not very relevant for the case
                elif key == "glasstype":
                    for glass in constraints[key]:
                        if glass == cocktail.find(key).text:
                            sim += 1 * self.similarity_weights["glasstype_match"]

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
                            exc_ingredient_basic_taste = \
                                [k for k in self.basic_dict if ingredient in self.basic_dict[k]][0]

                        # Decrease similarity if ingredient excluded is found in cocktail
                        if ingredient in c_ingredients:
                            sim += 1 * self.similarity_weights["exc_ingr_match"]

                        # Decrease similarity if excluded ingredient alc_type is used in cocktail
                        elif itype == "alcohol" and exc_ingredient_alc_type in c_ingredients_atype:
                            sim += 1 * self.similarity_weights["exc_ingr_alc_type_match"]

                        # Decrease similarity if excluded ingredient basic_taste is used in cocktail
                        elif itype == "non-alcohol" and exc_ingredient_basic_taste in c_ingredients_btype:
                            sim += 1 * self.similarity_weights["exc_ingr_basic_taste_match"]

                # If one of the excluded alcohol_types is found in the cocktail, similarity is reduced
                elif key == "exc_alc_type":
                    for atype in constraints[key]:
                        sim += sum([1 * self.similarity_weights["exc_alc_type"]
                                    for i in cocktail.find("ingredients") if atype == i.attrib['alc_type']])

                # If one of the excluded basic_tastes is found in the cocktail, similarity is reduced
                elif key == "exc_basic_taste":
                    for atype in constraints[key]:
                        sim += sum([1 * self.similarity_weights["exc_basic_taste"]
                                    for i in cocktail.find("ingredients") if atype == i.attrib['basic_taste']])

        return (sim * float(cocktail.find("utility").text))

    def _retrieval(self, constraints):
        """ Retrieve most appropriate cocktail given the provided constraints.
        
        It does a structured search by first filtering by the category.
        Then, the architecture is like a flat memory.

        Args:
            constraints (ditc): dictionary of constraints

        Returns:
            retrieved_case (Element): retrieved cocktail Element
        """
        # SEARCHING PHASE
        # Filter elements that correspond to the category constraint
        # If category constraints is not empty
        if constraints['category']:
            searching_list = list(itertools.chain.from_iterable([self.library_by_category[cat]
                                                                 for cat in constraints['category']]))
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
        self.verboseprint(f"[CBR] Retrieved case: {retrieved_case.find('name').text}")
        
        return retrieved_case

    def _create_ingr_element(self, ingredient, cocktail, ingr_id):
        """ Convert an Ingredient Named Tuple to an ingredient XML element

        Args:
            ingredient (namedtuple): ingredient namedtuple
        """
        ingr_element = etree.SubElement(cocktail.find("ingredients"), "ingredient",
                                        id=ingr_id, alc_type=ingredient.alc_type,
                                        basic_taste=ingredient.basic_taste,
                                        measure=ingredient.measure,
                                        quantity=ingredient.quantity,
                                        unit=ingredient.unit)
        ingr_element.text = ingredient.name

        return ingr_element

    def add_ingredient_by_type(self, cocktail, constraints, idx_ingr, ingr_type, type):
        if type == "alc_type":
            possible_ingr = [ingredient_to_add for ingredient_to_add in self.ingredients_list if
                             ingredient_to_add.alc_type == ingr_type and
                             ingredient_to_add.text not in constraints["ingredients"]]
        elif type == "basic_taste":
            possible_ingr = [ingredient_to_add for ingredient_to_add in self.ingredients_list if
                             ingredient_to_add.basic_taste == ingr_type and
                             ingredient_to_add.text not in constraints["ingredients"]]

        # Choose a random ingredient with this ingredient_type from the database, excluding the non-desired ones
        ingredient_to_add = random.choice(possible_ingr)
        
        # Add it to the recipe with a new index
        to_add = self._create_ingr_element(ingredient_to_add, cocktail, "ingr" + str(idx_ingr))
        cocktail.find("ingredients").append(to_add)
        
        # New step to the recipe in which we include the added ingredient to the cocktail
        step = etree.SubElement(cocktail.find("preparation"), "step")
        step.text = "Add ingr" + str(idx_ingr) + " to the cocktail."
        cocktail.find("preparation").append(step)

    def remove_ingredient(self, cocktail, ingredient):
        cocktail.find("ingredients").remove(ingredient)

        # Adapt the step that contains the excluded ingredient
        for step in cocktail.find("preparation"):
            # If there is any other ingredient in the step, remove only the excluded one
            if ingredient.get('id') in step.text and \
                    any([ingr in step for ingr in cocktail.find("ingredients")]):
                
                # Remove ingredient id in step
                ingr_pattern = r"\b({})\b".format(ingredient.get('id'))
                step = re.sub(ingr_pattern, "", step)
                
            # If the excluded is the only ingredient in the step, remove the whole step from the recipe
            elif ingredient.get('id') in step.text:
                cocktail.find("preparation").remove(step)

    def _adaptation(self, constraints, retrieved_cocktail):
        """ Adapt the ingredients and steps of the preparation for the best retrieved case
        following the constraints fixed by the user

        Args:
            constraints (dict): dictionary of constraints to be fulfilled
            retrieved_cocktail (Element): retrieved cocktail element that needs to be adapted

        Returns:
            adapted_cocktail (Element): Element of the adapted cocktail from the retrieved one
            n_changes (int): number of changes needed to adapt the solution of the case
        """

        adapted_cocktail = deepcopy(retrieved_cocktail)
        n_changes = 0

        # Change the name of the cocktail according to the constraints
        if constraints["name"]:
            adapted_cocktail.find("name").text = constraints["name"]
        else:
            adapted_cocktail.find("name").text += "2.0"

        # Save the derivation parameter for the adapted case
        adapted_cocktail.find("derivation").text = retrieved_cocktail.find("name").text

        # If glass does not fulfill constraint, change it
        if len(constraints["glass_type"]):
            if adapted_cocktail.find("glasstype").text not in constraints["glass_type"]:
                adapted_cocktail.find("glasstype").text = random.choice(constraints["glass_type"])
                n_changes += 1
            
        # REMOVE ingredients that are in the exclude ingredients constraint
        if len(constraints["exc_ingredients"]):
            for ingr in adapted_cocktail.find("ingredients"):
                if ingr.text in constraints["exc_ingredients"]:
                    self.remove_ingredient(cocktail=adapted_cocktail, ingredient=ingr)
                    n_changes += 1

        # REMOVE alcohol types that are in the exclude alcohol types constraint
        if len(constraints["exc_alc_type"]):
            for ingr in adapted_cocktail.find("ingredients"):
                if ingr.get("alc_type") in constraints["exc_alc_type"]:
                    self.remove_ingredient(cocktail=adapted_cocktail, ingredient=ingr)
                    n_changes += 1

        # REMOVE basic tastes that are in the exclude basic tastes constraint
        if len(constraints["exc_basic_taste"]):
            for ingr in adapted_cocktail.find("ingredients"):
                if ingr.get("basic_taste") in constraints["exc_basic_taste"]:
                    self.remove_ingredient(cocktail=adapted_cocktail, ingredient=ingr)
                    n_changes += 1

        # Define an index for the ingredients in order to avoid repetitions in the indexes when adding new ingredients
        idx_ingr = 2*len(adapted_cocktail.find("ingredients"))

        # If a desired alcohol type / basic taste is not in the recipe, ADD an ingredient of this type from the database
        for alcohol in constraints["alc_type"]:
            # If the desired alcohol type it is not in the recipe, add some ingredient from this type
            if alcohol not in [ingr.get("alc_type") for ingr in adapted_cocktail.find("ingredients")]:
                self.add_ingredient_by_type(cocktail=adapted_cocktail, constraints=constraints, idx_ingr=idx_ingr,
                                            ingr_type=alcohol, type="alc_type")
                idx_ingr += 1
                n_changes += 1

        for taste in constraints["basic_taste"]:
            # If the desired basic taste it is not in the recipe, add some ingredient from this type
            if taste not in [ingr.get("basic_taste") for ingr in adapted_cocktail.find("ingredients")]:
                self.add_ingredient_by_type(cocktail=adapted_cocktail, constraints=constraints, idx_ingr=idx_ingr,
                                            ingr_type=taste, type="basic_taste")
                idx_ingr += 1
                n_changes += 1

        # If a desired concrete ingredient is not in the recipe, ADD it or SUBSTITUTE another from the same type
        # Taking into account that the one we substitute is not another "mandatory" ingredient desired by the user
        for ingre in constraints["ingredients"]:
            # If the desired ingredient is already in the cocktail we skip this constraint and check the following one
            if ingre in [ingr.text for ingr in adapted_cocktail.find("ingredients")]:
                continue

            # Otherwise, we try to substitute some ingredient of the same type or add it directly
            else:
                # Choose a random ingredient (with different quantities and indexes) with this name
                possible_ingr = [ingredient_to_add for ingredient_to_add in self.ingredients_list if
                                 ingredient_to_add.name == ingre]
                ingredient_to_add = random.choice(possible_ingr)

                # If we are including a non-alcoholic ingredient
                if ingredient_to_add.alc_type == "":
                    # Store all the non-alcoholic ingredients in the recipe with the same basic_taste than the desired
                    # and that are not one of the desired ingredients
                    without_alcohol = [ingr for ingr in adapted_cocktail.find("ingredients") if
                                       ingr.get("basic_taste") == ingredient_to_add.basic_taste and
                                       ingr.text not in constraints["ingredients"]]

                    if len(without_alcohol) > 0:
                        # If we have any possible ingredients to be substituted, we SUBSTITUTE one by the desired
                        ingr = random.choice(without_alcohol)
                        adapted_cocktail.find("ingredients").remove(ingr)
                        to_add = self._create_ingr_element(ingredient_to_add, adapted_cocktail, ingr.get('id'))
                        adapted_cocktail.find("ingredients").append(to_add)

                        n_changes += 1
                    else:
                        # If there is none ingredient of that basic taste we directly ADD the desired one
                        to_add = self._create_ingr_element(ingredient_to_add, adapted_cocktail, "ingr" + str(idx_ingr))
                        # TODO: check the following line is not neccessary, auto-overwrite
                        # adapted_cocktail.find("ingredients").append(to_add)
                        # ADD also a step concerning this ingredient to the recipe
                        step = etree.SubElement(adapted_cocktail.find("preparation"), "step")
                        step.text = "Add ingr" + str(idx_ingr) + " to the cocktail."
                        # TODO: check the following line is not neccessary, auto-overwrite
                        # adapted_cocktail.find("preparation").append(step)

                        idx_ingr += 1
                        n_changes += 1

                # If we are including an alcoholic ingredient
                else:
                    # Store all the alcoholic ingredients in the recipe with the same alcohol type than the desired
                    # and that are not one of the desired ingredients
                    with_alcohol = [ingr for ingr in adapted_cocktail.find("ingredients") if
                                    ingr.get('alc_type') == ingredient_to_add.alc_type and
                                    ingr.text not in constraints["ingredients"]]

                    if len(with_alcohol) > 0:
                        # If we have any possible ingredients to be substituted, we SUBSTITUTE one by the desired
                        ingr = random.choice(with_alcohol)
                        adapted_cocktail.find("ingredients").remove(ingr)
                        to_add = self._create_ingr_element(ingredient_to_add, adapted_cocktail, ingr.get('id'))
                        adapted_cocktail.find("ingredients").append(to_add)
                        n_changes += 1
                    else:
                        # If there is none ingredient of that alcohol type we directly ADD the desired one
                        to_add = self._create_ingr_element(ingredient_to_add, adapted_cocktail, "ingr" + str(idx_ingr))
                        adapted_cocktail.find("ingredients").append(to_add)

                        # ADD also a step concerning this ingredient to the recipe
                        step = etree.SubElement(adapted_cocktail.find("preparation"), "step")
                        step.text = "Add ingr" + str(idx_ingr) + " to the cocktail."
                        adapted_cocktail.find("preparation").append(step)

                        idx_ingr += 1
                        n_changes += 1
                
        return adapted_cocktail, n_changes
      
    def _evaluation(self, adapted_cocktail):
        """ Evaluate the ingredients and steps of the preparation by the user in order to determine if the
         adapted case is a success or a failure

        Args:
            adapted_cocktail (Element): adapted cocktail element that needs to be evaluated

        Returns:
            adapted_cocktail (Element): adapted cocktail with
            score (float64): value of the score assigned by the expert user
        """
        print("The cocktail to evaluate contains the following ingredients:")
        self._print_ingredients(adapted_cocktail)
        print("The preparation steps of the cocktail is the following one:")
        self._print_preparation(adapted_cocktail)
        print("How good was the cocktail?")
        print("Please, introduce a score between 0 and 10 (You can use decimals)")
        score=float(input())
        if score >= self.threshold_eval:
            adapted_cocktail.find('evaluation').text = "Success"
        else:
            adapted_cocktail.find('evaluation').text = "Failure"
        return adapted_cocktail, score

    def check_constraints(self, constraints):
        """ Check that constraints contain valid values.

        Args:
            constraints (dictionary): constraints to fulfill
        """
        errors = []
        
        # Check name
        if constraints['name'] in self.cocktail_names:
            errors.append('Name already in use')
        
        # Check categories
        if not all([i in self.categories for i in constraints['category']]):
            errors.append('Some invalid categories')
        
        # Check glass type:
        if not all([i in self.glass_types for i in constraints['glass_type']]):
            errors.append('Some invalid glass types')
            
        # Check ingredients:
        if not all([i in self.ingredient_names for i in constraints['ingredients']]):
            errors.append('Some invalid ingredients')
        
        # Check basic tastes:
        if not all([i in self.basic_tastes for i in constraints['basic_taste']]):
            errors.append('Some invalid basic tastes')
        
        # Check alcohol types:
        if not all([i in self.alcohol_types for i in constraints['alc_type']]):
            errors.append('Some invalid alcohol types')
            
        # Check exc ingredients:
        if not all([i in self.ingredient_names for i in constraints['exc_ingredients']]):
            errors.append('Some invalid exc ingredients')
        
        # Check exc alcohol types:
        if not all([i in self.alcohol_types for i in constraints['exc_alc_type']]):
            errors.append('Some invalid exc alcohol types')
            
        # Check exc basic tastes:
        if not all([i in self.basic_tastes for i in constraints['exc_basic_taste']]):
            errors.append('Some invalid exc basic tastes')

        return errors