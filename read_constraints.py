import json
import xml.etree.ElementTree as ET


def read_parse_json(filename):
    tree = ET.parse('Data/case_library.xml')
    cocktails = tree.getroot()
    categories = set([child.find('category').text for child in cocktails])
    glasses=set([child.find('glasstype').text for child in cocktails])
    ingredients=set([child.find('ingredients').find('ingredient').text for child in cocktails])
    alc_types = set([child.find('ingredients').find('ingredient').attrib['alc_type'] for child in cocktails])
    with open(filename) as json_file:
        data = json.load(json_file)
    if len(data.keys()) == 0:
        print("Empty JSON, please add some constraint")
        exit(1)
    elif 'constraints' in data:
        if len(data['constraints'].keys()) == 0:
            print("No constraints specified, please specify some.")
            exit(1)
        if 'category' in data['constraints'] and data['constraints']['category'] not in categories:
            data['constraints']['category'] = ""
        if 'glass_type' in data['constraints'] and data['constraints']['glass_type'] not in glasses:
            data['constraints']['glass_type'] = ""
        if 'ingredients' not in data['constraints']:
            data['constraints']['ingredients'] = []
        else:
            aux = 0
            for idx, ingredient in enumerate(data['constraints']['ingredients']):
                if ingredient not in ingredients:
                    data['constraints']['ingredients'].remove(idx - aux)
                    aux = aux + 1
        if 'alc_type' not in data['constraints']:
            data['constraints']['alc_type']=[]
        else:
            aux=0
            for idx, alc_type in enumerate(data['constraints']['alc_type']):
                if alc_type not in alc_types:
                    data['constraints']['alc_type'].remove(idx-aux)
                    aux=aux+1
        if 'exc_ingredients' not in data['constraints']:
            data['constraints']['exc_ingredients']=[]
        else:
            aux=0
            for idx, exc_ingredients in enumerate(data['constraints']['exc_ingredients']):
                if exc_ingredients not in ingredients or exc_ingredients in data['constraints']['ingredients']:
                    data['constraints']['alc_type'].remove(idx-aux)
                    aux=aux+1
    return data['constraints']
