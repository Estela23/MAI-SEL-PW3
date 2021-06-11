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
    ingredients_cocktail={}
    for ingr in retrieved_cocktail.find("ingredients"):
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
    print(possible_changes_ingredients_alc_type)



    # Adapt the steps

