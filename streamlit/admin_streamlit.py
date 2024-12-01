import os
import shutil
import streamlit as st
import subprocess

# Objectif du streamlit

# En option : 
# Sélectionner les images pour l'entrainement. (Directement dans raw per classes)
# Enregistrer avec dvc commit et dvc push et git commit 
# Récupérer le git hash et le stocker dans ML flow run (plus bas)



# 1. Lancer dvc pull et dvc repro pour réentrainer le modèle
# 2. Afficher le résultat
# 3. Proposer à l'admin d'enregistrer ou non


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
        
        st.header("Launch a new training")
        
        # DVC and Git commit buttons
        col1, col2, col3 = st.columns(3)

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