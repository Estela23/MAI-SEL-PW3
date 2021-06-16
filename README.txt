################################################################################################
#    Supervised and Experiential Learning (SEL)                                                #
#    Master in Artificial Intelligence (UPC)                                                   #
#    PW3 - A CBR prototype for a synthetic task                                                #
#          A CBR for a cocktail recipe creator                                                 #
#                                                                                              #
#    Authors: Xavier Cucurull Salamero <xavier.cucurull@estudiantat.upc.edu>                   #   
#             Daniel Hinjos García <daniel.hinjos@estudiantat.upc.edu>                         #
#             Fernando Vázquez Novoa <fernando.vazquez.novoa@estudiantat.upc.edu>              # 
#             Estela Vázquez-Monjardín Lorenzo <estela.vazquez-monjardin@estudiantat.upc.edu>  #
#    Course: 2020/2021                                                                         #
################################################################################################

Contents of the delivery folder:
    Data: 
       - data_cocktails.csv: original dataset
       - case_library.xml: case library created from the original dataset
       - my_cosntraints.json: example of a constraints JSON  file

    Source
        - main.py: main script to run the CLI program
        - cbr.py: implementation of the CBR engine
        - create_case_library.py: script to convert the CSV dataset to the XML case library
        - utils.py: implementation of various functions (to load json, to crate user menu, etc.)
        - requirements.txt: packages required to correctly execute the code

    app: contains the files related to the GUI application.
        - main.py: main script to run the GUI application

    tests: files used to automatically test the system

    Documentation:
        - PW3_SEL-Cockatil_CBR_Report.pdf: written report
        - User_Manual: user manual for the Cocktails CBR
        - PW3_SEL-Cockatil_CBR_Slides.pdf: presentation slides

INSTRUCTIONS:
In order to execute the CLI application follow these steps:
    1. Open a terminal and navigate to this folder.
        $ cd PW3_delivery

    2. Install the required packages.
        $ pip install -r requirements.txt

    3. Execute the main script loading the case library
        $ python main.py Data/case_library.xml

In order to execute the GUI application follow these steps:
    1. Open a terminal and navigate to this folder.
        $ cd PW3_delivery

    2. Install the required packages.
        $ pip install -r requirements.txt

    3. Execute the app main script
        $ python app/main.py
