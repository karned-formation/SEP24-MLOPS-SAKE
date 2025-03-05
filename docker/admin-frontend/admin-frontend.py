import json
import streamlit as st
import requests
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from urllib.parse import quote
import os
from streamlit_extras.let_it_rain import rain
from streamlit_extras.stylable_container import stylable_container

# Set page configuration
st.set_page_config(
    page_title="ML Image Workflow",
    page_icon=":rocket:",
    layout="wide"
)

BACKEND_URL = os.getenv("ADMIN_BACKEND_URL", "http://admin-backend-service")

# Handle session state
if "selected_folder" not in st.session_state:
    st.session_state.selected_folder = None

if "training_result" not in st.session_state:
    st.session_state.training_result = None

if 'training_status' not in st.session_state:
    st.session_state.training_status = None

if 'mlflow_runs' not in st.session_state:
    st.session_state.mlflow_runs = None

if 'selected_runs' not in st.session_state:
    st.session_state.selected_runs = pd.DataFrame()


def main():    
    # Sidebar for navigation
    page = st.sidebar.selectbox("Choose a page", ['Select Images', 'Train', 'ML Flow Runs'])
    
    if page == "Select Images":
        show_image_management()
    elif page == "Train":
        show_training_page()
    else:
        show_version_management()

def show_image_management():
    st.header("Image Management")
    
    response = requests.get(f"{BACKEND_URL}/get_images")
    if response.status_code == 200:
        st.session_state.folders_data = response.json()
    
    if "folders_data" in st.session_state:
        folder = st.selectbox("Select Folder", list(st.session_state.folders_data.keys()),
                              index=list(st.session_state.folders_data.keys()).index(st.session_state.selected_folder) if st.session_state.selected_folder in st.session_state.folders_data else 0)
        st.session_state.selected_folder = folder
        
        uploaded_file = st.file_uploader(f"Add image to {folder}", type=["jpg", "png"])
        if uploaded_file:
            add_image(folder, uploaded_file)
        with stylable_container(key="button", css_styles="""
                   button { 
                        background-color: #0000ff; 
                        color: white;
                    }
                    """):
            if st.button("Retrieve images from feedbacks"):
                response = requests.get(f"{BACKEND_URL}/get_predictions_images")
                if response.status_code == 200:
                    st.success("Images added to training set!")
                else:
                    st.error("Retrieval failed!")

        if folder in st.session_state.folders_data:
            cols = st.columns(6)
            for idx, img_data in enumerate(st.session_state.folders_data[folder]):
                with cols[idx % 6]:
                    st.image(img_data["thumbnail"], caption=img_data["name"])
                    if st.button(f"Delete {img_data['name']}", key=f"del_{folder}_{idx}"):
                        delete_image(folder, img_data["name"])
        


def show_training_page():
    st.header("Training Management")
    
    if st.button("Start Training"):
        with st.spinner("Training in progress..."):
            response = requests.post(f"{BACKEND_URL}/train")
            if response.status_code == 200:
                st.session_state.training_result = json.loads(response.content)
                st.success("Training completed!")
                rain(emoji="🎉", font_size=60, falling_speed=5, animation_length=5)
            else:
                st.error("Training failed!")
    
    if st.session_state.training_result:
        result = st.session_state.training_result
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.subheader("Scores")
            scores = json.loads(result['scores'].replace("'", '"'))
            st.write(f"Overall Accuracy: {scores['accuracy']:.2%}")
            st.write(f"Overall f1 score: {scores['avg_f1']:.2%}")
            st.write(f"Overall Recall: {scores['avg_rec']:.2%}")
        
        with col2:
            matrix_dict = json.loads(result['confusion_matrix'].replace("'", '"'))
            matrix = pd.DataFrame.from_dict(matrix_dict)
            fig = plt.figure(figsize=(5,4))
            sns.heatmap(matrix, annot=True, cmap='Blues', fmt='d', 
                        xticklabels=['Facture', 'Identité', 'CV'],
                        yticklabels=['Facture', 'Identité', 'CV'],
                        annot_kws={"fontsize":16})
            plt.title('Confusion Matrix', fontsize=18)
            st.pyplot(fig)
    
    if st.button("Register Current Model to S3"):
        with st.spinner("Registering model..."):
            response = requests.post(f"{BACKEND_URL}/registermodel")
            if response.status_code == 200:
                st.success("Model registered successfully!")
            else:
                st.error("Model registration failed!")

def show_version_management():
    st.header("Version Management")
    response = requests.get(f"{BACKEND_URL}/getmlflowruns")
    if response.status_code == 200:
        st.session_state.mlflow_runs = pd.DataFrame(json.loads(response.json()))
    
    if st.session_state.mlflow_runs is not None:
        st.session_state.selected_runs = display_mlflow_runs(st.session_state.mlflow_runs)
    
    if st.button("Register Current Model to S3"):
        with st.spinner("Registering model..."):
            response = requests.post(f"{BACKEND_URL}/registermodel")
            if response.status_code == 200:
                st.success("Model registered successfully!")
            else:
                st.error("Model registration failed!")

def display_mlflow_runs(runs_df):
    runs_df['start_time'] = pd.to_datetime(runs_df['start_time'], unit='ms')
    runs_df['end_time'] = pd.to_datetime(runs_df['end_time'], unit='ms')
    runs_df['Select'] = False
    
    if not st.session_state.selected_runs.empty:
        runs_df.update(st.session_state.selected_runs)
    
    edited_df = st.data_editor(
        runs_df, 
        column_config={
            'Select': st.column_config.CheckboxColumn(
                "Select Run",
                help="Select one run to revert to",
                default=False
            )
        },
        disabled=[
            'tags.mlflow.runName', 'start_time', 'end_time', 'status', 
            'metrics.accuracy', 'metrics.f1_score', 'tags.commit_hash'
        ],
        hide_index=True
    )
    
    selected_runs = edited_df[edited_df['Select']]
    st.session_state.selected_runs = selected_runs
    
    if len(selected_runs) > 1:
        st.warning("Please select only one run.")
    
    if len(selected_runs) == 1:
        selected_run = selected_runs.iloc[0]
        commit_hash = selected_run['commit_hash']
        encoded_url = f"{BACKEND_URL}/reverttocommit?commit_hash={quote(commit_hash)}"
        if st.button(f"Revert to Commit {commit_hash[:7]}", type="primary"):
            response = requests.post(encoded_url)
            if response.status_code == 200:
                st.success("Successfully reverted to specified commit!")
                st.balloons()
            else:
                st.error("Revert failed!")
    
    return edited_df
    

def delete_image(folder, image_name):
    encoded_url = f"{BACKEND_URL}/deleteimage?folder={quote(folder)}&image_name={quote(image_name)}"
    try:
        response = requests.post(encoded_url)
        if response.status_code == 200:
            st.success(f"Deleted {image_name}")
            st.rerun()
        else:
            st.error(f"Failed to delete {image_name}")
    except requests.RequestException as e:
        st.error(f"Request failed: {e}")

def add_image(folder, file):
    response = requests.post(f"{BACKEND_URL}/addimage", files={"file": file}, data={"folder": folder})
    if response.status_code == 200:
        st.success("Image uploaded successfully!")

        # Update session state, no manual rerun
        response = requests.get(f"{BACKEND_URL}/get_images")
        if response.status_code == 200:
            st.session_state.folders_data = response.json()
    else:
        st.error("Failed to upload image")


if __name__ == "__main__":
    main()