import json
import streamlit as st
import requests
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from urllib.parse import quote

# Set page configuration
st.set_page_config(
    page_title="ML Image Workflow",
    page_icon=":rocket:",
    layout="wide"
)

API_URL = "http://localhost:8910"

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
    
    # Get folders and images
    response = requests.get(f"{API_URL}/get_images")
    if response.status_code == 200:
        folders_data = response.json()
        
        # Select folder
        folder = st.selectbox("Select Folder", list(folders_data.keys()))
        
        # Upload new images
        uploaded_file = st.file_uploader(f"Add image to {folder}", type=["jpg", "png"])
        if uploaded_file:
            add_image(folder, uploaded_file)

        # Display images in grid
        if folder in folders_data:
            cols = st.columns(6)
            for idx, img_data in enumerate(folders_data[folder]):
                with cols[idx % 6]:
                    st.image(img_data["thumbnail"], caption=img_data["name"])
                    if st.button(f"Delete {img_data['name']}", key=f"del_{folder}_{idx}"):
                        delete_image(folder, img_data["name"])
        

def show_training_page():
    st.header("Training Management")
        
    # Training button
    if st.button("Start Training"):
        with st.spinner("Training in progress..."):
            response = requests.post(f"{API_URL}/train")
            if response.status_code == 200:
                st.success("Training completed!")
            else:
                st.error("Training failed!")

    # Model registration
    if st.button("Register Current Model to S3"):
        with st.spinner("Registering model..."):
            response = requests.post(f"{API_URL}/registermodel")
            if response.status_code == 200:
                st.success("Model registered successfully!")
            else:
                st.error("Model registration failed!")


def show_version_management():
    st.header("Version Management")

    # Display MLflow runs
    response = requests.get(f"{API_URL}/getmlflowruns")
    if response.status_code == 200:
        runs = response.json()
        df = pd.DataFrame(json.loads(runs))
        display_mlflow_runs(df)

def display_mlflow_runs(runs_df):
    """
    Display MLflow runs with selection and revert functionality
    
    Args:
        runs_df (pd.DataFrame): DataFrame of MLflow runs
    """
    runs_df['start_time'] = pd.to_datetime(runs_df['start_time'], unit='ms')
    runs_df['end_time'] = pd.to_datetime(runs_df['end_time'], unit='ms')

    # Add a selection column
    runs_df['Select'] = False
    
    # Display the dataframe with selection
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
            'tags.mlflow.runName', 
            'start_time', 
            'end_time', 
            'status', 
            'metrics.accuracy', 
            'metrics.f1_score', 
            'tags.commit_hash'
        ],
        hide_index=True
    )
    
    # Count selected runs
    selected_runs = edited_df[edited_df['Select']]
    
    # Validate selection
    if len(selected_runs) > 1:
        st.warning("Please select only one run.")
    
    # Revert button
    if len(selected_runs) == 1:
        selected_run = selected_runs.iloc[0]
        commit_hash = selected_run['commit_hash']
        encoded_url = f"{API_URL}/reverttocommit?commit_hash={quote(commit_hash)}"
        if st.button(f"Revert to Commit {commit_hash[:7]}", type="primary"):
            response = requests.post(encoded_url)
            if response.status_code == 200:
                st.success("Successfully reverted to specified commit!")
                st.balloons()
            else:
                st.error("Revert failed!")
    
    return edited_df
    

def delete_image(folder, image_name):
    headers = {"Content-Type": "application/json"}  # Retain headers if required
    # Construct the query parameters
    query_params = {
        "folder": folder,
        "image_name": image_name
    }
    # Encode query parameters into the URL
    encoded_url = f"{API_URL}/deleteimage?folder={quote(folder)}&image_name={quote(image_name)}"

    try:
        response = requests.post(encoded_url, headers=headers)
        
        if response.status_code == 200:
            st.success(f"Deleted {image_name}")
            st.rerun()
        else:
            # Log full response details for debugging
            st.error(f"Failed to delete image: {image_name}")
            st.error(f"Response status: {response.status_code}")
            st.error(f"Response body: {response.text}")
    
    except requests.RequestException as e:
        # Handle connection errors
        st.error(f"Request failed: {e}")

def add_image(folder, file):
    files = {"file": file}
    response = requests.post(
        f"{API_URL}/addimage",
        files=files,
        data={"folder": folder}
    )
    if response.status_code == 200:
        st.success("Image uploaded successfully!")
        st.rerun()
    else:
        st.error("Failed to upload image")


def plot_confusion_matrix(matrix):
    plt.figure(figsize=(8, 6))
    sns.heatmap(matrix, annot=True, cmap='Blues', fmt='d', 
                xticklabels=['Facture', 'Identité', 'CV'],
                yticklabels=['Facture', 'Identité', 'CV'],
                annot_kws={"fontsize":30})
    plt.title('Confusion Matrix', fontsize=30)
    plt.xlabel('Predicted', fontsize=12)
    plt.ylabel('Actual', fontsize=12)
    plt.xticks(fontsize=20)
    plt.yticks(fontsize=20)
    return plt





if __name__ == "__main__":
    main()
