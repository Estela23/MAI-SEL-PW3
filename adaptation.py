def adapt_steps(best_case, constraints):
    solution = {"name": constraints["cocktail_name"],
                "category": constraints["category"] if "category" in constraints else best_case["category"],
                "glasstype": constraints["glasstype"] if "glasstype" in constraints else best_case["glasstype"]}

    # Adapt the ingredients:
    ingredients = constraints["ingredients"]
    for ingr in best_case["ingredients"]:
        if ingr["name"] not in constraints["forbidden_ingredients"]:
            ingredients[ingr["name"]] = ingr["name"]


