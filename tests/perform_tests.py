import argparse
import json
import os
import time
import sys
import numpy as np
import matplotlib.pyplot as plt

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from cbr import CBR
from create_case_library import create_xml_library

DATA_PATH = '../DATA'

def parse_arguments():
    """ Define program input arguments and parse them.
    """
    # Create the parser and add arguments
    parser = argparse.ArgumentParser()
    parser.add_argument(dest='path', type=str, help="path where the csv dataset file is")
    parser.add_argument(dest='tests', type=str, help="path where the json test file is")

    # Parse arguments
    args = parser.parse_args()

    return args


def perform_tests(args):
    # Convert CSV to xml to make sure that case_library.xml only contains original recipes
    xml_file = os.path.join(DATA_PATH, 'case_library.xml')
    create_xml_library(args.path, xml_file)
    
    cbr = CBR(xml_file)
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
        plt.plot(experiments, total_times, color="red", label="Total Time")
        plt.plot(experiments, np.array(get_new_case_times), color="green", label="Retrieval and Adaptation")
        plt.plot(experiments, np.array(evaluated_learn_new_case_times), color="blue", label="Evaluation and Learning")
        plt.plot([0, len(total_times)], [mean_total_time, mean_total_time], "--", color="red",
                 label="Average Total Time")
        plt.title(f"Times needed for each phase for {len(total_times)} experiments")
        plt.xlabel("Queries performed")
        plt.ylabel("Time in seconds")
        plt.legend(loc="upper left")
        plt.savefig(f"{len(total_times)}_results.png")
        plt.show()

    with open(f"./{len(total_times)}_results.txt", 'w') as output:
        print(get_new_case_times, file=output)
        print(evaluated_learn_new_case_times, file=output)


if __name__ == "__main__":
    # Input arguments
    args = parse_arguments()

    # tests
    perform_tests(args)
