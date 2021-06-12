import sys

from adaptation import adaptation_step
from menu_interactivo import menu_interactivo
from read_constraints import read_parse_json
#from retrieval import retrieval_step


def main():
    if len(sys.argv) > 1:
        json = sys.argv[1]
        constraints=read_parse_json(json)
        print(constraints)
        #constraints, retrieved_case = retrieval_step(constraints)
        adapted_case=adaptation_step( constraints)
        print(adapted_case.find("glasstype").text)
        for ingre in adapted_case.find("ingredients"):
            print(ingre.text)
        for ingre in adapted_case.find("preparation"):
            print(ingre.text)

    else:
        constraints = menu_interactivo()
        #constraints, retrieved_case = retrieval_step(constraints)
        adaptation_step( constraints)


if __name__ == "__main__":
    main()