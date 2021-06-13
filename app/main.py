import sys
from PySide2 import QtCore, QtGui, QtWidgets
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QApplication, QMainWindow
from PySide2.QtCore import QFile
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from cbr import CBR

DATA_PATH = 'Data'

        
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
    def __init__(self, ui_filename):        
        loader = QUiLoader()
        self.dialog = loader.load(os.path.join(os.path.dirname(__file__), ui_filename), None) 
        self.dialog.btn_getrecipes.clicked.connect(self.btn_click)
        self.dialog.show()
        
        
        self.cbr = self.cbr = CBR(os.path.join(DATA_PATH, 'case_library.xml'), verbose=True)
    
        # self.dialog.scrollArea.setLayout(self.vbox)
        
        #Scroll Area Properties
        # self.dialog.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        # self.dialog.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        #self.dialog.scrollArea.setWidgetResizable(True)
        #   self.dialog.scrollArea.setWidget(self.widget)

        # Redirect stdout and stderr
        sys.stdout = OutLog(self.dialog.logText)
        sys.stderr = OutLog(self.dialog.logText, color=QtGui.QColor(255,0,0))
        
    def btn_click(self):
        ingredients = self.dialog.text_ingredients.text().split(', ')
        if not ingredients[0]:
            ingredients = []
            print('KDAJFLKDASJFLKJAKLDFJKLASDS')
            
        alc_types = self.dialog.text_alc_types.text().split(', ')
        if not alc_types[0]:
            alc_types = []
            
        basic_tastes = self.dialog.text_basic_tastes.text().split(', ')
        if not basic_tastes[0]:
            basic_tastes = []
            
        exc_ingredients = self.dialog.text_exc_ingredients.text().split(', ')
        if not exc_ingredients[0]:
            exc_ingredients = []
            
        name = self.dialog.text_name.text()
        if not name:
            name = 'SEL-Cocktail'
        
        #category = self.dialog.comboBox_categories.currentText()
        categories = []
        glass_types = ['old-fashioned glass']

        constraints = {'name': name, 'category': categories, 'glass_type': glass_types, 'ingredients': ingredients,
                    'alc_type': alc_types, 'basic_taste': basic_tastes, 'exc_ingredients': exc_ingredients}
        
        print(f'constraints: {constraints}\n')        

        self.test_cbr(constraints)
        
    def test_cbr(self, constraints):
        # Retrive cocktail wight given constraints
        c = self.cbr._retrieval(constraints)
        print(f'\n{c.find("name").text} cocktail retrieved')

        print('\nOriginal Ingredients:')
        self.cbr._print_ingredients(c)
        print('\nOriginal Preparation:')
        self.cbr._print_preparation(c)

        adapted_cocktail = self.cbr._adaptation(constraints, c)
        print(f'\n{adapted_cocktail.find("name").text} cocktail adapted')

        print('\nAdapted Ingredients:')
        self.cbr._print_ingredients(adapted_cocktail)
        print('\nAdapted Preparation:')
        self.cbr._print_preparation(adapted_cocktail)

        # Evaluate constraints
        evaluation, eval_results = self.cbr._evaluate_constraints_fullfillment(constraints, adapted_cocktail)

        if evaluation:
            print('\nAll contstraints fullfilled!')
        else:
            print('\nConstraints error:')
            print('\n'.join(eval_results))
            assert (evaluation)
        
        
if __name__ == "__main__":
    ui_filename = 'form.ui'
    app = QtWidgets.QApplication(sys.argv)
    cocktail_app = CocktailsApp(ui_filename)
    sys.exit(app.exec_())