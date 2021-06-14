import sys

from cbr import CBR
from utils import load_json, interactive_menu


# from retrieval import retrieval_step


def main():
    if len(sys.argv) > 1:
        json = sys.argv[1]
        constraints = load_json(json)
        cbr = CBR('Data/case_library.xml')
        print(constraints)
        # constraints, retrieved_case = retrieval_step(constraints)
        aaaaa = None
        adapted_case = cbr.adaptation(constraints, aaaaa)
        print(adapted_case.find("glasstype").text)
        for ingre in adapted_case.find("ingredients"):
            print(ingre.text)
        for ingre in adapted_case.find("preparation"):
            print(ingre.text)

    else:
        constraints = interactive_menu()
        # constraints, retrieved_case = retrieval_step(constraints)
        interactive_menu(constraints)


if __name__ == "__main__":
    main()
