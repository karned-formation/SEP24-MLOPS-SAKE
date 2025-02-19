import streamlit as st
import requests
import os
from src.utils.files import encode_files

# 🔹 Configuration de la page
st.set_page_config(page_title="Analyse des Prédictions", layout="centered")

# 🔹 Menu de navigation
st.sidebar.title("Navigation")
st.sidebar.page_link("app.py", label="📤 Déposer & Classifier")
st.sidebar.page_link("pages/feedback.py", label="📊 Vérifier & Corriger")



# 🔹 Chargement de l'URL Backend depuis les variables d'environnement
endpoint_url = os.getenv('URL_BACKEND')
if not endpoint_url:
    st.error("L'URL du backend n'est pas définie. Vérifiez vos variables d'environnement.")
    st.stop()
endpoint_url += '/predict'

# 🔹 Titre principal
st.title("Classification de documents image")

# 🔹 Entrée utilisateur
reference = st.text_input("Votre référence")
uploaded_files = st.file_uploader("Documents", accept_multiple_files=True)

# 🔹 Bouton pour traiter les fichiers
if st.button("Traiter"):
    if reference and uploaded_files:
        data_dict = {
            "reference": reference,
            "files": encode_files(uploaded_files)
        }

        with st.spinner("Envoi des données..."):
            headers = {'Content-Type': 'application/json'}
            response = requests.post(
                url=endpoint_url,
                json=data_dict,
                headers=headers
            )

        # Vérification de la réponse JSON
        try:
            r = response.json()
        except ValueError:
            st.error("La réponse du serveur n'est pas au format JSON.")
            st.stop()

        # Vérification de l'unicité de la référence
        ref_is_unique = r.get('message') != "Reference should be unique. Try again."

        if response.status_code != 200:
            st.error(f"Erreur {response.status_code} : {response.text}")
        elif ref_is_unique:
            st.success(
                f"Référence : {r['reference']} \n\n"
                f"UUID : {r['uuid']} \n\n"
                f"Message : {r['message']} \n\n"
                f"Raw : {r}"
            )
        else:
            st.error("La référence doit être unique.")
    else:
        st.warning("Veuillez entrer une référence et sélectionner au moins un fichier.")