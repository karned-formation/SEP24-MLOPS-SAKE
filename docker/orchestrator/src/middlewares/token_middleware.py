import os
import time

import httpx
from fastapi import HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

UNPROTECTED_PATHS = ['/favicon.ico', '/docs', '/openapi.json', '/metrics']
API_NAME = 'karned'
KEYCLOAK_HOST = os.environ.get('KEYCLOAK_SERVER_URL')
KEYCLOAK_REALM = os.environ.get('KEYCLOAK_REALM_NAME')
KEYCLOAK_CLIENT_ID = os.environ.get('KEYCLOAK_CLIENT_ID')
KEYCLOAK_CLIENT_SECRET = os.environ.get('KEYCLOAK_CLIENT_SECRET')

def is_unprotected_path( path: str ) -> bool:
    return path.lower() in UNPROTECTED_PATHS


def generate_state_info( token_info: dict ) -> dict:
    return {
        "user_id": token_info.get("sub"),
        "user_display_name": token_info.get("preferred_username"),
        "user_email": token_info.get("email"),
        "user_audiences": token_info.get("aud")
    }


def is_token_valid_audience( token_info: dict ) -> bool:
    aud = token_info.get("aud")
    return API_NAME in aud


def is_token_active( token_info: dict ) -> bool:
    now = int(time.time())
    iat = token_info.get("iat")
    exp = token_info.get("exp")

    if iat is not None and exp is not None:
        return iat < now < exp

    return False


def introspect_token( token: str ) -> dict:
    url = f"{KEYCLOAK_HOST}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/token/introspect"
    data = {
        "token": token,
        "client_id":KEYCLOAK_CLIENT_ID,
        "client_secret": KEYCLOAK_CLIENT_SECRET
    }

    response = httpx.post(url, data=data)
    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Keycloak introspection failed")
    return response.json()


def is_headers_token_present( request: Request ) -> bool:
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return False
    if not auth_header.startswith("Bearer "):
        return False
    return True


def extract_token( request: Request ) -> str:
    auth_header = request.headers.get("Authorization")
    token = auth_header.split(" ")[1]
    return token


def store_token_info_in_state( state_token_info: dict, request: Request ):
    request.state.token_info = state_token_info


def check_headers_token( request: Request ):
    if not is_headers_token_present(request):
        raise HTTPException(status_code=401, detail="Token manquant ou invalide")


def check_token( token_info ):
    if not is_token_active(token_info):
        raise HTTPException(status_code=401, detail="Token is not active")

    if not is_token_valid_audience(token_info):
        raise HTTPException(status_code=401, detail="Token is not valid for this audience")


class TokenVerificationMiddleware(BaseHTTPMiddleware):
    def __init__( self, app ):
        super().__init__(app)

    async def dispatch( self, request: Request, call_next ) -> Response:
        if not is_unprotected_path(request.url.path):
            check_headers_token(request)
            token = extract_token(request)
            token_info = introspect_token(token)
            check_token(token_info)
            state_token_info = generate_state_info(token_info)
            store_token_info_in_state(state_token_info, request)
        response = await call_next(request)
        return response
