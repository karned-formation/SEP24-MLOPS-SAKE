import boto3
import csv
import os
from src.custom_logger import logger


def get_env_var(name):
    value = os.getenv(name)
    if not value:
        raise EnvironmentError(f"La variable d'environnement '{name}' n'est pas définie ou est vide.")
    return value

BUCKET_NAME = get_env_var("AWS_BUCKET_NAME")
CSV_PREFIX = "feedback.csv"  
LOCAL_CSV_DIR = "csv_files"  # Temp folder for CSV files
BASE_OUTPUT_DIR = "data/raw_per_classes"

# Mapping categories to folders
CLASS_MAPPING = {
    "Resume": "2",
    "Facture": "0",
    "ID_Piece": "1"
}


def get_images_pred():
    try:
        # Initialize S3 client
        s3 = boto3.client("s3")

        # Ensure local directories exist
        os.makedirs(LOCAL_CSV_DIR, exist_ok=True)
        for folder in CLASS_MAPPING.values():
            os.makedirs(os.path.join(BASE_OUTPUT_DIR, folder), exist_ok=True)

        # List all feedback.csv files
        response = s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix="")
        csv_files = [obj["Key"] for obj in response.get("Contents", []) if CSV_PREFIX in obj["Key"]]

        print(f"Found {len(csv_files)} CSV files.")

        # For each feedback CSV file
        for csv_file in csv_files:
            local_csv_path = os.path.join(LOCAL_CSV_DIR, os.path.basename(csv_file))
            
            # Download the CSV
            s3.download_file(BUCKET_NAME, csv_file, local_csv_path)
            print(f"Downloaded {csv_file}")

            # Read CSV and download images
            with open(local_csv_path, newline="", encoding="utf-8") as f:
                reader = csv.reader(f)
                next(reader)  # Skip the header
                
                for row in reader:
                    image_path = row[0]
                    class_label = row[-1]

                    # Determine output directory
                    if class_label in CLASS_MAPPING:
                        output_dir = os.path.join(BASE_OUTPUT_DIR, CLASS_MAPPING[class_label])
                    else:
                        print(f"Skipping {image_path}, unknown class: {class_label}")
                        continue

                    # Download the image
                    local_image_path = os.path.join(output_dir, os.path.basename(image_path))
                    s3.download_file(BUCKET_NAME, image_path, local_image_path)
                    print(f"Saved {image_path} to {local_image_path}")

        print("All files processed successfully!")
        return True
    except Exception as e:
        logger.error(e)
        print(e)
        return False
