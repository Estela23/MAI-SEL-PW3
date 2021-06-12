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

# Declare Ingredient namedtuple() 
Ingredient = namedtuple('Ingredient', ['name', 'identifier', 'alc_type', 'basic_taste', 'measure', 'quantity', 'unit'])


class CBR:
    def __init__(self, cbl_filename):
        tree = etree.parse(cbl_filename)
        self.cocktails = tree.getroot()
        self.alcohol_types = set()
        self.basic_tastes = set()
        self.ingredients_list = []

        self._init_structure()

    def _init_structure(self):
        """ Initialize library structure
        
        Parse cocktails tree and extract relevant information such as 
        the unique categories, alcohol types, ingredients, etc.
        """

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
            if not any(i in ckt_ingredients for i in cnst_ingredients):
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
                
        # Chekc alc_type
        if cnst_alc_types:
            if all(i in ckt_alc_types for i in cnst_alc_types):
                evaluation.append(True)
            else:
                evaluation.append(False)
                evaluation_results.append('Alcohol types constraint failed')
        
        # Chekc basic_taste
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
        retrieved_case = self.retrieval(constraints)
        # ADAPTATION PHASE
        adapted_case = self.adaptation(retrieved_case)
        # EVALUATION PHASE
        # LEARNING PHASE
        # TODO: Add the rest of the phases in the future

        return adapted_case, self.cocktails

    def _update_case_library(self, new_case):
        """ Update the case_library with the succesful adapted case

        Args:
            new_case: adapted and evaluated succesful case

        Returns:

        """
        # TODO: What happens with the failures, are they saved in the case library as well?
        # TODO: update utility function and case label
        self.cocktails.append(new_case)
        et = etree.ElementTree(self.cocktails)
        et.write('Data/case_library.xml', pretty_print=True, encoding="UTF-8")
        return

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
        # If there are more than two category constraints
        if len(constraints['category']):
            searching_list = list(itertools.chain.from_iterable([[child for child in self.cocktails
                                if child.find('category').text == category] for category in constraints['category']]))
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

    def _create_ingr_element(ingredient, cocktail, ingr_id):
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
        
    def adaptation_step(self, constraints, retrieved_cocktail):
        """ Adapt a retrieved cocktail to fullfill the given constraints

        Args:
            constraints (dict): constraints to be fullfilled
            retrieved_cocktail (Element): cocktail element that needs to be adapted

        Returns:
            Element: adapted cocktail element
        """
        # Adapt the ingredients:
        # Add ingredients
        # TODO: hacer esto al revés para tener las cantidades, meter primero los de la receta
        #  y luego los que añadimos metiendo las cantidades al chou (?)
        ingredients = constraints["ingredients"]  # TODO: quantity? index?
        alc_type = constraints["alc_type"]
        ingredients_remove = constraints["exc_ingredients"]
        ingredients_cocktail = {}
        
        # If glass does not fullfill constraint, change it
        if len(constraints["glass_type"]):
            if retrieved_cocktail.find("glasstype").text not in constraints["glass_type"]:
                retrieved_cocktail.find("glasstype").text = random.choice(constraints["glass_type"])
            
        # TODO: Revisar esta fase, es el remove.
        for ingr in retrieved_cocktail.find("ingredients"):
            if ingr.text in constraints["exc_ingredients"]:
                retrieved_cocktail.find("ingredients").remove(ingr)
                # TODO: Check si es la mejor forma de remover de las steps
                for step in retrieved_cocktail.find("preparation"):
                    if ingr.get('id') in step.text:
                        retrieved_cocktail.find("preparation").remove(step)
                        
        # TODO: Revisar, add y substitution step, puede contener errores, prefiero segundo vistazo
        idx_ingr = 2*len(retrieved_cocktail.find("ingredients"))
        for alcohol in alc_type:
            flag_to_add = True
            for ingr in retrieved_cocktail.find("ingredients"):
                # Si un alcohol type no esta, se añade a la preparation
                if ingr.get('alc_type') == alcohol:
                    flag_to_add = False
            # Paso de añadir alcohol type
            if flag_to_add:
                possible_ingr = [ingredient_to_add for ingredient_to_add in self.ingredients_list if
                                 ingredient_to_add.alc_type == alcohol]
                ingredient_to_add = random.choice(possible_ingr)
                to_add = self._create_ingr_element(ingredient_to_add, retrieved_cocktail, "ingr" + str(idx_ingr))                
                retrieved_cocktail.find("ingredients").append(to_add)
                step = etree.SubElement(retrieved_cocktail.find("preparation"), "step")
                # Si añades el alcohol type, posiblemente se necesite un paso de preparacion que lo contenga, esta es una idea, luego veremos que tal pirula.
                step.text = "Add ingr" + str(idx_ingr) + " to the cocktail."
                idx_ingr = idx_ingr + 1
                retrieved_cocktail.find("preparation").append(step)
                break
            
        # Segun mi logica, primer se añade el alcohol type, una vez añadido si una bebida de ese alcohol type si en las constratins se especifico una bebida tb de ese alcohol type, se sustituye
        # Tabmién si en la receta hay un ron y nos pide concretamente Havana Club, se sustituye el ron por Havana Club.
        for ingre in ingredients:
            # Recupero posibles ingredientes
            possible_ingr = [ingredient_to_add for ingredient_to_add in self.ingredients_list if
                             ingredient_to_add.name == ingre]
            flag_to_add = True
            # Si hay posible ingrediente
            if len(possible_ingr) > 0:
                # Se selecciona aleatorio, para no escoger siemrpe el mismo
                ingredient_to_add = random.choice(possible_ingr)
                if ingredient_to_add.alc_type == "":
                    without_alcohol=[ingr for ingr in retrieved_cocktail.find("ingredients") if
                     ingr.get('alc_type') == ingredient_to_add.alc_type and ingr.get("alc_type") == "" and ingr.get(
                         "basic_taste") == ingredient_to_add.basic_taste and ingredient_to_add.name != ingr.text]
                    if len([ingr for ingr in retrieved_cocktail.find("ingredients") if
                            ingr.get('alc_type') == ingredient_to_add.alc_type and ingr.get("alc_type") == "" and ingr.get(
                                "basic_taste") == ingredient_to_add.basic_taste and ingr.text == ingredient_to_add.name]) > 0:
                        flag_to_add=False
                    elif len(without_alcohol)>0:
                        ingr = random.choice(without_alcohol)
                        retrieved_cocktail.find("ingredients").remove(ingr)
                        to_add = self._create_ingr_element(ingredient_to_add, retrieved_cocktail, ingr.get('id'))
                        retrieved_cocktail.find("ingredients").append(to_add)
                        flag_to_add = False
                else:
                    with_alcohol = [ingr for ingr in retrieved_cocktail.find("ingredients") if
                                       ingr.get('alc_type') == ingredient_to_add.alc_type and ingr.get("alc_type") != "" and ingr.text!= ingredient_to_add.name]
                    if len([ingr for ingr in retrieved_cocktail.find("ingredients") if
                            ingr.get('alc_type') == ingredient_to_add.alc_type and ingr.get("alc_type") != "" and ingr.text == ingredient_to_add.name]) > 0:
                        flag_to_add=False
                    elif len(with_alcohol)>0:
                        ingr = random.choice(with_alcohol)
                        retrieved_cocktail.find("ingredients").remove(ingr)
                        to_add = self._create_ingr_element(ingredient_to_add, retrieved_cocktail, ingr.get('id'))
                        to_add.text = ingredient_to_add.name
                        retrieved_cocktail.find("ingredients").append(to_add)
                        flag_to_add = False
                        
                '''for ingr in retrieved_cocktail.find("ingredients"):
                    if ingr.get('alc_type') == ingredient_to_add.alc_type and ingredient_to_add.alc_type == "":
                        # EN CASO DE BEEBIDA NO ALGOHOLICA SUSTITUYO POR BASIC TASTE
                        if ingr.get("basic_taste") == ingredient_to_add.basic_taste and ingr.text != ingredient_to_add.name:
                            retrieved_cocktail.find("ingredients").remove(ingr)
                            to_add = self._create_ingr_element(ingredient_to_add, retrieved_cocktail, ingr.get('id'))
                            retrieved_cocktail.find("ingredients").append(to_add)
                            flag_to_add = False
                            break
                        elif ingr.get("basic_taste") == ingredient_to_add.basic_taste and ingr.text == ingredient_to_add.name:
                            flag_to_add = False
                            break
                    # Si es mismo alcohol Y DIFERENTE NOMBRE SE CAMBIA
                    elif ingr.get('alc_type') == ingredient_to_add.alc_type and ingredient_to_add.alc_type != "":
                        if ingr.get('alc_type') == ingredient_to_add.alc_type and ingr.text != ingredient_to_add.name:
                            retrieved_cocktail.find("ingredients").remove(ingr)
                            to_add = self._create_ingr_element(ingredient_to_add, retrieved_cocktail, ingr.get('id'))
                            retrieved_cocktail.find("ingredients").append(to_add)
                            flag_to_add = False
                            break
                        elif ingr.get('alc_type') == ingredient_to_add.alc_type and ingr.text == ingredient_to_add.name:
                            flag_to_add = False
                            break
                #Si no había sustitución posible se añade'''
            if flag_to_add:
                to_add = self._create_ingr_element(ingredient_to_add, retrieved_cocktail, "ingr" + str(idx_ingr))
                retrieved_cocktail.find("ingredients").append(to_add)
                step = etree.SubElement(retrieved_cocktail.find("preparation"), "step")
                # Posiblemente se necesite añadir una step luego de añadir el nuevo elemento, revisar codigo de todas formas, y hay que pensar forma de añadirlo logicamente.
                step.text = "Add ingr" + str(idx_ingr) + " to the cocktail."
                idx_ingr = idx_ingr + 1
                retrieved_cocktail.find("preparation").append(step)
        return retrieved_cocktail

    def adaptation(self):
        return

'''
# To test RETRIEVAL step
constraints = {'category': ['Cocktail', 'Shot'], 'glasstype': ['Beer glass', 'Shot glass'], 'ingredients': ['Amaretto'],
                'alc_type': ['Rum'], 'basic_type': ['Sweet'], 'exc_ingredients': ['Vodka']}

cbr = CBR("Data/case_library.xml")
case_retrieved = cbr.retrieval(constraints)
'''

