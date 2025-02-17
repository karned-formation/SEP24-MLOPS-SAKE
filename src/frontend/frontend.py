import os
import streamlit as st
import requests
from src.utils.files import encode_files


endpoint_url = os.getenv('URL_BACKEND') + '/predict'

st.title("Classification de documents")
reference = st.text_input("Votre référence")
uploaded_files = st.file_uploader("Documents", accept_multiple_files = True)

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

        if response.status_code == 200:
            st.success(f"Réponse du serveur : {response.text}")
        else:
            st.error(f"Erreur {response.status_code} : {response.text}")
    else:
        st.warning("Veuillez entrer une référence et sélectionner au moins un fichier.")
