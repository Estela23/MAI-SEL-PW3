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
        
        # Get cocktails ingredients and alc_type
        c_ingredients = [i.text for i in cocktail.findall('ingredients/ingredient')]
        c_ingredients_type = [i.attrib['alc_type'] for i in cocktail.findall('ingredients/ingredient')]
                        
        # Evaluate each constraint one by one
        for key in constraints:
            if constraints[key]:
                # Ingredient constraing has highest importance
                if key == "ingredients":
                    for ingredient in constraints[key]:
                        # Get ingredient alcohol type
                        ingredient_alc_type = [k for k in self.alcohol_dict if ingredient in self.alcohol_dict[k]][0]
                        
                        # Add 1 if constraint ingredient is used in cocktail
                        if ingredient in c_ingredients:
                            sim += 1
                            
                        # Add 0.5 if constraint ingredient alc_type is used in cocktail
                        elif ingredient_alc_type in c_ingredients_type:
                            sim += 0.5
                                
                # Alochol type is the second most important
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

    def adaptation_step(self, constraints, retrieved_case):
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
        retrieved_cocktail = cocktails[0]
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