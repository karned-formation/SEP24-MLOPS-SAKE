import streamlit as st
import requests
import os
from PIL import Image
import io

API_URL = "http://localhost:8000"

def main():
    st.title("ML Training System")
    
    # Sidebar for navigation
    page = st.sidebar.selectbox("Choose a page", ["Image Management", "Training", "Model Management"])
    
    if page == "Image Management":
        show_image_management()
    elif page == "Training":
        show_training_page()
    else:
        show_model_management()

def show_image_management():
    st.header("Image Management")
    
    # Get folders and images
    response = requests.get(f"{API_URL}/get_images")
    if response.status_code == 200:
        folders_data = response.json()
        
        # Select folder
        folder = st.selectbox("Select Folder", list(folders_data.keys()))
        
        # Display images in grid
        if folder in folders_data:
            cols = st.columns(4)
            for idx, img_data in enumerate(folders_data[folder]):
                with cols[idx % 4]:
                    st.image(img_data["thumbnail"], caption=img_data["name"])
                    if st.button(f"Delete {img_data['name']}", key=f"del_{folder}_{idx}"):
                        delete_image(folder, img_data["name"])
        
        # Upload new images
        uploaded_file = st.file_uploader(f"Add image to {folder}", type=["jpg", "png"])
        if uploaded_file:
            add_image(folder, uploaded_file)

def show_training_page():
    st.header("Training Management")
    
    # Display MLflow runs
    response = requests.get(f"{API_URL}/getmlflowruns")
    if response.status_code == 200:
        runs = response.json()
        st.table(runs)
    
    # Training button
    if st.button("Start Training"):
        with st.spinner("Training in progress..."):
            response = requests.post(f"{API_URL}/train")
            if response.status_code == 200:
                st.success("Training completed!")
            else:
                st.error("Training failed!")

def show_model_management():
    st.header("Model Management")
    
    # Model registration
    if st.button("Register Current Model to S3"):
        with st.spinner("Registering model..."):
            response = requests.post(f"{API_URL}/registermodel")
            if response.status_code == 200:
                st.success("Model registered successfully!")
            else:
                st.error("Model registration failed!")
    
    # Git revert
    commit_hash = st.text_input("Enter commit hash to revert to:")
    if commit_hash and st.button("Revert to Commit"):
        response = requests.post(f"{API_URL}/reverttocommit", json={"commit_hash": commit_hash})
        if response.status_code == 200:
            st.success("Successfully reverted to specified commit!")
        else:
            st.error("Revert failed!")

def delete_image(folder, image_name):
    response = requests.post(f"{API_URL}/deleteimage", json={
        "folder": folder,
        "image_name": image_name
    })
    if response.status_code == 200:
        st.success(f"Deleted {image_name}")
        st.rerun()
    else:
        st.error("Failed to delete image")

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

if __name__ == "__main__":
    main()