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
        self.ingredients_list = []
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

        # Get unique values for alcohol types
        self.alcohol_types.update(
            [i.attrib['alc_type'] for i in self.cocktails.findall('cocktail/ingredients/ingredient')])
        self.alcohol_types.remove('')  # remove empty type

        # Get unique values for basic taste
        self.basic_tastes.update(
            [i.attrib['basic_taste'] for i in self.cocktails.findall('cocktail/ingredients/ingredient')])
        self.basic_tastes.remove('')  # remove empty type

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

        # Define historial for all cases in case library, containing number of successes and failures
        self.cases_historial = {}
        [self.cases_historial.update({c.find("name").text:[0,0]}) for c in self.cocktails]

        self.categories = set([c.find("category").text for c in self.cocktails])
        self.library_by_category = {}
        [self.library_by_category.update({cat: [c for c in self.cocktails
                                                if c.find('category').text == cat]}) for cat in self.categories]
        

    def _print_ingredients(self, cocktail):
        """ Print the ingredients (with measures) of the given cocktail.

        Args:
            cocktail (Element): cocktail Element
        """
        for i in cocktail.findall('ingredients/ingredient'):
            print(f'{i.get("measure")} {i.text}')
            # print(f'{i.measure} {i.name} ({i.quantity} {i.unit})')

    def _print_preparation(self, cocktail):
        """ Print the preparation steps (with ingredient names) of the given cocktail.

        Args:
            cocktail (Element): cocktail Element
        """
        for s in cocktail.findall('preparation/step'):
            step = s.text
            for i in cocktail.findall('ingredients/ingredient'):
                step = step.replace(i.get('id'), i.text)
            print(step)

    def _evaluate_constraints_fullfillment(self, constraints, cocktail):
        """ Check that a cocktail fullfills all the requiered constraints.

        Args:
            constraings (dict): constraints to fulfill
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

        evaluation = []
        evaluation_results = []

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

        # Check alc_type
        if cnst_alc_types:
            if all(i in ckt_alc_types for i in cnst_alc_types):
                evaluation.append(True)
            else:
                evaluation.append(False)
                evaluation_results.append('Alcohol types constraint failed')

        # Check basic_taste
        if cnst_basic_tastes:
            if all(i in ckt_basic_tastes for i in cnst_basic_tastes):
                evaluation.append(True)
            else:
                evaluation.append(False)
                evaluation_results.append('Basic tastes constraint failed')

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
        adapted_case = self._adaptation(retrieved_case)
        # EVALUATION PHASE
        # LEARNING PHASE
        self._learning(retrieved_case, adapted_case)
        # TODO: Add the rest of the phases in the future

        return adapted_case, self.cocktails

    def _learning(self, retrieved_case, adapted_case):
        """ Learning phase in order to decide if the evaluated case is a success or a failure, and act consequently

        Args:
            retrieved_case (Element): case resulting from retrieval phase
            adapted_case (Element): case resulting from adaptation phase, which has been evaluated

        Returns:

        """
        # MANAGING UTILITY SCORE OF THE RETRIEVED CASE
        # Update the cases_historial of the retrieved case based on the status
        # If the adapted case is a success, according to the human oracle
        if adapted_case.find('evaluation').text == "Success":
            self.cases_historial[retrieved_case.find("name").text][0] += 1
        # If the adapted case is a failure, according to the human oracle
        elif adapted_case.find('evaluation').text == "Failure":
            self.cases_historial[retrieved_case.find("name").text][1] += 1

        # Compute utility score for retrieved_case
        utility_score = (self.cases_historial[retrieved_case.find("name").text][0] - \
                        self.cases_historial[retrieved_case.find("name").text][1] + 1) / 2

        # If utility score is 0.0, remove retrieved_case from case library, from cases_historial and from library_by_category
        if utility_score == 0.0:
            self.cocktails.remove(retrieved_case)
            rem = self.cases_historial.pop([retrieved_case.find("name").text], None)
            if rem == None:
                print("ERROR: You are trying to delete a cocktail that doesn't exist in the cases_historial structure")
            self.library_by_category[retrieved_case.find("category").text] = self.library_by_category[retrieved_case.find("category").text].remove(retrieved_case)
        # Otherwise, update retrieved case utility score if the computed utility score has changed
        elif str(utility_score) != retrieved_case.find("utility").text:
            for c in self.cocktails:
                if c.find("name").text == retrieved_case.find("name").text:
                    c.find("utility").text = str(utility_score)

        # Initialize utility of adapted_case to 1.0 always
        adapted_case.find("utility").text = str(1.0)

        # Update case_historial with the adapted case:
        self.cases_historial.update({adapted_case.find('name').text: [0, 0]})
        # Update library_by_category
        self.library_by_category[adapted_case.find("category").text] = self.library_by_category[adapted_case.find("category").text].append(adapted_case)
        # Add new adapted_case to case library
        self._update_case_library(adapted_case)
        # TODO: Decide what to do with failures
        '''
        # FOR WHEN DECIDING WHAT TO DO WITH FAILURES
        if adapted_case.find('evaluation').text == "Success":
            # Update case_historial with the adapted case:
            self.cases_historial.update({adapted_case.find('name').text: [0,0]})
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
        # TODO: Introduce the new succesful case in the neighbourhood when 9-division case library is built
        self.cocktails.append(new_case)
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
                    for glass in constraints[key]:
                        if glass == cocktail.find(key).text:
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
                            exc_ingredient_basic_taste = \
                                [k for k in self.basic_dict if ingredient in self.basic_dict[k]][0]

                        # Decrease similarity by -2 if ingredient excluded is found in cocktail
                        if ingredient in c_ingredients:
                            sim -= 2

                        # Decrease similarity by -1 if if excluded ingredient alc_type is used in cocktail
                        elif itype == "alcohol" and exc_ingredient_alc_type in c_ingredients_atype:
                            sim -= 1

                        # Decrease similarity by -1 if if excluded ingredient basic_taste is used in cocktail
                        elif itype == "non-alcohol" and exc_ingredient_basic_taste in c_ingredients_btype:
                            sim -= 1
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

    def add_ingredient_by_type(self, cocktail, idx_ingr, ingr_type, type):
        if type == "alc_type":
            possible_ingr = [ingredient_to_add for ingredient_to_add in self.ingredients_list if
                             ingredient_to_add.alc_type == ingr_type]
        elif type == "basic_taste":
            possible_ingr = [ingredient_to_add for ingredient_to_add in self.ingredients_list if
                             ingredient_to_add.basic_taste == ingr_type]

        # Choose a random ingredient with this ingredient_type from the database
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
                step.text.replace(ingredient.get('id'), "")
            # If the excluded is the only ingredient in the step, remove the whole step from the recipe
            elif ingredient.get('id') in step.text:
                cocktail.find("preparation").remove(step)

    def _adaptation(self, constraints, retrieved_cocktail):
        """ Adapt the ingredients and steps of the preparation for the best retrieved case
        following the constraints fixed by the user

        Args:
            constraints (dict): dictionary of constraints to be fullfilled
            retrieved_cocktail (Element): retrieved cocktail element that needs to be adapted

        Returns:
            adapted_cocktail (Element): Element of the adapted cocktail from the retrieved one
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

        # Define an index for the ingredients in order to avoid repetitions in the indexes when adding new ingredients
        idx_ingr = 2*len(adapted_cocktail.find("ingredients"))

        # If a desired alcohol type / basic taste is not in the recipe, ADD an ingredient of this type from the database
        for alcohol in constraints["alc_type"]:
            # If the desired alcohol type it is not in the recipe, add some ingredient from this type
            if alcohol not in [ingr.get("alc_type") for ingr in adapted_cocktail.find("ingredients")]:
                self.add_ingredient_by_type(cocktail=adapted_cocktail, idx_ingr=idx_ingr, ingr_type=alcohol,
                                            type="alc_type")
                idx_ingr += 1
                n_changes += 1

        for taste in constraints["basic_taste"]:
            # If the desired basic taste it is not in the recipe, add some ingredient from this type
            if taste not in [ingr.get("basic_taste") for ingr in adapted_cocktail.find("ingredients")]:
                self.add_ingredient_by_type(cocktail=adapted_cocktail, idx_ingr=idx_ingr, ingr_type=taste,
                                            type="basic_taste")
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
                        adapted_cocktail.find("ingredients").append(to_add)
                        # ADD also a step concerning this ingredient to the recipe
                        step = etree.SubElement(adapted_cocktail.find("preparation"), "step")
                        step.text = "Add ingr" + str(idx_ingr) + " to the cocktail."
                        adapted_cocktail.find("preparation").append(step)

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


                #### TODO: a partir de aquí no entiendo para qué sirve, creo que son cosas que ya se hacen antes, no?
                for ingr in adapted_cocktail.find("ingredients"):
                    if ingr.get('alc_type') == ingredient_to_add.alc_type and ingredient_to_add.alc_type == "":
                        # EN CASO DE BEBIDA NO ALGOHOLICA SUSTITUYO POR BASIC TASTE
                        if ingr.get("basic_taste") == ingredient_to_add.basic_taste and ingr.text != ingredient_to_add.name:
                            adapted_cocktail.find("ingredients").remove(ingr)
                            to_add = self._create_ingr_element(ingredient_to_add, adapted_cocktail, ingr.get('id'))
                            adapted_cocktail.find("ingredients").append(to_add)
                            flag_to_add = False
                            break
                        elif ingr.get("basic_taste") == ingredient_to_add.basic_taste and ingr.text == ingredient_to_add.name:
                            flag_to_add = False
                            break
                    # Si es mismo alcohol Y DIFERENTE NOMBRE SE CAMBIA
                    elif ingr.get('alc_type') == ingredient_to_add.alc_type and ingredient_to_add.alc_type != "":
                        if ingr.get('alc_type') == ingredient_to_add.alc_type and ingr.text != ingredient_to_add.name:
                            adapted_cocktail.find("ingredients").remove(ingr)
                            to_add = self._create_ingr_element(ingredient_to_add, adapted_cocktail, ingr.get('id'))
                            adapted_cocktail.find("ingredients").append(to_add)
                            flag_to_add = False
                            break
                        elif ingr.get('alc_type') == ingredient_to_add.alc_type and ingr.text == ingredient_to_add.name:
                            flag_to_add = False
                            break
                
        return adapted_cocktail
      
    def evaluation(self, adapted_cocktail):
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

'''
# To test RETRIEVAL step
constraints = {'category': ['Cocktail', 'Shot'], 'glasstype': ['Beer glass', 'Shot glass'], 'ingredients': ['Amaretto'],
                'alc_type': ['Rum'], 'basic_type': ['Sweet'], 'exc_ingredients': ['Vodka']}




    '''
''''# To test RETRIEVAL step
constraints = {'category': ['Cocktail', 'Shot'], 'glasstype': ['Beer glass', 'Shot glass'], 'ingredients': ['Amaretto'],
                'alc_type': ['Rum'], 'basic_type': ['Sweet'], 'exc_ingredients': ['Vodka']}

cbr = CBR("Data/case_library.xml")
case_retrieved = cbr.retrieval(constraints)
'''

