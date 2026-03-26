"""
Uploads router – queries the NOMAD API for upload/entry information and
returns summarised data to the dashboard frontend.

All endpoints here are protected: a valid Keycloak Bearer token must be
present in the Authorization header.  The token is forwarded to the NOMAD
API so that only data the user is allowed to see is returned.
"""

import logging
import re
from collections import defaultdict

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

# ── Domain constants (TFSC schema entry types) ────────────────────────────────
_SAMPLE_TYPES = frozenset({'TFSC_General_Sample'})
_PROCESS_TYPES = frozenset({
    'TFSC_General_SpinCoating', 'TFSC_General_BladeCoating',
    'TFSC_General_SlotDieCoating', 'TFSC_General_GravurePrinting',
    'TFSC_General_Inkjet_Printing', 'TFSC_General_ScreenPrinting',
    'TFSC_General_Sputtering', 'TFSC_General_Evaporation',
    'TFSC_General_AtomicLayerDeposition', 'TFSC_General_Substrate',
    'TFSC_General_Cleaning', 'TFSC_General_LaserScribing', 'TFSC_General_Batch',
})
_RAW_TYPES = frozenset({'RawTFSCGeneralExperiment', 'RawFileTFSCGeneral'})


def _is_measurement(entry_type: str | None) -> bool:
    if not entry_type:
        return False
    return (
        entry_type not in _SAMPLE_TYPES
        and entry_type not in _PROCESS_TYPES
        and entry_type not in _RAW_TYPES
    )


def _nomad_headers(token: str) -> dict:
    return {'Authorization': f'Bearer {token}'}


async def _nomad_get(client: httpx.AsyncClient, url: str, token: str, **kwargs) -> dict:
    """Shared GET helper – raises HTTPException on NOMAD or network errors."""
    try:
        resp = await client.get(url, headers=_nomad_headers(token), **kwargs)
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
    return resp.json()


@router.get('/summary', summary='Return a summary of recent uploads')
async def uploads_summary(token: str = Depends(require_auth)):
    """
    Returns a summary of uploads visible to the authenticated user.
    Queries the NOMAD /uploads endpoint and aggregates basic statistics.
    """
    url = f'{_NOMAD_API}/uploads'
    logger.info('Querying NOMAD uploads at: %s', url)
    async with httpx.AsyncClient() as client:
        data = await _nomad_get(client, url, token, params={'page_size': 100}, timeout=30)

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


@router.get('/{upload_id}/detail', summary='Return detailed overview of a single upload')
async def upload_detail(upload_id: str, token: str = Depends(require_auth)):
    """
    Returns upload metadata + a structured map of entries (type counts,
    process→samples, sample→measurements, errors) for the given upload.
    """
    async with httpx.AsyncClient() as client:
        # Fetch upload metadata and all entries in parallel
        import asyncio
        meta_data, entries_data = await asyncio.gather(
            _nomad_get(client, f'{_NOMAD_API}/uploads/{upload_id}', token, timeout=30),
            _nomad_get(client, f'{_NOMAD_API}/uploads/{upload_id}/entries',
                       token, params={'page_size': 10000}, timeout=60),
        )

    # ── Upload metadata ───────────────────────────────────────────────────────
    meta = meta_data.get('data', meta_data)
    upload_info = {
        'upload_id': meta.get('upload_id', upload_id),
        'upload_name': meta.get('upload_name') or upload_id,
        'upload_create_time': meta.get('upload_create_time', ''),
        'publish_time': meta.get('publish_time', ''),
        'published': meta.get('published', False),
        'n_entries': meta.get('n_entries', 0),
        'last_status_message': meta.get('last_status_message', ''),
    }

    # ── Entry map (adapted from parse_upload_map) ─────────────────────────────
    entries = entries_data.get('data', [])

    def _m(e):
        return e.get('entry_metadata', e)

    entry_by_id = {e['entry_id']: e for e in entries}

    # 1. Type counts
    type_counter: dict = defaultdict(int)
    for e in entries:
        type_counter[_m(e).get('entry_type') or 'Unknown'] += 1
    type_counts = [
        {'entry_type': et, 'count': c}
        for et, c in sorted(type_counter.items(), key=lambda x: -x[1])
    ]

    # 2. Process → samples
    process_to_samples = []
    for e in entries:
        m = _m(e)
        if m.get('entry_type') not in _PROCESS_TYPES:
            continue
        seen: set = set()
        samples = []
        for ref in m.get('entry_references', []):
            tid = ref.get('target_entry_id')
            if tid and tid not in seen:
                target = entry_by_id.get(tid)
                if target and _m(target).get('entry_type') in _SAMPLE_TYPES:
                    samples.append(_m(target).get('entry_name') or tid)
                    seen.add(tid)
        process_to_samples.append({
            'process_name': m.get('entry_name') or e.get('entry_id', ''),
            'process_type': m.get('entry_type'),
            'samples': samples,
        })

    # 3. Sample → measurements
    sample_name_set = {
        (_m(e).get('entry_name') or '').strip(): (_m(e).get('entry_name') or '').strip()
        for e in entries if _m(e).get('entry_type') in _SAMPLE_TYPES
        if (_m(e).get('entry_name') or '').strip()
    }

    def _guess_sample(meas_name: str) -> str | None:
        name = meas_name.strip()
        c = re.sub(r'(_cell\d+_\d+)+$', '', name).strip()
        if c in sample_name_set:
            return c
        c2 = re.sub(r'_[^_]+$', '', name).strip()
        return sample_name_set.get(c2)

    sample_map: dict = defaultdict(list)
    for e in entries:
        m = _m(e)
        et = m.get('entry_type')
        if not _is_measurement(et):
            continue
        meas_display = m.get('entry_name') or e.get('entry_id', '')
        seen = set()
        for ref in m.get('entry_references', []):
            tid = ref.get('target_entry_id')
            if tid and tid not in seen:
                target = entry_by_id.get(tid)
                if target and _m(target).get('entry_type') in _SAMPLE_TYPES:
                    sample_map[_m(target).get('entry_name') or tid].append(
                        {'name': meas_display, 'type': et}
                    )
                    seen.add(tid)
        if not seen:
            guessed = _guess_sample(meas_display)
            if guessed:
                sample_map[guessed].append({'name': meas_display, 'type': et})

    sample_to_measurements = [
        {'sample_name': s, 'measurements': ms}
        for s, ms in sorted(sample_map.items())
    ]

    # 4. Entries with errors
    entries_with_errors = [
        {
            'entry_name': _m(e).get('entry_name') or e.get('entry_id', ''),
            'entry_type': _m(e).get('entry_type') or 'Unknown',
            'errors': _m(e).get('processing_errors', []),
        }
        for e in entries if _m(e).get('processing_errors')
    ]

    # 5. Unknown entry types
    unknown_entries = [
        _m(e).get('entry_name') or e.get('mainfile') or e.get('entry_id', '')
        for e in entries if _m(e).get('entry_type') is None
    ]

    return {
        'upload': upload_info,
        'type_counts': type_counts,
        'process_to_samples': process_to_samples,
        'sample_to_measurements': sample_to_measurements,
        'entries_with_errors': entries_with_errors,
        'unknown_entries': unknown_entries,
        'total_entries': len(entries),
    }
