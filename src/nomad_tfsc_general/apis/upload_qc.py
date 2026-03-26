from fastapi import FastAPI
from nomad.config import config

upload_qc_entry_point = config.get_plugin_entry_point('nomad_tfsc_general.apis:upload_qc')

app = FastAPI(
    root_path=f'{config.services.api_base_path}/{upload_qc_entry_point.prefix}'
)

@app.get('/')
async def root():
    return {"message": "Hello World"}