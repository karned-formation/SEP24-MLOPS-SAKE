import os
import base64
import streamlit as st
import requests

endpoint_url = os.getenv('URL_BACKEND') + '/predict'
st.title("Classification de documents")

reference = st.text_input("Votre référence")
uploaded_files = st.file_uploader("Documents", accept_multiple_files=True)

if st.button("Traiter"):
    if reference and uploaded_files:
        files_base64 = []
        for uploaded_file in uploaded_files:
            file_content = uploaded_file.read()
            encoded_string = base64.b64encode(file_content).decode('utf-8')
            files_base64.append(encoded_string)

        data_dict = {
            "reference": reference,
            "files": files_base64
        }

        with st.spinner("Conversion et envoi des données..."):
            headers = {'Content-Type': 'application/json'}
            response = requests.post(endpoint_url, json=data_dict, headers=headers)

        if response.status_code == 200:
            st.success(f"Réponse du serveur : {response.text}")
        else:
            st.error(f"Erreur {response.status_code} : {response.text}")
    else:
        st.warning("Veuillez entrer une référence et sélectionner au moins un fichier.")