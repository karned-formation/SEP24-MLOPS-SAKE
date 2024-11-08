from pathlib import Path
import shutil

def load_env_file(filepath):
    env_vars = {}
    with open(filepath, 'r') as file:
        for line in file:
            # Ignore les lignes vides et les commentaires
            if line.strip() and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                env_vars[key] = value
    return env_vars

def save_env_file(filepath, env_vars):
    with open(filepath, 'w') as file:
        for key, value in env_vars.items():
            file.write(f"{key}={value}\n")

env_path = Path(".env")
env_original_path = Path(".env_original")
env_mlops_path = Path(".env_mlops_sake")

if not env_original_path.exists():
    shutil.copy(env_path, env_original_path)
    print(f"Copie de sauvegarde créée : {env_original_path}")

env_original_vars = load_env_file(env_original_path)
env_mlops_vars = load_env_file(env_mlops_path)

# Mettre à jour env_original_vars avec les valeurs de env_mlops_vars sans redondance
env_original_vars.update(env_mlops_vars)

save_env_file(env_path, env_original_vars)

print("Le fichier .env a été mis à jour avec le contenu fusionné de .env_original et .env_mlops_sake.")
