import streamlit as st
import requests
import os
from src.utils.files import encode_files

endpoint_url = os.getenv('URL_BACKEND') + '/predict'

st.set_page_config(
    page_title="Images Classification App",  # Title of the page in the browser tab and left panel
    page_icon="📊",  # Optional: Emoji or icon for the page
)
st.title("Classification de documents")
reference = st.text_input("Votre référence")
uploaded_files = st.file_uploader("Documents", accept_multiple_files=True)

if st.button("Traiter"):
    if reference and uploaded_files:
        files = []
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

        # Check if the response is JSON and parse it
        try:
            r = response.json()
        except ValueError:
            st.error("La réponse du serveur n'est pas au format JSON.")
            st.stop()

        ref_is_unique = r['message'] != "Reference should be unique. Try again."

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
