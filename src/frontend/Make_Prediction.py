# Classifier des images
import streamlit as st
import requests

endpoint_url = 'http://localhost:8908/predict'

st.set_page_config(
    page_title="Images Classification  App",  # Title of the page in the browser tab and left panel
    page_icon="📊",  # Optional: Emoji or icon for the page
)
st.title("Classification de documents")
reference = st.text_input("Votre référence")
uploaded_files = st.file_uploader("Documents", accept_multiple_files=True)

if st.button("Traiter"):
    if reference and uploaded_files:
        files = []
        for uploaded_file in uploaded_files:
            files.append(("files", (uploaded_file.name, uploaded_file, uploaded_file.type)))

        data = {"reference": reference}

        with st.spinner("Envoi des données..."):
            response = requests.post(endpoint_url, data=data, files=files)

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
