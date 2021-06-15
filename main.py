import sys
import argparse

from cbr import CBR
from utils import load_constraints, interactive_menu, evaluation_menu




# from retrieval import retrieval_step

def process(self, constraints):
        """ CBR principal flow, where the different stages of the CBR will be called

        Args:
            constraints (dict): dictionary containing a set of constraints

        Returns: adapted case and new database

        """
        # RETRIEVAL PHASE
        retrieved_case = cbr.retrieval(constraints)
        
        # ADAPTATION PHASE
        adapted_case, n_changes = cbr.adaptation(constraints, retrieved_case)
        
        # CHECK ADAPTED SOLUTION HAS AT LEAST A CHANGE
        if n_changes == 0:
            return adapted_case, self.cocktails
        
        # CHECK ADAPTED SOLUTION IS NOT A FAILURE
        if cbr.check_adapted_failure(adapted_case):
            adapted_case.get('evaluation').text = "Failure"
            ev_score = 0.0
            cbr.learning(retrieved_case, adapted_case, ev_score)
            return adapted_case, self.cocktails
        
        # EVALUATION PHASE
        adapted_case, ev_score = self.evaluation(adapted_case)
        
        # LEARNING PHASE
        cbr.learning(retrieved_case, adapted_case, ev_score)

        return adapted_case, self.cocktails

def parse_arguments():
    """ Define program input arguments and parse them.
    """
    # Create the parser and add arguments
    parser = argparse.ArgumentParser()
    parser.add_argument(dest='caselibrary', type=str, help="Filepath of the XML case library")
    parser.add_argument("--verbosity", type=int, help="Output verbosity", default=0)
    parser.add_argument('-c', '--constraints', type=str, help="Filepath of the JSON constraints file")

    # Parse arguments
    args = parser.parse_args()
    
    return args

def get_constraints(args, cbr):
    """ Get user constraints.
    
    Depending on the constraints arg, load from JSON or launch
    interactive menu to manually inptut them by keyboard.
    
    If JSON constraints are invalid, exit system

    Args:
        args (argparse.Namespace): parsed arguments
        cbr (CBR): initialized CBR system
        
    Return:
        dict: constraints to be fulfilled.
    """
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
        
    # Print constraints
    print('\nUser constraints:')
    for k, v in constraints.items():
        if len(v):
            print(f'{k}: {v}')
    print()
            
    return constraints
        
if __name__ == "__main__":
        
    # Input arguments
    args = parse_arguments()
    
    # Initialize CBR
    cbr = CBR(args.caselibrary, verbose=args.verbosity)
    
    # Get user constraints
    constraints = get_constraints(args, cbr)   
    
    # RETRIEVAL PHASE
    retrieved_case = cbr.retrieval(constraints)
    
    # ADAPTATION PHASE
    adapted_case, n_changes = cbr.adaptation(constraints, retrieved_case)
    
    # CHECK ADAPTED SOLUTION HAS AT LEAST A CHANGE
    if n_changes > 0:
        # CHECK ADAPTED SOLUTION IS NOT A FAILURE
        if cbr.check_adapted_failure(adapted_case):
            adapted_case.get('evaluation').text = "Failure"
            ev_score = 0.0
            cbr.learning(retrieved_case, adapted_case, ev_score)
        
        # EVALUATION PHASE
        ev_score = evaluation_menu(cbr, adapted_case)
        
        # LEARNING PHASE
        cbr.learning(retrieved_case, adapted_case, ev_score)

    adapted_case, cbr.cocktails
    
    
    # Print retrieved case
    # print(f'\nRetrieved cocktail: {retrieved_case.find("name").text}')
    # print(f'\nIngredients:')
    # cbr.print_ingredients(retrieved_case)
    # print(f'\nPreparation:')
    # cbr.print_preparation(retrieved_case)
    # print()
    
