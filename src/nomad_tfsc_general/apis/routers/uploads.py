"""
Uploads router – queries the NOMAD API for upload/entry information and
returns summarised data to the dashboard frontend.

All endpoints here are protected: a valid Keycloak Bearer token must be
present in the Authorization header.  The token is forwarded to the NOMAD
API so that only data the user is allowed to see is returned.
"""

import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from nomad.config import config

from nomad_tfsc_general.apis.routers.auth import require_auth

router = APIRouter(prefix='/uploads', tags=['uploads'])

# Base URL of the local NOMAD API (same host, internal call)
_NOMAD_API = f'{config.services.api_base_path}/v1'


def _nomad_headers(token: str) -> dict:
    return {'Authorization': f'Bearer {token}'}


@router.get('/summary', summary='Return a summary of recent uploads')
async def uploads_summary(token: str = Depends(require_auth)):
    """
    Returns a summary of uploads visible to the authenticated user.
    Queries the NOMAD /uploads endpoint and aggregates basic statistics.
    """
    url = f'{_NOMAD_API}/uploads'
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(
                url,
                headers=_nomad_headers(token),
                params={'page_size': 100},
                timeout=30,
            )
            resp.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise HTTPException(
                status_code=exc.response.status_code,
                detail=f'NOMAD API error: {exc.response.text}',
            ) from exc
        except httpx.RequestError as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f'Could not reach NOMAD API: {exc}',
            ) from exc

    data = resp.json()
    uploads = data.get('data', [])

    return {
        'total': data.get('pagination', {}).get('total', len(uploads)),
        'uploads': [
            {
                'upload_id': u.get('upload_id'),
                'upload_name': u.get('upload_name'),
                'upload_create_time': u.get('upload_create_time'),
                'published': u.get('published', False),
                'n_entries': u.get('n_entries', 0),
                'processing_failed': u.get('n_entries_with_processing_errors', 0),
            }
            for u in uploads
        ],
    }
