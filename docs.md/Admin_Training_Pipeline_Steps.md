# Step n°0 : l'admin gére les images d'entrainement (add / get / delete)
![Manage_images](../docs/Admin_train_Overview_Step0_Manage_images.png)

# Step n°1 : l'admin lance l'entrainement (déclenchement de la pipeline DVC)
![Training_pipeline](../docs/Admin_train_Overview_Step1_Training_pipeline.png)

# Step n°2 : l'admin analyse les résultats des expériences enregistrée via MLFlow (et restaure éventuellement une ancienne expérience => tout est restauré: images+modèles+metrics)
![Analyse_and_select_Experiment](../docs/Admin_train_Overview_Step2_Analyse_and_select_Experiment.png)

# Step n°3 : l'admin enregistre le modèle correspondant à l'expérience sélectionnée (éventuellement une ancienne expérience)
![Register_Model](../docs/Admin_train_Overview_Step3_Register_Model.png)