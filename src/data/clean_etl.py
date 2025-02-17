
import requests
from src.custom_logger import logger
from src.utils.env import get_env_var


def call_clean( text: str ) -> str:
    url = (get_env_var('ENDPOINT_URL_CLEAN'))
    payload = {
        "text": f"{text}"
    }
    headers = {"Content-Type": "application/json"}
    response = requests.post(
        url=url,
        json=payload,
        headers=headers
    )
    return response.text


def transform( files: list) -> list:
    try:
        datas = []
        for file in files:
            text = call_clean(file.text)
            datas.append({"name": f"{file.name}.txt", "text": text})
        return datas

    except Exception as e:
        logger.error(f"CLEAN / An error occurred : {str(e)}")
        raise e
