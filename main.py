"""

PW3 - SEL - 2021
CBR for a cocktail recipe creator

Authors:    Xavier Cucurull Salamero <xavier.cucurull@estudiantat.upc.edu>
            Daniel Hinjos García <daniel.hinjos@estudiantat.upc.edu>
            Fernando Vázquez Novoa <fernando.vazquez.novoa@estudiantat.upc.edu>
            Estela Vázquez-Monjardín Lorenzo <estela.vazquez-monjardin@estudiantat.upc.edu>
"""

import sys
import argparse

from cbr import CBR
from utils import load_constraints, interactive_menu, evaluation_menu


def parse_arguments():
    """ Define program input arguments and parse them.
    """
    # Create the parser and add arguments
    parser = argparse.ArgumentParser()
    parser.add_argument(dest='caselibrary', type=str, help="Filepath of the XML case library")
    parser.add_argument("--verbosity", type=int, help="Output verbosity level. Set to 1 to print debug messages.", default=0)
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
    """ Main program to get cocktails from the cocktails CBR
    given a set of constraints provided by the user.
    
    usage: main.py [-h] [--verbosity VERBOSITY] [-c CONSTRAINTS] caselibrary

    positional arguments:
        caselibrary           Filepath of the XML case library

        optional arguments:
        -h, --help            show this help message and exit
        --verbosity VERBOSITY
                                Output verbosity level. Set to 1 to print debug
                                messages.
        -c CONSTRAINTS, --constraints CONSTRAINTS
                                Filepath of the JSON constraints file
    """
    # Input arguments
    args = parse_arguments()
    
    # Initialize CBR
    cbr = CBR(args.caselibrary, verbose=args.verbosity)
    
    # Get user constraints
    constraints = get_constraints(args, cbr)   

    # Get new case
    retrieved_case, adapted_case, original = cbr.get_new_case(constraints)
    
    # Evaluate if cocktail is derivated (not original)
    if not original:
        ev_score = evaluation_menu(cbr, adapted_case)
        cbr.evaluate_new_case(retrieved_case, adapted_case, ev_score)
        