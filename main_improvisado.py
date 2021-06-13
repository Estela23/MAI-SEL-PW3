import sys

from cbr import CBR
from read_constraints import read_parse_json
#from retrieval import retrieval_step


def main():
    if len(sys.argv) > 1:
        json = sys.argv[1]
        constraints=read_parse_json(json)
        cbr = CBR('Data/case_library.xml')
        print(constraints)
        #constraints, retrieved_case = retrieval_step(constraints)
        aaaaa=None
        adapted_case=cbr.adaptation( constraints,aaaaa)
        print(adapted_case.find("glasstype").text)
        for ingre in adapted_case.find("ingredients"):
            print(ingre.text)
        for ingre in adapted_case.find("preparation"):
            print(ingre.text)

    else:
        constraints = menu_interactivo()
        #constraints, retrieved_case = retrieval_step(constraints)
        adaptation( constraints)


if __name__ == "__main__":
    main()