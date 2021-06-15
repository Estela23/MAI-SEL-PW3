import argparse
import json
import os
import time
import numpy as np
import matplotlib.pyplot as plt

from cbr import CBR
from create_case_library import create_xml_library


def parse_arguments():
    """ Define program input arguments and parse them.
    """
    # Create the parser and add arguments
    parser = argparse.ArgumentParser()
    parser.add_argument(dest='path', type=str, help="path where the csv file is")
    parser.add_argument(dest='tests', type=str, help="path where the json test file is")

    # Parse arguments
    args = parser.parse_args()

    return args


def perform_tests(args):
    create_xml_library(args.path)
    cbr = CBR("Data/case_library.xml")
    get_new_case_times = []
    evaluated_learn_new_case_times = []
    with open(args.tests) as json_file:
        data = json.load(json_file)
        for key, value in data.items():
            # Get test constraints of each case
            constraints = value
            # Get new case
            start_ra = time.time()
            retrieved_case, adapted_case, original = cbr.get_new_case(constraints)
            end_ra = time.time()
            get_new_case_times.append(end_ra - start_ra)

            # Evaluate if cocktail is derived (not original)
            start_el = time.time()
            if not original:
                cbr.evaluate_new_case(retrieved_case, adapted_case, 8.0)
            end_el = time.time()
            evaluated_learn_new_case_times.append(end_el - start_el)

            total_times = np.array(get_new_case_times) + np.array(evaluated_learn_new_case_times)

        mean_ra_time = np.mean(np.array(get_new_case_times))
        mean_el_time = np.mean(np.array(evaluated_learn_new_case_times))
        mean_total_time = np.mean(total_times)
        print(f"The average time needed for retrieval and adaptation steps is : {mean_ra_time}")
        print(f"The average time needed for evaluation and adaptation steps is: {mean_el_time}")
        print(f"The average total time for the complete CBR cycle over a new case is : {mean_total_time}")

        experiments = [i for i in range(len(total_times))]
        plt.plot(experiments, total_times, color="red", label="Total time")
        plt.plot(experiments, np.array(get_new_case_times), color="green", label="Retrieval and Adaptation")
        plt.plot(experiments, np.array(evaluated_learn_new_case_times), color="blue", label="Evaluation and Learning")
        plt.title("Times needed for each phase for 100 experiments")
        plt.xlabel("Queries performed")
        plt.ylabel("Time in seconds")
        plt.legend(loc="upper left")
        plt.show()

    with open("tests/results.txt", 'w') as output:
        print(get_new_case_times, file=output)
        print(evaluated_learn_new_case_times, file=output)


if __name__ == "__main__":
    # Input arguments
    args = parse_arguments()

    # tests
    perform_tests(args)
