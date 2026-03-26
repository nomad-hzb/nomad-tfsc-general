"""
Upload Quality Check – FastAPI application entry point.

URL layout (relative to the plugin prefix, e.g. /nomad-oasis/uploadqc):
  /           → serves the SPA (index.html)
  /static/    → static assets (JS, CSS)
  /auth/*     → Keycloak configuration endpoint (see routers/auth.py)
  /uploads/*  → NOMAD upload query endpoints (see routers/uploads.py)
  /docs       → auto-generated OpenAPI docs
"""

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from nomad.config import config

from nomad_tfsc_general.apis.routers import auth, uploads

upload_qc_entry_point = config.get_plugin_entry_point('nomad_tfsc_general.apis:upload_qc')

_STATIC_DIR = Path(__file__).parent / 'static'

app = FastAPI(
    title='Upload Quality Check',
    description='Dashboard for monitoring NOMAD uploads and entries.',
    root_path=f'{config.services.api_base_path}/{upload_qc_entry_point.prefix}',
)

# ── routers ──────────────────────────────────────────────────────────────────
app.include_router(auth.router)
app.include_router(uploads.router)

# ── static files & SPA fallback ──────────────────────────────────────────────
app.mount('/static', StaticFiles(directory=_STATIC_DIR), name='static')


@app.get('/', include_in_schema=False)
async def spa_root():
    """Serve the single-page application shell."""
    return FileResponse(_STATIC_DIR / 'index.html')