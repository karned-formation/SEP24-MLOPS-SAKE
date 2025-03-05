import streamlit as st
import requests
import os
from src.utils.files import encode_files

KEYCLOAK_SERVER_URL = os.environ.get("KEYCLOAK_SERVER_URL")
KEYCLOAK_REALM_NAME = os.environ.get("KEYCLOAK_REALM_NAME")
KEYCLOAK_CLIENT_ID = os.environ.get("KEYCLOAK_CLIENT_ID")
KEYCLOAK_CLIENT_SECRET = os.environ.get("KEYCLOAK_CLIENT_SECRET")

# 🔹 Configuration de la page
st.set_page_config(page_title="Analyse des Prédictions", layout="centered")

def main():
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
                headers = {
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {st.session_state.access_token}'
                }
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


if "access_token" not in st.session_state:
    st.session_state.access_token = None
    st.session_state.user_info = None

def get_token( username, password ):
    url = f"{KEYCLOAK_SERVER_URL}/realms/{KEYCLOAK_REALM_NAME}/protocol/openid-connect/token"
    data = {
        "grant_type": "password",
        "client_id": KEYCLOAK_CLIENT_ID,
        "client_secret": KEYCLOAK_CLIENT_SECRET,
        "username": username,
        "password": password
    }
    response = requests.post(url, data=data)
    if response.status_code == 200:
        return response.json()
    else:
        return None

if st.session_state.access_token:
    if st.button("Se déconnecter"):
        st.session_state.access_token = None
        st.rerun()

    main()
else:
    st.subheader("🔒 Veuillez vous connecter")

    username = st.text_input("Nom d'utilisateur", value="", placeholder="Entrez votre identifiant")
    password = st.text_input("Mot de passe", type="password", placeholder="Entrez votre mot de passe")

    if st.button("Se connecter"):
        token_data = get_token(username, password)
        if token_data:
            st.session_state.access_token = token_data["access_token"]
            st.success("✅ Connexion réussie !")
            st.rerun()
        else:
            st.error("❌ Identifiants incorrects !")