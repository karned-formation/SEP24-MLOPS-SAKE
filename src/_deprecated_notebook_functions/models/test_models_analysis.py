import numpy as np
import pandas as pd
from typing import Self

from sklearn.metrics import ConfusionMatrixDisplay
import matplotlib.pyplot as plt

#from sklearn.neighbors import KNeighborsClassifier
#from sklearn.svm import SVC
#from sklearn.naive_bayes import CategoricalNB
#from sklearn.linear_model import LogisticRegression, LogisticRegressionCV
#from sklearn.ensemble import GradientBoostingClassifier, BaggingClassifier, AdaBoostClassifier
#from sklearn.model_selection import GridSearchCV

from sklearn.metrics import classification_report
from imblearn.metrics import classification_report_imbalanced

class TestModel:
    def __init__(self) -> None:
        #self.models = {}
        return None
    #------------------------------------------------------------------------
    # Methods (refactored)
    #------------------------------------------------------------------------

    def fit_and_predict_and_classification_report_imbalanced (self, 
                                                            model, 
                                                            model_type: str, model_name: str, 
                                                            class_names,
                                                            X_train, X_test, 
                                                            y_train, y_test,
                                                            savemodel = ''
                                                            ):
        """ On a 'model', documented with 'model_type' and 'model_name', perform the following step
                - fit the 'model' with 'X_train' and 'y_train'
                - predict with 'X_test' and compare with 'y_test'
                - compute all the métrics and provide them in return

        Args:
            * model created
            * model_type et model_name : string
            * X_train_text_tfid
            * X_test_text_tfid
            * y_train_text
            * y_test_text    
        Returns:
            * model trained
            * df_report : the respective classification_report_imbalanced as a DataFrame
            * score_accuracy : the value of the score accuracy
            * df_confusion_matrix : the confusion matrix reshaped with index and column names
        """
        model = model.fit(X_train, y_train)
        y_pred_test = model.predict(X_test)
        report_classif_imbalanced = classification_report_imbalanced(y_test, y_pred_test, 
                                                                    target_names = class_names,
                                                                    zero_division=0, 
                                                                    output_dict=True) ## report as dictionnary
        ## to convert the report as dataframe
        df_report = pd.DataFrame(report_classif_imbalanced).transpose()
        df_report = df_report.reset_index()
        df_report["model_type"] = model_type
        df_report["model_name"] = model_name
        
        # to produce the confusion matrix
        df_confusion_matrix = pd.crosstab ( y_test, y_pred_test, 
                                        rownames=['Classe réelle'], colnames=['Classe Prédite'])
        # to map the index encoded names with the label of the classes
        df_confusion_matrix.index = class_names
        # to map the columns with the function ( utilisé au cas où classe non prédite
        mapping_label_classes = {indice: valeur for indice, valeur in enumerate(class_names)}
        df_confusion_matrix.columns = df_confusion_matrix.columns.map(mapping_label_classes) 

        score_accuracy = model.score(X_test, y_test)
        
        labels = class_names
        fig = plt.figure()
        ax = fig.add_subplot(111)        
        ConfusionMatrixDisplay.from_predictions(y_test, y_pred_test, ax=ax, cmap="Blues", colorbar=False, display_labels=labels)
        ax.set_title(model_name + " (Accuracy = {:.2%})".format(score_accuracy))
        ax.set_xticks(np.arange(len(labels)))
        ax.set_yticks(np.arange(len(labels)))
        ax.set_yticklabels(labels, rotation_mode='anchor')
        ax.set_xticklabels(labels, rotation=40, ha='right', rotation_mode='anchor')
        ax.tick_params(axis='y', which='both', labelright=True, labelleft=False, right=True, left=False)
        if savemodel == '':
            plt.show()
        else:
            plt.savefig(savemodel, bbox_inches='tight')

        return model, df_report, score_accuracy, df_confusion_matrix  

