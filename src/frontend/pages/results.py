# TEST
import streamlit as st
import requests
from datetime import datetime
import json
import pandas as pd

st.set_page_config(page_title="Dashboard Page")

def convert_timestamp(timestamp):
    # Définir la langue pour les dates en français
    timestamp = float(timestamp)
    dt_object = datetime.fromtimestamp(timestamp)
    # Formater la date et l'heure
    formatted_date = dt_object.strftime("%d %B %Y à %Hh%M")
    return formatted_date

def process_prediction_dataframe(prediction):
    prediction = json.loads(prediction)
    df = pd.DataFrame(prediction).T
    df.index = df.index.str.split("/").str[-1]
    df.index.name = 'Filename'
    # df = df.reset_index()
    # df.rename(columns={'index': 'filename'}, inplace=True)
    return df

def parse_response(pred):
    timestamp = pred['metadata']['time']
    date = convert_timestamp(timestamp)
    n_images = pred['metadata']['n_files']
    status = pred['status']
    uuid = pred['metadata']['uuid']
    prediction = process_prediction_dataframe(pred['prediction']) if status == 'COMPLETED' else None
    return date, n_images, status, uuid, prediction



st.title("Afficher les prédictions")

reference = st.text_input("Entrez une référence pour récupérer les prédictions:")
if st.button("Affichage des prédictions"):
    if reference:
        endpoint_url = f'http://localhost:8908/predict/{reference}'

        with st.spinner("Récupération des prédictions..."):
            response = requests.get(endpoint_url)

        if response.status_code != 200:
            st.error(f"Erreur {response.status_code} : {response.text}")
        else:
            if len(response.json()):
                with st.expander("View JSON Response", expanded=False, icon=":material/file_json:"):
                    st.json(response.json())
                st.write("---")
                # st.subheader("Prédictions :")
                predictions = sorted(response.json(), key=lambda x: x['metadata']['time'], reverse=True)
                for pred in predictions:
                    date, n_images, status, uuid, prediction = parse_response(pred)
                    if status == 'COMPLETED':
                        st.write(f"Prédiction du **{date}**")
                        st.markdown(f"""
                                    - **Status :** {status}
                                    - **Nombre de fichiers :** {n_images}
                                    - **uuid :** {uuid}
                                    """)
                        # st.dataframe(prediction, hide_index=False, use_container_width=True)
                        st.dataframe(
                            prediction.style\
                            .format("{:.2%}")\
                            .highlight_max(axis=1, color='green'),
                            hide_index=False, 
                            use_container_width=True,
                            column_config={
                                    "Prob_class_0": st.column_config.NumberColumn(
                                        "Probabilité Facture",
                                    ),
                                    "Prob_class_1": st.column_config.NumberColumn(
                                        "Probabilité ID_Piece",
                                    ),
                                    "Prob_class_2": st.column_config.NumberColumn(
                                        "Probabilité Resume",
                                    ),
                                },
                        )
                    else:
                        st.write(f"Prédiction du {date} incluant {n_images} images")
                        st.write(f"Status : {status}")
                    st.write("---")
            else:
                st.warning("Référence invalide")

    else:
        st.warning("Veuillez entrer une référence.")
