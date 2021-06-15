import argparse
import json
import os
import time
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from cbr import CBR
from create_case_library import create_xml_library

DATA_PATH = '../DATA'

def parse_arguments():
    """ Define program input arguments and parse them.
    """
    # Create the parser and add arguments
    parser = argparse.ArgumentParser()
    parser.add_argument(dest='tests', type=str, help="path where the json test file is")

    # Parse arguments
    args = parser.parse_args()

    return args


def perform_tests(args):
    cbr = CBR(os.path.join(DATA_PATH, 'case_library.xml'))
    get_new_case_times = []
    evaluated_learn_new_case = []
    with open(args.tests) as json_file:
        data = json.load(json_file)
        for key, value in data.items():
            # Get test constraints of each case
            constraints = value
            # Get new case
            start = time.time()
            retrieved_case, adapted_case, original = cbr.get_new_case(constraints)
            end = time.time()
            get_new_case_times.append(end - start)

            # Evaluate if cocktail is derived (not original)
            start = time.time()
            if not original:
                cbr.evaluate_new_case(retrieved_case, adapted_case, 8.0)
            end = time.time()
            evaluated_learn_new_case.append(end - start)

    with open("./results.txt", 'w') as output:
        print(get_new_case_times, file=output)
        print(evaluated_learn_new_case, file=output)


if __name__ == "__main__":
    # Input arguments
    args = parse_arguments()

    # tests
    perform_tests(args)
