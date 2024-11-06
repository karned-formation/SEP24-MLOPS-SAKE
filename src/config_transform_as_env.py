import yaml
import os
import re

def flatten_dict(d, parent_key='', sep='_'):
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key.upper(), v))
    return dict(items)

def transform_YAML_as_Environnement_variable(param_yaml_path, 
                                             env_path):

    # Charger le fichier YAML et aplatir la structure
    with open(param_yaml_path, "r") as file:
        params = yaml.safe_load(file)
        flat_params = flatten_dict(params)

    # Substituer les variables utilisant la syntaxe `${data_ingestion.ocr_port}`
    pattern = re.compile(r'\$\{([a-zA-Z0-9_]+)\.([a-zA-Z0-9_]+)\}')

    for key, value in flat_params.items():
        if isinstance(value, str) and "${" in value:
            matches = pattern.findall(value)
            for match in matches:
                group, var = match
                lookup_key = f"{group.upper()}_{var.upper()}"
                if lookup_key in flat_params:
                    value = value.replace(f"${{{group}.{var}}}", str(flat_params[lookup_key]))
            flat_params[key] = value

    print("Les variables d'environnement suivantes sont déclarées")
    with open(env_path, "w") as env_file:
        env_file.write("\n# Variables d'environnement pour le projet MLOps-SAKE\n")
        for key, value in flat_params.items():
            env_file.write(f"{key}={value}\n")
            print(f"{key}={value}")

    print("\nAjout des 2 variables (pour définir le propriétaire hôte des volumes partagés):")
    uid = os.getuid()
    gid = os.getgid()
    with open(env_path, "a") as env_file:
        env_file.write("# Ajout des 2 variables (pour définir le propriétaire hôte des volumes partagés):\n")
        env_file.write(f"UID={uid}\n")
        env_file.write(f"GID={gid}\n")
        print(f"UID={uid}")
        print(f"GID={gid}")

    print(f"=> Le fichier '{env_path}' contient toutes ces variables d'environnement")


    print("\nCréer les répertoires suivants si nécessaire:")
    for key, path in flat_params.items():
        if key.endswith('_DIR') and isinstance(path, str):
            os.makedirs(path, exist_ok=True)
            print(f"{path}")

if __name__ == "__main__":
    param_yaml_path = './params.yaml'
    env_path = './.env_mlops_sake'
    transform_YAML_as_Environnement_variable(param_yaml_path, 
                                             env_path)
    
