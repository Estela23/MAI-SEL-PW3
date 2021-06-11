def adapt_steps(best_case, constraints):
    solution = {"name": constraints["name"] if "name" in constraints else str(best_case["name"]) + "2.0",
                "category": constraints["category"] if "category" in constraints else best_case["category"],
                "glasstype": constraints["glasstype"] if "glasstype" in constraints else best_case["glasstype"]}

    # Adapt the ingredients:
    # Add ingredients
    # TODO: hacer esto al revés para tener las cantidades, meter primero los de la receta y luego los que añadimos
    ingredients = constraints["ingredients"]    # TODO: quantity? index?
    for ingr in best_case["ingredients"]:
        # Remove ingredients if they belong to "forbidden_ingredients"
        if ingr not in ingredients:
            ingredients[ingr["name"]] = ingr["name"] if ingr["name"] not in constraints["forbidden_ingredients"]
        # TODO: se indexa así por el nombre o por "ingr5"?

    # Differenciate between constraints with a alcohol type or with a brand (name) -> substitute
    # TODO: How to substitute? there are cocktails with 3 different Rums



    # Adapt the steps

