import os
import shutil
import streamlit as st
import subprocess
import json
import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

# Objectif du streamlit

# En option : 
# Sélectionner les images pour l'entrainement. (Directement dans raw per classes)
# Enregistrer avec dvc commit et dvc push et git commit 
# Récupérer le git hash et le stocker dans ML flow run (plus bas)



# 1. Lancer dvc pull et dvc repro pour réentrainer le modèle
# 2. Afficher le résultat
# 3. Proposer à l'admin d'enregistrer ou non

def load_confusion_matrix(file_path='metrics/confusion_matrix.json'):
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    # Convert nested dict to numpy array
    matrix = np.array([[data[str(i)][str(j)] for j in range(3)] for i in range(3)])
    return matrix

def load_scores(file_path='metrics/scores.json'):
    with open(file_path, 'r') as f:
        scores = json.load(f)
    return scores

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

def list_images(directory):
    """List image files in a directory."""
    return [f for f in os.listdir(directory) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]

def delete_image(directory, filename):
    """Delete an image from a specific directory."""
    os.remove(os.path.join(directory, filename))

def run_command(command):
    """Run a shell command and return its output."""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.stdout.strip(), result.stderr.strip()
    except Exception as e:
        return "", str(e)

def main():
    st.set_page_config(layout='wide')
  
    # Initialize session state for command outputs if not exists
    if 'command_outputs' not in st.session_state:
        st.session_state.command_outputs = []

    # Use column layout to create a main area and an output log area
    main_col, log_col = st.columns([3, 1])

    with main_col:
        
    # Initialize session state for command outputs if not exists
    if 'command_outputs' not in st.session_state:
            st.session_state.command_outputs = []
    
        # Use column layout to create a main area and an output log area
        main_col, log_col = st.columns([3, 1])

        with col1:
            if st.button("Train Model (DVC Reproduce)"):
                # Run DVC reproduce
                st.write("Training...")
                dvc_repro_output, dvc_repro_err = run_command("dvc repro")
                st.session_state.command_outputs.append(f"DVC REPRO : {dvc_repro_output}")

        with col2:
            if st.button("Commit Data (DVC & Git)"):         
                # Git add and commit
                git_add_output, git_add_err = run_command("git add dvc.lock")          
                st.session_state.command_outputs.append(f"GIT ADD : {git_add_output}")

                git_commit_output, git_commit_err = run_command('git commit -m "Training completed."')
                st.session_state.command_outputs.append(f"GIT COMMIT : {git_commit_output}")

                # Get commit hash
                commit_hash_output, commit_hash_err = run_command("git rev-parse HEAD")
                st.success(f"Commit Hash: {commit_hash_output}")
        
        with col3:
            if st.button("Save run in MLflow"):         
                # Git add and commit
                st.write("to implement")

        st.header("""
                  1. Train : afficher les métriques et la matrice de confusion
                  2. Sortir l'enregistrement du run MLflow de EVAL et le mettre ici : enregistrer le commit hash dans les artefacts
                  3. Ajouter un bouton "Save model in registry and promote"
                  4. Lister les experiences MLflow et pouvoir sélectionner un hash et revenir à l'état de ces données.
        """)
        with col1:
            if st.button("Train Model (DVC Reproduce)"):
                # Run DVC reproduce
                st.write("Training...")
                dvc_repro_output, dvc_repro_err = run_command("dvc repro")
                st.session_state.command_outputs.append(f"DVC REPRO : {dvc_repro_output}")
                
                # Load and display confusion matrix
                matrix = load_confusion_matrix()
                scores = load_scores()

                fig = plot_confusion_matrix(matrix)
                st.pyplot(fig)
                st.write(f"Overall Accuracy: {scores['accuracy']:.2%}")

        with col2:
            if st.button("Commit Data (DVC & Git)"):         
                # Git add and commit
                git_add_output, git_add_err = run_command("git add dvc.lock")          
                st.session_state.command_outputs.append(f"GIT ADD : {git_add_output}")

                git_commit_output, git_commit_err = run_command('git commit -m "Training completed."')
                st.session_state.command_outputs.append(f"GIT COMMIT : {git_commit_output}")

                # Get commit hash
                commit_hash_output, commit_hash_err = run_command("git rev-parse HEAD")
                st.success(f"Commit Hash: {commit_hash_output}")

                

        
        with col3:
            if st.button("Save run in MLflow"):         
                # Git add and commit
                st.write("to implement")

        st.header("""
                  2. Sortir l'enregistrement du run MLflow de EVAL et le mettre ici : enregistrer le commit hash dans les artefacts
                  3. Ajouter un bouton "Save model in registry and promote"
                  4. Lister les experiences MLflow et pouvoir sélectionner un hash et revenir à l'état de ces données.
        """)

        st.header("Select images for training")
        
        # Directory selection
        selected_dir = st.selectbox("Select Directory", 
            [f"data/raw_per_classes/{i}" for i in range(3)])
        
        
        # Image upload section
        uploaded_files = st.file_uploader("Upload Images", accept_multiple_files=True, type=['png', 'jpg', 'jpeg', 'gif', 'bmp'])
        

        # Upload images if files are selected
        if uploaded_files:
            for uploaded_file in uploaded_files:
                file_path = os.path.join(selected_dir, uploaded_file.name)
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
            st.sidebar.success(f"Uploaded {len(uploaded_files)} file(s) to {selected_dir}")
        
        # Display and manage images
        st.header(f"Images in {selected_dir}")
        images = list_images(selected_dir)
        
        # Image grid
        cols = st.columns(6)
        for i, image in enumerate(images):
            with cols[i % 6]:
                img_path = os.path.join(selected_dir, image)
                st.image(img_path, width=200)
                
                # Delete button for each image
                if st.button(f"Delete {image}", key=f"delete_{selected_dir}_{image}"):
                    delete_image(selected_dir, image)
                    st.rerun()
        
   
    # Log output area on the right
    with log_col:
        st.header("Command Log")
        if 'command_outputs' in st.session_state and st.session_state.command_outputs:
            # Create a scrollable text area with all command outputs
            output_text = "\n".join(st.session_state.command_outputs)
            st.text_area("Command Outputs", value=output_text, height=600, disabled=True)
        else:
            st.write("No commands executed yet.")

if __name__ == "__main__":
    main()