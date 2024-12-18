import streamlit as st
import requests
from datetime import datetime
import json
import pandas as pd

uuid = "blablabla"

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
    df = df.reset_index()
    df.rename(columns={'index': 'filename'}, inplace=True)
    return df

def parse_response(pred):
    timestamp = pred['metadata']['time']
    date = convert_timestamp(timestamp)
    n_images = pred['metadata']['n_files']
    status = pred['status']
    prediction = process_prediction_dataframe(pred['prediction']) if status == 'COMPLETED' else None
    return date, n_images, status, prediction



st.title("Afficher les prédictions")

reference = st.text_input("Entrez une référence pour récupérer les prédictions:")

if st.button("Display Predictions"):
    if reference:
        endpoint_url = f'http://localhost:8908/predict/{reference}'
        with st.spinner("Récupération des prédictions..."):
            response = requests.get(endpoint_url)

        if response.status_code != 200:
            st.error(f"Erreur {response.status_code} : {response.text}")
        else:
            predictions = response.json()
            if st.button("Display raw response"):
                st.code(json.dumps(predictions, indent=2), language="json", line_numbers=True)
            predictions = sorted(predictions, key=lambda x: x['metadata']['time'], reverse=True)
            for pred in predictions:
                date, n_images, status, prediction = parse_response(pred)
                if status == 'COMPLETED':
                    st.write(f"Prédiction du **{date}**")
                    st.markdown(f"""
                                - **Status :** {status}
                                - **Nombre de fichiers :** {n_images}
                                - **uuid :** {uuid}
                                """)
                    st.dataframe(prediction, hide_index=True)
                else:
                    st.write(f"Prédiction du {date} incluant {n_images} images")
                    st.write(f"Status : {status}")
                st.write("---")

            st.subheader("Prédictions :")
            if isinstance(preds, list):
                for i, pred in enumerate(preds, start=1):
                    st.write(f"{i}. {pred}")
            else:
                st.write(preds)
    else:
        st.warning("Veuillez entrer une référence.")
