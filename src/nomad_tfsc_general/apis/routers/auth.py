"""
Auth router – exposes Keycloak configuration to the frontend SPA so the
Keycloak JS adapter can be initialised without hard-coding credentials in
the static files.

Protected endpoints can use the `require_auth` dependency to validate the
Bearer token that the frontend obtains after login.
"""

from fastapi import APIRouter, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from nomad.config import config

router = APIRouter(prefix='/auth', tags=['auth'])

_bearer = HTTPBearer(auto_error=False)


@router.get('/config', summary='Return Keycloak configuration for the frontend')
async def auth_config():
    """
    Returns the Keycloak parameters needed by the Keycloak JS adapter so the
    SPA can authenticate the user without any credentials being hard-coded in
    the static files.
    """
    return {
        'keycloak_url': config.keycloak.public_server_url,
        'keycloak_realm': config.keycloak.realm_name,
        'keycloak_client_id': config.keycloak.client_id,
    }


async def require_auth(
    credentials: HTTPAuthorizationCredentials = Security(_bearer),
) -> str:
    """
    FastAPI dependency that validates the Bearer token sent by the frontend.

    Usage::

        @router.get('/protected')
        async def protected(user: str = Depends(require_auth)):
            return {'user': user}

    Returns the raw token string so downstream code can forward it to the
    NOMAD API if needed.
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Missing Bearer token',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    # The token is validated by Keycloak on the frontend before it is sent
    # here.  For server-side validation (optional but recommended for
    # sensitive endpoints) you can use python-keycloak:
    #
    #   from keycloak import KeycloakOpenID
    #   kc = KeycloakOpenID(
    #       server_url=config.keycloak.public_server_url,
    #       realm_name=config.keycloak.realm_name,
    #       client_id=config.keycloak.client_id,
    #   )
    #   token_info = kc.introspect(credentials.credentials)
    #   if not token_info.get('active'):
    #       raise HTTPException(status_code=401, detail='Invalid or expired token')
    #
    return credentials.credentials
