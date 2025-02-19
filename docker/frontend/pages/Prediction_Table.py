import streamlit as st
import requests
from datetime import datetime
import json
import pandas as pd
from PIL import Image
import os
from src.s3handler import S3Handler


st.set_page_config(page_title="Dashboard Page")


def get_env_var(name):
    """Retrieve environment variables securely."""
    value = os.getenv(name)
    if not value:
        raise EnvironmentError(f"La variable d'environnement '{name}' n'est pas définie ou est vide.")
    return value

def initialize_s3_handler():
    """Initialize the S3 handler with environment variables."""
    aws_access_key_id = get_env_var("AWS_ACCESS_KEY_ID")
    aws_secret_access_key = get_env_var("AWS_SECRET_ACCESS_KEY")
    aws_bucket_name = get_env_var("AWS_BUCKET_NAME")
    # logger.info("S3 handler initialized.")
    return S3Handler(aws_bucket_name)

# Fonction pour convertir un timestamp en date lisible
def convert_timestamp(timestamp):
    timestamp = float(timestamp)
    dt_object = datetime.fromtimestamp(timestamp)
    formatted_date = dt_object.strftime("%d %B %Y à %Hh%M")
    return formatted_date

# Fonction pour transformer les prédictions en DataFrame
def process_prediction_dataframe(prediction):
    prediction = json.loads(prediction)
    df = pd.DataFrame(prediction).T
    df.index = df.index.str.split("/").str[-1]
    df.index.name = 'Filename'
    return df

def process_new_prediction(prediction_response):
    predictions = prediction_response[1]
    
    # Create a list of dictionaries for DataFrame creation
    data = []
    for item in predictions:
        image_name = item['name']
        probabilities = {f"Prob_class_{p['id_class']}": p['confidence'] for p in item['probabilities']}
        probabilities['Filename'] = image_name
        data.append(probabilities)
    
    # Create DataFrame
    df = pd.DataFrame(data)
    df.set_index('Filename', inplace=True)
    return df

# Fonction pour analyser la réponse de l'API
def parse_response(pred):
    timestamp = pred['metadata']['time']
    date = convert_timestamp(timestamp)
    n_images = pred['metadata']['n_files']
    status = pred['status']
    uuid = pred['metadata']['uuid']
    prediction = process_new_prediction(pred['prediction']) if status == 'COMPLETED' else None
    return date, n_images, status, uuid, prediction

# Fonction pour gérer le clic sur le bouton "Valider les corrections"
def handle_submit(table_data, uuid):
    df = pd.DataFrame(table_data)

    # Chemin pour sauvegarder corrections_{uuid}.csv à la racine de "corrections/"
    corrections_dir = "corrections"
    os.makedirs(corrections_dir, exist_ok=True)  # Crée le dossier si nécessaire

    corrections_csv_path = os.path.join(corrections_dir, f"corrections_{uuid}.csv")
    df.to_csv(corrections_csv_path, index=False)

    # Création du fichier feedback.csv dans "corrections/{UUID}/prediction/"
    feedback_dir = os.path.join(corrections_dir, uuid, "prediction")
    os.makedirs(feedback_dir, exist_ok=True)  # Crée le dossier si nécessaire

    df_feedback = df.copy()
    df_feedback["Image"] = df_feedback["Image"].str.replace(r"^img/", "", regex=True)  # Supprime "img/" du chemin

    feedback_csv_path = os.path.join(feedback_dir, "feedback.csv")
    df_feedback.to_csv(feedback_csv_path, index=False)

    # Upload du fichier feedback.csv vers le S3
    remote_dir = os.path.join(uuid, "prediction")
    handler.upload_directory(remote_path=remote_dir, local_directory_name=feedback_dir)

    # Afficher un message de confirmation
    st.success("Corrections enregistrées avec succès !")
    st.info(f"Les corrections ont été enregistrées dans :\n- {corrections_csv_path}\n- {feedback_csv_path}")




handler = initialize_s3_handler()

