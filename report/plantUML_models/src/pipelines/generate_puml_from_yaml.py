import yaml

# Lire le fichier de configuration YAML
with open("../../../../src/config.yaml", "r") as f:
    config = yaml.safe_load(f)

# Générer un fichier PlantUML avec les variables injectées
with open("output.puml", "w") as f:
    f.write(f"""
@startuml
[{config['data_ingestion']['processed_dir']}] --> [{config['data_ingestion']['raw_dataset_path']}]
@enduml
""")
