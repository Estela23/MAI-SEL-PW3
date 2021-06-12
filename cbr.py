"""

PW3 - SEL - 2021
CBR for a cocktail recipe creator

Authors:    Xavier Cucurull Salamero <xavier.cucurull@estudiantat.upc.edu>
            Daniel Hinjos García <daniel.hinjos@estudiantat.upc.edu>
            Fernando Vázquez Novoa <fernando.vazquez.novoa@estudiantat.upc.edu>
            Estela Vázquez-Monjardín Lorenzo <estela.vazquez-monjardin@estudiantat.upc.edu>
"""
import random

from lxml import etree
import numpy as np
import random
import itertools
from caseBase import Ingredient


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

    def adaptation_step(self, constraints, retrieved_cocktail):
        '''Falta el retrieved_cocktail como entrada, se le pondrá luego'''
        #El retrieved_cocktail por ahora se finje
        tree = etree.parse('Data/case_library.xml')
        cocktails = tree.getroot()
        # Cargo todos los ingredientes
        ingredients_list = []
        for c in cocktails:
            ingredients = c.find('ingredients')
            for i in ingredients:
                ing = Ingredient(i.text, i.get('id'), i.get('alc_type'), i.get('basic_taste'), i.get('measure'),
                                 i.get('quantity'), i.get('unit'))
            ingredients_list.append(ing)

        # Adapt the ingredients:
        # Add ingredients
        # TODO: hacer esto al revés para tener las cantidades, meter primero los de la receta
        #  y luego los que añadimos metiendo las cantidades al chou (?)
        ingredients = constraints["ingredients"]  # TODO: quantity? index?
        alc_type = constraints["alc_type"]
        ingredients_remove = constraints["exc_ingredients"]
        ingredients_cocktail = {}
        # TODO: cambiar el vaso
        if constraints["glass_type"] != "":
            retrieved_cocktail.find("glasstype").text = constraints["glass_type"]
        # TODO: Revisar esta fase, es el remove.
        for ingr in retrieved_cocktail.find("ingredients"):
            if ingr.text in constraints["exc_ingredients"]:
                retrieved_cocktail.find("ingredients").remove(ingr)
                # TODO: Check si es la mejor forma de remover de las steps
                for step in retrieved_cocktail.find("preparation"):
                    if ingr.get('id') in step.text:
                        retrieved_cocktail.find("preparation").remove(step)
        # TODO: Revisar, add y substitution step, puede contener errores, prefiero segundo vistazo
        for alcohol in alc_type:
            flag_to_add = True
            for ingr in retrieved_cocktail.find("ingredients"):
                # Si un alcohol type no esta, se añade a la preparation
                if ingr.get('alc_type') == alcohol:
                    flag_to_add = False
            # Paso de añadir alcohol type
            if flag_to_add:
                possible_ingr=[ingredient_to_add for ingredient_to_add in ingredients_list if ingredient_to_add.alc_type==alcohol]
                ingredient_to_add = random.choice(possible_ingr)
                to_add = etree.SubElement(retrieved_cocktail.find("ingredients"), "ingredient",
                                                  id=ingredient_to_add.identifier, alc_type=ingredient_to_add.alc_type,
                                                  basic_taste=ingredient_to_add.basic_taste,
                                                  measure=ingredient_to_add.measure,
                                                  quantity=ingredient_to_add.quantity, unit=ingredient_to_add.unit)
                to_add.text = ingredient_to_add.name
                retrieved_cocktail.find("ingredients").append(to_add)
                step = etree.SubElement(retrieved_cocktail.find("preparation"), "step")
                # Si añades el alcohol type, posiblemente se necesite un paso de preparacion que lo contenga, esta es una idea, luego veremos que tal pirula.
                step.text = "Add " + str(ingredient_to_add.identifier) + " to the cocktail."
                retrieved_cocktail.find("preparation").append(step)
                break
        # Segun mi logica, primer se añade el alcohol type, una vez añadido si una bebida de ese alcohol type si en las constratins se especifico una bebida tb de ese alcohol type, se sustituye
        # Tabmién si en la receta hay un ron y nos pide concretamente Havana Club, se sustituye el ron por Havana Club.
        for ingre in ingredients:
            #Recupero posibles ingredientes
            possible_ingr = [ingredient_to_add for ingredient_to_add in ingredients_list if ingredient_to_add.name==ingre]
            flag_to_add = True
            #Si hay posible ingrediente
            if len(possible_ingr)>0:
                #Se selecciona aleatorio, para no escoger siemrpe el mismo
                ingredient_to_add = random.choice(possible_ingr)
                for ingr in retrieved_cocktail.find("ingredients"):
                    if ingr.get('alc_type') == ingredient_to_add.alc_type and ingredient_to_add.alc_type == "":
                        # EN CASO DE BEEBIDA NO ALGOHOLICA SUSTITUYO POR BASIC TASTE
                        if ingr.get("basic_taste") == ingredient_to_add.basic_taste:
                            retrieved_cocktail.find("ingredients").remove(ingr)
                            to_add = etree.SubElement(retrieved_cocktail.find("ingredients"), "ingredient",
                                                      id=ingr.get('id'), alc_type=ingredient_to_add.alc_type,
                                                      basic_taste=ingredient_to_add.basic_taste,
                                                      measure=ingredient_to_add.measure,
                                                      quantity=ingredient_to_add.quantity,
                                                      unit=ingredient_to_add.unit)
                            retrieved_cocktail.append(to_add)
                            flag_to_add = False
                    # Si es mismo alcohol Y DIFERENTE NOMBRE SE CAMBIA
                    elif ingr.get('alc_type') == ingredient_to_add.alc_type and ingr.text != ingredient_to_add.name:
                        retrieved_cocktail.find("ingredients").remove(ingr)
                        to_add = etree.SubElement(retrieved_cocktail.find("ingredients"), "ingredient",
                                                  id=ingr.get('id'), alc_type=ingredient_to_add.alc_type,
                                                  basic_taste=ingredient_to_add.basic_taste,
                                                  measure=ingredient_to_add.measure,
                                                  quantity=ingredient_to_add.quantity,
                                                  unit=ingredient_to_add.unit)
                        retrieved_cocktail.append(to_add)
                        flag_to_add = False
                #Si no había sustitución posible se añade
                if flag_to_add:
                    to_add = etree.SubElement(retrieved_cocktail.find("ingredients"), "ingredient",
                                              id=ingredient_to_add.identifier, alc_type=ingredient_to_add.alc_type,
                                              basic_taste=ingredient_to_add.basic_taste,
                                              measure=ingredient_to_add.measure,
                                              quantity=ingredient_to_add.quantity,
                                              unit=ingredient_to_add.unit)
                    to_add.text=ingredient_to_add.name
                    retrieved_cocktail.find("ingredients").append(to_add)
                    step = etree.SubElement(retrieved_cocktail.find("preparation"), "step")
                    # Posiblemente se necesite añadir una step luego de añadir el nuevo elemento, revisar codigo de todas formas, y hay que pensar forma de añadirlo logicamente.
                    step.text = "Add " + str(ingredient_to_add.identifier) + " to the cocktail."
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