st.title("Afficher les prédictions")

# Champ pour entrer la référence
reference = st.text_input("Entrez une référence pour récupérer les prédictions :")

if reference:  # Vérifie si une référence est entrée
    endpoint_url = f'http://localhost:8908/predict/{reference}'

    with st.spinner("Récupération des prédictions..."):
        response = requests.get(endpoint_url)

    if response.status_code != 200:
        st.error(f"Erreur {response.status_code} : {response.text}")
    else:
        if len(response.json()):
            with st.expander("View JSON Response", expanded=False):
                st.json(response.json())
            st.write("---")
            
            predictions = sorted(response.json(), key=lambda x: x['metadata']['time'], reverse=True)
            for pred in predictions:
                date, n_images, status, uuid, prediction = parse_response(pred)
                local_directory = os.path.join("img", uuid)  # Chemin local du répertoire
                if not os.path.exists(local_directory):
                    handler.download_directory(remote_directory_name=uuid, local_path="img/")
                if status == 'COMPLETED':
                    st.write(f"Prédiction du **{date}**")
                    st.markdown(f"""
                                - **Status :** {status}
                                - **Nombre de fichiers :** {n_images}
                                - **uuid :** {uuid}
                                """)

                    if prediction is not None:
                        filenames = prediction.index 
                        predicted_classes = prediction.idxmax(axis=1)  # Classe prédite (colonne avec probabilité max)
                        class_labels = {
                            "Prob_class_0": "Facture",
                            "Prob_class_1": "ID_Piece",
                            "Prob_class_2": "Resume",
                        }
                        correction_options = list(class_labels.values()) + ["Autre"]  # Ajout de la catégorie "Autre"

                        # Initialiser les corrections dans session_state
                        if f"corrections_{uuid}" not in st.session_state:
                            st.session_state[f"corrections_{uuid}"] = {
                                filename: class_labels.get(pred_class, "Inconnu") for filename, pred_class in zip(filenames, predicted_classes)
                            }

                        # Structure du tableau
                        with st.form(f"form_{uuid}"):
                            st.write("### Tableau des prédictions")
                            col_names = ["Image", "Classe Prédite", "Classe Réelle"]

                            for filename, pred_class in zip(filenames, predicted_classes):
                                predicted_label = class_labels.get(pred_class, "Inconnu")
                                image_path = f"img/{uuid}/original_raw/{filename}"

                                cols = st.columns([3, 2, 2])  # Ajustez les largeurs des colonnes
                                with cols[0]:
                                    if os.path.exists(image_path):
                                        st.image(image_path)
                                    else:
                                        st.error(f"Image introuvable : {image_path}")

                                with cols[1]:
                                    st.markdown(f"**Classe Prédite :** {predicted_label}")

                                with cols[2]:
                                    # ✅ Met à jour `st.session_state` AVANT d'ajouter à `table_data`
                                    st.session_state[f"corrections_{uuid}"][filename] = st.selectbox(
                                        "**Classe réelle :**",
                                        options=correction_options,
                                        index=correction_options.index(st.session_state[f"corrections_{uuid}"][filename]),
                                        key=f"{uuid}_{filename}"
                                    )

                            # ✅ Construire table_data APRÈS que toutes les selectbox aient été mises à jour
                            submitted = st.form_submit_button("Valider les corrections")
                            if submitted:
                                table_data = [
                                    {
                                        "Image": f"img/{uuid}/original_raw/{filename}",
                                        "Classe Prédite": class_labels.get(pred_class, "Inconnu"),
                                        "Classe Réelle": st.session_state[f"corrections_{uuid}"][filename]  # ✅ MAJ après interaction
                                    }
                                    for filename, pred_class in zip(filenames, predicted_classes)
                                ]
                                handle_submit(table_data, uuid)

                    st.write("---")
                else:
                    st.write(f"Prédiction du {date} incluant {n_images} images")
                    st.write(f"Status : {status}")
                    st.write("---")
        else:
            st.warning("Référence invalide")
