"""
Uploads router – queries the NOMAD API for upload/entry information and
returns summarised data to the dashboard frontend.

All endpoints here are protected: a valid Keycloak Bearer token must be
present in the Authorization header.  The token is forwarded to the NOMAD
API so that only data the user is allowed to see is returned.
"""

import logging

import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from nomad.config import config

from nomad_tfsc_general.apis.routers.auth import require_auth

logger = logging.getLogger(__name__)

router = APIRouter(prefix='/uploads', tags=['uploads'])

# Base URL of the local NOMAD API (same host, internal call)
# api_base_path is only a path segment (e.g. '/nomad-oasis'), so we use
# api_url() which builds the full http://host:port/base/api/v1 URL.
# Note: api_url(ssl, api=...) – 'ssl' is the first positional arg, so use keyword.
_NOMAD_API = config.services.api_url(ssl=False, api='api/v1')


def _nomad_headers(token: str) -> dict:
    return {'Authorization': f'Bearer {token}'}


@router.get('/summary', summary='Return a summary of recent uploads')
async def uploads_summary(token: str = Depends(require_auth)):
    """
    Returns a summary of uploads visible to the authenticated user.
    Queries the NOMAD /uploads endpoint and aggregates basic statistics.
    """
    url = f'{_NOMAD_API}/uploads'
    logger.info('Querying NOMAD uploads at: %s', url)
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
                detail=f'NOMAD API error at {url}: {exc.response.text}',
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
