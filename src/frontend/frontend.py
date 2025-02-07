import os
import streamlit as st
import requests

endpoint_url = 'http://localhost:8908/predict'

st.title("Classification de documents")
reference = st.text_input("Votre référence")
uploaded_files = st.file_uploader("Documents", accept_multiple_files = True)

if st.button("Traiter"):
    if reference and uploaded_files:
        files = []
        for uploaded_file in uploaded_files:
            files.append(("files", (uploaded_file.name, uploaded_file, uploaded_file.type)))

        data = {"reference": reference}

        with st.spinner("Envoi des données..."):
            response = requests.post(
                url=endpoint_url,
                data = data,
                files = files
            )

        if response.status_code == 200:
            st.success(f"Réponse du serveur : {response.text}")
        else:
            st.error(f"Erreur {response.status_code} : {response.text}")
    else:
        st.warning("Veuillez entrer une référence et sélectionner au moins un fichier.")
