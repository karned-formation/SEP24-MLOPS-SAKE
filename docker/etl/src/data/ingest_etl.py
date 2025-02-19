import requests
from src.custom_logger import logger
from src.utils.env import get_env_var

def call_ocr( image_base64: str ) -> str:
    url = (get_env_var('ENDPOINT_URL_OCR'))
    payload = {
        "file": f"{image_base64}",
        "model_detection": "db_resnet34",
        "model_recognition": "crnn_vgg16_bn"
    }
    headers = {"Content-Type": "application/json"}
    response = requests.post(
        url=url,
        json=payload,
        headers=headers
    )
    return response.text


def extract( files: list ):
    try:
        datas = []
        for file in files:
            text = call_ocr(image_base64=file.content)
            datas.append({"name": f"{file.name}.txt", "text": text})
        return datas

    except Exception as e:
        logger.error(f"OCERIZE / An error occurred : {str(e)}")
        raise e

