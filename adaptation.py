from lxml import etree

from caseBase import load_library, Ingredient


def adaptation_step(constraints):
    '''Falta el retrieved_cocktail como entrada, se le pondrá luego'''
    tree = etree.parse('Data/case_library.xml')
    cocktails = tree.getroot()
    #Cargo todos los ingredientes
    ingredients_list=[]
    for c in cocktails:
        ingredients = c.find('ingredients')
        for i in ingredients:
            ing = Ingredient(i.text, i.get('id'), i.get('alc_type'), i.get('basic_taste'), i.get('measure'),
                             i.get('quantity'), i.get('unit'))
        ingredients_list.append(ing)
    retrieved_cocktail = cocktails[0]
    solution = {"name": constraints["name"] if "name" in constraints else retrieved_cocktail.find("name").text + "2.0",
                "category": constraints["category"] if "category" in constraints else retrieved_cocktail.find("category").text,
                "glasstype": constraints["glasstype"] if "glasstype" in constraints else retrieved_cocktail.find("glasstype").text}
    # Adapt the ingredients:
    # Add ingredients
    # TODO: hacer esto al revés para tener las cantidades, meter primero los de la receta
    #  y luego los que añadimos metiendo las cantidades al chou (?)
    ingredients = constraints["ingredients"]    # TODO: quantity? index?
    alc_type = constraints["alc_type"]
    ingredients_remove = constraints["exc_ingredients"]
    ingredients_cocktail={}
    #TODO: cambiar el vaso
    if constraints["glass_type"] != "":
        retrieved_cocktail.find("glasstype").text=constraints["glass_type"]
    #TODO: Revisar esta fase, es el remove.
    for ingr in retrieved_cocktail.find("ingredients"):
        if ingr.text in constraints["exc_ingredients"]:
            retrieved_cocktail.find("ingredients").remove(ingr)
            #TODO: Check si es la mejor forma de remover de las steps
            for step in retrieved_cocktail.find("preparation"):
                if ingr.get('id') in step.text:
                    retrieved_cocktail.find("preparation").remove(step)
    #TODO: Revisar, add y substitution step, puede contener errores, prefiero segundo vistazo
    for alcohol in alc_type:
        flag_to_add=True
        for ingr in retrieved_cocktail.find("ingredients"):
            #Si un alcohol type no esta, se añade a la preparation
            if ingr.get('alc_type') == alcohol:
                flag_to_add=False
        #Paso de añadir alcohol type
        if flag_to_add:
            for ingredient_to_add in ingredients_list:
                if ingredient_to_add.alc_type==alcohol:
                    to_add = etree.SubElement(retrieved_cocktail.find("ingredients"), "ingredient", id=ingredient_to_add.identifier, alc_type= ingredient_to_add.alc_type, basic_taste = ingredient_to_add.basic_taste, measure = ingredient_to_add.measure, quantity = ingredient_to_add.quantity, unit = ingredient_to_add.unit)
                    to_add.text=ingredient_to_add.name
                    retrieved_cocktail.find("ingredients").append(to_add)
                    step = etree.SubElement(retrieved_cocktail.find("preparation"), "step")
                    #Si añades el alcohol type, posiblemente se necesite un paso de preparacion que lo contenga, esta es una idea, luego veremos que tal pirula.
                    step.text = "Add "+ str(ingredient_to_add.identifier) + " to the cocktail."
                    retrieved_cocktail.find("preparation").append(step)
                    break
    #Segun mi logica, primer se añade el alcohol type, una vez añadido si una bebida de ese alcohol type si en las constratins se especifico una bebida tb de ese alcohol type, se sustituye
    #Tabmién si en la receta hay un ron y nos pide concretamente Havana Club, se sustituye el ron por Havana Club.
    for ingre in ingredients:
        for idx, ingredient_to_add in enumerate(ingredients_list):
            if ingredient_to_add.name == ingre:
                break
        flag_to_add=True
        if idx != len(ingredients_list)-1:
            for ingr in retrieved_cocktail.find("ingredients"):
                if ingr.get('alc_type') == ingredient_to_add.alc_type and ingredient_to_add.alc_type=="":
                    #EN CASO DE BEEBIDA NO ALGOHOLICA SUSTITUYO POR BASIC TASTE
                    if ingr.get("basic_taste") == ingredient_to_add.basic_taste:
                        retrieved_cocktail.find("ingredients").remove(ingr)
                        to_add = etree.SubElement(retrieved_cocktail.find("ingredients"), "ingredient",
                                                  id=ingr.get('id'), alc_type=ingredient_to_add.alc_type,
                                                  basic_taste=ingredient_to_add.basic_taste,
                                                  measure=ingredient_to_add.measure,
                                                  quantity=ingredient_to_add.quantity,
                                                  unit=ingredient_to_add.unit)
                        retrieved_cocktail.append(to_add)
                        flag_to_add=False
                #Si es mismo alcohol Y DIFERENTE NOMBRE SE CAMBIA
                elif ingr.get('alc_type') == ingredient_to_add.alc_type and ingr.text != ingredient_to_add.name:
                    retrieved_cocktail.find("ingredients").remove(ingr)
                    to_add = etree.SubElement(retrieved_cocktail.find("ingredients"), "ingredient",
                                              id=ingr.get('id'), alc_type=ingredient_to_add.alc_type,
                                              basic_taste=ingredient_to_add.basic_taste,
                                              measure=ingredient_to_add.measure, quantity=ingredient_to_add.quantity,
                                              unit=ingredient_to_add.unit)
                    retrieved_cocktail.append(to_add)
                    flag_to_add = False
            if flag_to_add:
                to_add = etree.SubElement(retrieved_cocktail.find("ingredients"), "ingredient",
                                          id=ingredient_to_add.identifier, alc_type=ingredient_to_add.alc_type,
                                          basic_taste=ingredient_to_add.basic_taste,
                                          measure=ingredient_to_add.measure,
                                          quantity=ingredient_to_add.quantity,
                                          unit=ingredient_to_add.unit)
                retrieved_cocktail.append(to_add)
                step = etree.SubElement(retrieved_cocktail.find("preparation"), "step")
                # Posiblemente se necesite añadir una step luego de añadir el nuevo elemento, revisar codigo de todas formas, y hay que pensar forma de añadirlo logicamente.
                step.text = "Add " + str(ingredient_to_add.identifier) + " to the cocktail."
                retrieved_cocktail.find("preparation").append(step)
    return retrieved_cocktail

    '''for ingr in retrieved_cocktail.find("ingredients"):
        # Remove ingredients if they belong to "forbidden_ingredients"
        if ingr.text not in ingredients and ingr.text not in constraints["exc_ingredients"]:
            # ingredients[ingr.get('id')] = ingr.text # ESTA ERA LA LINEA ORIGINAL, Por que? ingredients es un array eh no tiene clave
            #ingredients.append(ingr.text) # Esto es lo que querías hacer?????????? No entiendo bien que se quería aquí por eso pregunto
            ingredients_cocktail[ingr.get('id')] = ingr.text # si quieres guardar el ingrediente con su id, no me parece demasiada buena idea, después como recuperamos el id? Sería como un for loop con un array no?
            # TODO: se indexa así por el nombre o por "ingr5"?
    alc_type = constraints["alc_type"]
    # Differenciate between constraints with a alcohol type or with a brand (name) -> substitute
    # TODO: How to substitute? there are cocktails with 3 different Rums

    # Propuesta de como buscar cambios, no se cuanto de bien estará
    possible_changes_ingredients_alc_type = []
    for ingr in ingredients_list:
        # Remove ingredients if they belong to "forbidden_ingredients"
        if ingr.name not in constraints["exc_ingredients"]:
            if ingr.alc_type in alc_type:
                possible_changes_ingredients_alc_type.append(ingr)




    # Adapt the steps'''

