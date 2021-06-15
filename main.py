import sys
import argparse

from cbr import CBR
from utils import load_constraints, interactive_menu




# from retrieval import retrieval_step

def process(self, constraints):
        """ CBR principal flow, where the different stages of the CBR will be called

        Args:
            constraints (dict): dictionary containing a set of constraints

        Returns: adapted case and new database

        """
        # RETRIEVAL PHASE
        retrieved_case = self._retrieval(constraints)
        
        # ADAPTATION PHASE
        adapted_case, n_changes = self._adaptation(constraints, retrieved_case)
        
        # CHECK ADAPTED SOLUTION HAS AT LEAST A CHANGE
        if n_changes == 0:
            return adapted_case, self.cocktails
        
        # CHECK ADAPTED SOLUTION IS NOT A FAILURE
        if self._check_adapted_failure(adapted_case):
            adapted_case.get('evaluation').text = "Failure"
            ev_score = 0.0
            self._learning(retrieved_case, adapted_case, ev_score)
            return adapted_case, self.cocktails
        
        # EVALUATION PHASE
        adapted_case, ev_score = self.evaluation(adapted_case)
        
        # LEARNING PHASE
        self._learning(retrieved_case, adapted_case, ev_score)

        return adapted_case, self.cocktails
    
def main():
    if len(sys.argv) > 1:
        json = sys.argv[1]
        constraints = load_constraints(json)
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
    #main()
    
    # Create the parser and add arguments
    parser = argparse.ArgumentParser()
    parser.add_argument(dest='caselibrary', type=str, help="Filepath of the XML case library")
    parser.add_argument("--verbosity", type=int, help="Output verbosity", default=0)
    parser.add_argument('-c', '--constraints', type=str, help="Filepath of the JSON constraints file")

    # Parse arguments
    args = parser.parse_args()
    
    # Initialize CBR
    cbr = CBR(args.caselibrary, verbose=args.verbosity)
    
    if args.constraints:
        # Load constraints from JSON
        constraints = load_constraints(args.constraints)
        
        # Check validity of constraints
        err = cbr.check_constraints(constraints)
        # If error in constraints, exit
        if len(err):
            print('Error: invalid constraints!')
            print('\n'.join(err))
            exit(1)

    else:
        # Launch interactive menu to manually input constraints
        constraints = interactive_menu(cbr)
        