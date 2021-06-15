import sys
import json
import PySide2
from PySide2 import QtCore, QtGui, QtWidgets
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QApplication, QMainWindow
from PySide2.QtCore import QFile
import os
import platform
import subprocess
import webbrowser as wb

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from cbr import CBR
from utils import load_constraints

DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'Data')
USER_MANUAL = 'User_Manual.pdf'

loader = QUiLoader()
        
class OutLog:
    def __init__(self, edit, out=None, color=None):
        """
        Write stdout, stderr to a QTextEdit.
        
        Arguments:
            edit = QTextEdit
            out = alternate stream ( can be the original sys.stdout )
            color = alternate color (i.e. color stderr a different color)

        Note: source: http://stackoverflow.com/questions/17132994/pyside-and-python-logging/17145093#17145093
        """
        self.edit = edit
        self.out = None
        self.color = color

    def write(self, m):
        if self.color:
            tc = self.edit.textColor()      # save default text color
            self.edit.setTextColor(self.color)

        self.edit.moveCursor(QtGui.QTextCursor.End)
        self.edit.insertPlainText(m)

        if self.color:
            self.edit.setTextColor(tc)      # restore default text color

        if self.out:
            self.out.write(m)
                
class CocktailsApp():
    """ Cocktails App
    
    Define and configure various functions used to detect button clicks and
    retrieve text from input boxes.
    """
    def __init__(self, ui_filename):
        # Load UI        
        self.dialog = loader.load(os.path.join(os.path.dirname(__file__), ui_filename), None) 
        self.dialog.show()
        
        # Set title image
        pixmap = QtGui.QPixmap(os.path.join(os.path.dirname(__file__), 'title.png'))                                                                                                        
        self.dialog.label.setPixmap(pixmap)   
        
        # Button actions
        self.dialog.btn_getrecipes.clicked.connect(self.btn_getrecipe)
        self.dialog.btn_resetquery.clicked.connect(self.btn_resetquery)
        self.dialog.btn_rate.clicked.connect(self.btn_rate)
        
        # Menu actions
        self.dialog.actionAbout.triggered.connect(self.about)
        self.dialog.actionConstraints.triggered.connect(self.load_constraints_file)
        self.dialog.actionLibrary.triggered.connect(self.load_library_file)
        self.dialog.actionExport.triggered.connect(self.export_constraints_file)
        self.dialog.actionUser_Manual.triggered.connect(self.open_user_manual)
        
        # Slider action
        self.dialog.slider_evaluation.valueChanged.connect(self.slider_change)
        
        # Init CBR
        self.cbr = CBR(os.path.join(DATA_PATH, 'case_library.xml'), verbose=True)

        # Redirect stdout and stderr
        # sys.stdout = OutLog(self.dialog.logText)
        # sys.stderr = OutLog(self.dialog.logText, color=QtGui.QColor(255,0,0))
    
    def open_user_manual(self):
        """ Open Ueser Manual PDF
        """
        filename = os.path.join(os.path.dirname(__file__), '..', 'Documentation', USER_MANUAL)
        filename = os.path.abspath(filename)
        print(f'Opening {filename}...')
        wb.open_new(r'file://{}'.format(filename))
        
    def slider_change(self):
        """ When evaluation slider changes, update label.
        """
        self.dialog.label_rating.setText(str(self.dialog.slider_evaluation.value()))
        
    def btn_rate(self):
        """ When button "Rate" is clicked, evalute adapted cocktail
        """
        evaluation = self.dialog.slider_evaluation.value()        
        self.cbr.evaluate_new_case(self.retrieved_cocktail, self.adapted_cocktail, evaluation)
        self.dialog.btn_rate.setEnabled(False)
        
    def btn_resetquery(self):
        """ When the button "Reset Query" is clicked, clear all the text boxes.
        """
        self.dialog.text_ingredients.clear()
        self.dialog.text_alc_types.clear()
        self.dialog.text_basic_tastes.clear()
        self.dialog.text_glass_types.clear()
        self.dialog.text_exc_ingredients.clear()
        self.dialog.text_exc_alc_types.clear()
        self.dialog.text_exc_basic_tastes.clear()
        self.dialog.text_name.clear()
        self.dialog.or_recipe_text.clear()
        self.dialog.ad_recipe_text.clear()
        
        cat_checkboxes = self.dialog.categoriesBox.findChildren(QtWidgets.QCheckBox)
        for c in cat_checkboxes:
            c.setChecked(False)
            
        self.dialog.btn_rate.setEnabled(True)     
   
    def btn_getrecipe(self):
        """ When the button "Get Recipe" is clicked, retrieve inputs,
        call CBR and display retrieved and adapted recipes.
        """
        # Get constraints from user input
        constraints = self.get_constraints()   
        
        # Check if constraints contain any error
        constraints_err = self.cbr.check_constraints(constraints)
        if len(constraints_err):
            # Prompt error message
            button = QtWidgets.QMessageBox.critical(self.dialog, "Constraints error!",
            "\n".join(constraints_err), buttons=QtWidgets.QMessageBox.Close,
            defaultButton=QtWidgets.QMessageBox.Close)
        else:
            # Print constraints
            print(f'constraints: {constraints}\n')   
        
            self.test_cbr(constraints)
    
    def get_constraints(self):
        """ Get constraints from user input

        Returns:
            dict: constraints
        """
        ingredients = self.dialog.text_ingredients.text().lower().split(', ')
        if not ingredients[0]:
            ingredients = []
            
        alc_types = self.dialog.text_alc_types.text().lower().split(', ')
        if not alc_types[0]:
            alc_types = []
            
        basic_tastes = self.dialog.text_basic_tastes.text().lower().split(', ')
        if not basic_tastes[0]:
            basic_tastes = []
            
        glass_types = self.dialog.text_glass_types.text().lower().split(', ')
        if not glass_types[0]:
            glass_types = []

        exc_ingredients = self.dialog.text_exc_ingredients.text().lower().split(', ')
        if not exc_ingredients[0]:
            exc_ingredients = []
            
        exc_alc_types= self.dialog.text_exc_alc_types.text().lower().split(', ')
        if not exc_alc_types[0]:
            exc_alc_types = []
            
        exc_basic_tastes = self.dialog.text_exc_basic_tastes.text().lower().split(', ')
        if not exc_basic_tastes[0]:
            exc_basic_tastes = []
            
        name = self.dialog.text_name.text()
        if not name:
            name = 'SEL-Cocktail'
        
        cat_checkboxes = self.dialog.categoriesBox.findChildren(QtWidgets.QCheckBox)
        categories = [c.text().lower() for c in cat_checkboxes if c.isChecked()]

        constraints = {'name': name, 'category': categories, 'glass_type': glass_types, 'ingredients': ingredients,
                    'alc_type': alc_types, 'basic_taste': basic_tastes, 'exc_ingredients': exc_ingredients,
                    'exc_alc_type': exc_alc_types, 'exc_basic_taste': exc_basic_tastes} 
        
        return constraints
    
    def test_cbr(self, constraints):
        """ Run CBR and obtain cocktail from constraints

        Args:
            constraints (dict): constraints to fulfill
        """
        # Get new case
        self.retrieved_cocktail, self.adapted_cocktail, original = self.cbr.get_new_case(constraints)
            
        # Get info about retrieved and adapted cocktails
        or_name = self.retrieved_cocktail.find("name").text
        print(f'\nRetrieved cocktail: {or_name}')
        print('\nOriginal Ingredients:')
        or_ingr_str = self.cbr.print_ingredients(self.retrieved_cocktail)
        print('\nOriginal Preparation:')
        or_prep_str = self.cbr.print_preparation(self.retrieved_cocktail)

        ad_name = self.adapted_cocktail.find("name").text
        print(f'\nAdapted cocktail: {ad_name}')
        print('\nAdapted Ingredients:')
        ad_ingr_str = self.cbr.print_ingredients(self.adapted_cocktail)
        print('\nAdapted Preparation:')
        ad_prep_str = self.cbr.print_preparation(self.adapted_cocktail)

        # Output original and adapte recipe
        self.dialog.or_recipe_text.setText(f'{or_name}\n\nIngredients:\n{or_ingr_str}\nPreparation:\n{or_prep_str}')
        self.dialog.ad_recipe_text.setText(f'{ad_name}\n\nIngredients:\n{ad_ingr_str}\nPreparation:\n{ad_prep_str}')
        
        # Evaluate if cocktail is derivated (not original)
        if not original:
            # Enable rating button
            self.dialog.btn_rate.setEnabled(True)        
     
    def about(self):
        about_text = """<b>Cocktails Recipes CBR</b>
                            <p>Copyright &copy; 2021. Some rights reserved.
                            <p>This CBR application is part of the final project of SEL PW3 
                            <p>(MAI - UPC) 
                            <p>
                            <p>Python {} - PySide version {} - Qt version {} on {}""".format(platform.python_version(),
                                                                                            PySide2.__version__,
                                                                                            QtCore.__version__,
                                                                                            platform.system())   
        dlg = loader.load(os.path.join(os.path.dirname(__file__), 'about.ui'), None) 
        dlg.label.setText(about_text)
        # Set image
        pixmap = QtGui.QPixmap(os.path.join(os.path.dirname(__file__), 'beers.png'))                                                                                                        
        dlg.label_beers.setPixmap(pixmap)  
        dlg.exec_()

    def load_constraints_file(self):
        constraints_file, _ = QtWidgets.QFileDialog.getOpenFileName(self.dialog, "Open Constraints", DATA_PATH,
                                                    'Json Files (*.json)')
        print(f'Load constraints from: {constraints_file} ...')
        
        # Load constraints
        constraints = load_constraints(constraints_file)
        
        # Set constraints
        self.dialog.text_ingredients.setText(', '.join(constraints['ingredients']))
        self.dialog.text_alc_types.setText(', '.join(constraints['alc_type']))
        self.dialog.text_basic_tastes.setText(', '.join(constraints['basic_taste']))
        self.dialog.text_glass_types.setText(', '.join(constraints['glass_type']))
        self.dialog.text_exc_ingredients.setText(', '.join(constraints['exc_ingredients']))
        self.dialog.text_exc_alc_types.setText(', '.join(constraints['exc_alc_type']))
        self.dialog.text_exc_basic_tastes.setText(', '.join(constraints['exc_basic_taste']))
        self.dialog.text_name.setText(constraints['name'])
        
        # Set categories
        cat_checkboxes = self.dialog.categoriesBox.findChildren(QtWidgets.QCheckBox)
        for c in cat_checkboxes:
            if c.text().lower() in constraints['category']:
                c.setChecked(True)
            else:
                c.setChecked(False)
                
    def load_library_file(self):
        library_file, _ = QtWidgets.QFileDialog.getOpenFileName(self.dialog, "Open Library", DATA_PATH,
                                                    'XML Files (*.xml)')
        print(f'Load CBR library from: {library_file} ...')
        
        try:
            # Init CBR
            self.cbr = CBR(library_file, verbose=True)
        except Exception as e:
            # Prompt error message
            button = QtWidgets.QMessageBox.critical(self.dialog, "Library error!",
            f'Library error. Choose a valid case library.\nException:{str(e)}', buttons=QtWidgets.QMessageBox.Close,
            defaultButton=QtWidgets.QMessageBox.Close)
        
    def export_constraints_file(self):
        constraints_file, _ = QtWidgets.QFileDialog.getSaveFileName(self.dialog, "Save File", DATA_PATH,
                                                    'Json Files (*.json)')
        print(f'Save constraints to: {constraints_file} ...')
        constraints = self.get_constraints()
        with open(constraints_file, 'w') as f:
            json.dump(constraints, f, indent=1)
                    
if __name__ == "__main__":
    ui_filename = 'form.ui'
    app = QtWidgets.QApplication(sys.argv)
    cocktail_app = CocktailsApp(ui_filename)
    sys.exit(app.exec_())