import os
import streamlit as st
import json
import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from src.admin.mlflow_tracking import list_mlflow_runs, git_revert_to_commit, save_to_mlflow, register_model, run_command

# Set page configuration
st.set_page_config(
    page_title="ML Image Workflow",
    page_icon=":rocket:",
    layout="wide"
)

# Custom CSS for modern top navigation
st.markdown("""
<style>
.stApp {
    background-color: #f4f4f4;
}
.navigation {
    display: flex;
    justify-content: center;
    gap: 20px;
    padding: 15px;
    background-color: white;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    z-index: 1000;
    margin-top: -20px;
}
.stApp > div:first-child {
    margin-top: 80px;
}
.nav-button {
    padding: 10px 20px;
    border-radius: 8px;
    text-decoration: none;
    color: #333;
    transition: all 0.3s ease;
}
.nav-button:hover {
    background-color: #f0f0f0;
    color: #000;
}
.active-nav-button {
    background-color: #e0e0e0;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# Navigation function
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)


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


def page_select():
    pages = ['Select Images', 'Train', 'ML Flow Runs']

    # Create navigation buttons
    nav_container = st.container()
    with nav_container:
        st.markdown('<div class="navigation">', unsafe_allow_html=True)
        cols = st.columns(len(pages))
        
        for i, page in enumerate(pages):
            with cols[i]:
                # Use st.button with unique key
                if st.button(page, key=f'nav_{page}', use_container_width=True):
                    st.session_state.current_page = page
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Initialise on first page
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'Select Images'

###########################################################################################################################################################################
#                                                                          SELECT IMAGES PAGE                                                                             #
###########################################################################################################################################################################
    if st.session_state.current_page == 'Select Images':
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


###########################################################################################################################################################################
#                                                                               TRAINING PAGE                                                                             #
###########################################################################################################################################################################
    elif st.session_state.current_page == 'Train':
    # Initialize session state for command outputs if not exists
        if 'command_outputs' not in st.session_state:
            st.session_state.command_outputs = []

        # Use column layout to create a main area and an output log area
        main_col, log_col = st.columns([2, 1])

        with main_col:
            
            st.header("Launch a new training")
            
            # DVC and Git commit buttons
            col1, col2 = st.columns(2)

            with col1:
                if st.button("Train Model and save run in MLflow"):
                    # Run DVC reproduce
                    st.write("Training...")
                    dvc_repro_output = run_command("dvc repro --force")
                    st.session_state.command_outputs.append(f"DVC REPRO : {dvc_repro_output}")
                    
                    # Load and display confusion matrix
                    matrix = load_confusion_matrix()
                    scores = load_scores()

                    fig = plot_confusion_matrix(matrix)
                    st.pyplot(fig)
                    st.write(f"Overall Accuracy: {scores['accuracy']:.2%}")

                    # Git add and commit
                    st.write("Running git add...")
                    git_add_output = run_command("git add dvc.lock data/raw_per_classes.dvc")          
                    st.session_state.command_outputs.append(f"GIT ADD : {git_add_output}")

                    st.write("Running git commit...")
                    git_commit_output = run_command('git commit -m "Training completed."')
                    st.session_state.command_outputs.append(f"GIT COMMIT : {git_commit_output}")

                    # Get commit hash
                    commit_hash_output = run_command("git rev-parse HEAD")
                    st.success(f"Commit Hash: {commit_hash_output}")
                    
                    # DVC PUSH
                    st.write("Running dvc push...")
                    dvc_push_output = run_command("dvc push")
                    st.session_state.command_outputs.append(f"DVC PUSH : {dvc_push_output}")
                    st.session_state.commit_hash=commit_hash_output

                    st.write("Saving run in mlflow...")                    
                    st.session_state.run_id = save_to_mlflow(st.session_state.commit_hash)
                    st.success("Successfully saved run in MLFLOW")
            
            with col2:     
                if st.button("Register the model"):
                    if 'run_id' not in st.session_state:
                        st.error("Please train the model first!")
                    else:
                        register_model(st.session_state.run_id)
                        st.success("Successfully registered the model!")
    
        # Log output area on the right
        with log_col:
            st.header("Command Log")
            if 'command_outputs' in st.session_state and st.session_state.command_outputs:
                # Create a scrollable text area with all command outputs
                output_text = "\n".join(st.session_state.command_outputs)
                st.text_area("Command Outputs", value=output_text, height=600, disabled=True)
            else:
                st.write("No commands executed yet.")


###########################################################################################################################################################################
#                                                                                MLFLOW  PAGE                                                                             #
###########################################################################################################################################################################
    elif st.session_state.current_page == 'ML Flow Runs':
        st.header('ML Flow Runs')
        # Placeholder for MLflow run tracking
        runs = list_mlflow_runs()
        display_mlflow_runs(runs)

        

def display_mlflow_runs(runs_df):
    """
    Display MLflow runs with selection and revert functionality
    
    Args:
        runs_df (pd.DataFrame): DataFrame of MLflow runs
    """
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
        
        if st.button(f"Revert to Commit {commit_hash[:7]}", type="primary"):
            success, message = git_revert_to_commit(commit_hash)
            
            if success:
                st.success(f"Successfully reverted to commit {commit_hash}")
                st.balloons()
            else:
                st.error(message)
    
    return edited_df

def main():
    page_select()

if __name__ == "__main__":
    main()