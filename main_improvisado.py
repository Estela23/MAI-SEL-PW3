import sys

from adaptation import adaptation_step
from menu_interactivo import menu_interactivo
from read_constraints import read_parse_json
from retrieval import retrieval_step


def main():
    if len(sys.argv) > 1:
        json = sys.argv[1]
        constraints=read_parse_json(json)
        constraints, retrieved_case = retrieval_step(constraints)
        adaptation_step(retrieved_case, constraints)
    else:
        constraints = menu_interactivo()
        constraints, retrieved_case = retrieval_step(constraints)
        adaptation_step(retrieved_case, constraints)


if __name__ == "__main__":
    print(len(sys.argv))
    main()