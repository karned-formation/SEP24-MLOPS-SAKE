import base64
from PIL import Image
import io
from typing import Dict, List
import os
from fastapi import UploadFile


def get_image_list() -> Dict[str, List[Dict]]:
    """Get list of images from all folders with thumbnails."""
    base_folders = [f"data/raw_per_classes/{i}" for i in range(3)]
    result = {}
    
    for folder in base_folders:
        result[folder] = []
        if os.path.exists(folder):
            for filename in os.listdir(folder):
                if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                    # Create thumbnail
                    img_path = os.path.join(folder, filename)
                    with Image.open(img_path) as img:
                        img.thumbnail((100, 100))
                        buffered = io.BytesIO()
                        img.save(buffered, format="PNG")
                        img_str = base64.b64encode(buffered.getvalue()).decode()
                    
                    result[folder].append({
                        "name": filename,
                        "thumbnail": f"data:image/png;base64,{img_str}"
                    })
    return result

async def save_uploaded_image(file: UploadFile, folder: str) -> bool:
    """Save uploaded image to specified folder."""
    try:
        if not os.path.exists(folder):
            os.makedirs(folder)
        
        file_path = os.path.join(folder, file.filename)
        contents = await file.read()
        
        with open(file_path, "wb") as f:
            f.write(contents)
        
        return True
    except Exception as e:
        print(f"Error saving image: {str(e)}")
        return False

def delete_image_file(folder: str, image_name: str) -> bool:
    """Delete image from specified folder."""
    try:
        file_path = os.path.join(folder, image_name)
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False
    except Exception as e:
        print(f"Error deleting image: {str(e)}")
        return False