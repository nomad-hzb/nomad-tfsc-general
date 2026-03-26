from fastapi import FastAPI
from nomad.config import config

upload_qc_entry_point = config.get_plugin_entry_point('nomad_tfsc_general.apis:upload_qc')

app = FastAPI(
    root_path=f'{config.services.api_base_path}/{upload_qc_entry_point.prefix}'
)

@app.get('/')
async def root():
    return {"message": "Hello World"}

@app.get('/auth/config')
async def auth_config():
    """Return Keycloak config so the frontend can initialize authentication."""
    return {
        'keycloak_url': config.keycloak.public_server_url,
        'keycloak_realm': config.keycloak.realm_name,
        'keycloak_client_id': config.keycloak.client_id,
    }