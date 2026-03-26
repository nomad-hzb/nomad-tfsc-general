# Upload QC API – Architecture

## What this is

A **NOMAD plugin** that mounts a small FastAPI sub-application at
`{api_base_path}/uploadqc` (e.g. `http://localhost:8000/nomad-oasis/uploadqc`).
It provides a single-page dashboard for monitoring the quality of NOMAD uploads:
entry type distribution, process → sample links, sample → measurement links, and
processing errors.

---

## How it is mounted

NOMAD's plugin system calls `UploadQCEntryPoint.load()` (in `__init__.py`),
which returns the FastAPI `app` from `upload_qc.py`.  NOMAD then mounts it at:

```
{config.services.api_base_path}/{entry_point.prefix}
# default: /nomad-oasis/uploadqc
```

See `nomad/app/main.py → for entry_point in config.plugins …  app.mount(…)`.

---

## File map

```
apis/
├── __init__.py          # UploadQCEntryPoint – tells NOMAD how to load the app
├── upload_qc.py         # FastAPI app factory; registers routers + static files
├── ARCHITECTURE.md      # this file
│
├── routers/
│   ├── auth.py          # GET /auth/config  – returns Keycloak params to the SPA
│   │                    # require_auth()    – FastAPI dependency, extracts Bearer token
│   └── uploads.py       # GET /uploads/summary          – paginated upload list
│                        # GET /uploads/{id}/detail       – per-upload entry map
│
└── static/
    ├── index.html       # SPA shell (3 screens: login / list / detail)
    ├── app.js           # All SPA logic (auth flow, routing, render helpers)
    └── style.css        # CSS variables + component styles
```

---

## URL layout

| URL (relative to app root) | Handler | Auth required |
|---|---|---|
| `GET /` | serves `index.html` | no |
| `GET /static/*` | static file mount | no |
| `GET /auth/config` | `auth.auth_config` | no |
| `GET /uploads/summary` | `uploads.uploads_summary` | Bearer token |
| `GET /uploads/{upload_id}/detail` | `uploads.upload_detail` | Bearer token |
| `GET /docs` | FastAPI auto-docs | no |

---

## Auth flow

```
Browser                     FastAPI app              Keycloak              NOMAD API
  │                              │                      │                      │
  ├─GET /auth/config────────────►│                      │                      │
  │◄─{keycloak_url, realm, …}───┤                      │                      │
  │                              │                      │                      │
  ├─load keycloak.js─────────────┼─────────────────────►│                      │
  ├─keycloak.init(check-sso)─────┼─────────────────────►│                      │
  │◄─authenticated / not─────────┼─────────────────────┤                      │
  │                              │                      │                      │
  ├─GET /uploads/summary─────────►│                      │                      │
  │  Authorization: Bearer <tok> │                      │                      │
  │                              ├─GET /api/v1/uploads──┼─────────────────────►│
  │                              │◄─upload JSON─────────┼─────────────────────┤
  │◄─summary JSON────────────────┤                      │                      │
```

The Bearer token is **forwarded as-is** to the NOMAD API.  NOMAD validates it
against Keycloak itself, so this app never holds user credentials.

---

## Backend: key design decisions

### `_NOMAD_API` base URL
```python
_NOMAD_API = config.services.api_url(ssl=False, api='api/v1')
# → http://localhost:8000/nomad-oasis/api/v1
```
`api_url(ssl, api=…)` — note `ssl` is the **first positional arg**, so always
pass `api=` as a keyword to avoid silent misconfiguration.

### Entry-map logic (`/uploads/{id}/detail`)
Upload metadata and entries are fetched **in parallel** with `asyncio.gather`.
The entry map (type counts, process→samples, sample→measurements, errors) is
computed inline from the `parse_upload_map` logic in `parsers.py`, adapted to
avoid the external dependency.  The entry-reference graph is traversed first;
naming-convention heuristics (`_cell<N>_<N>` suffix stripping) are the fallback
for unlinked measurements.

### Domain constants
`_SAMPLE_TYPES`, `_PROCESS_TYPES`, `_RAW_TYPES` in `uploads.py` mirror the
frozensets in `parsers.py`.  **Keep them in sync** when new schema entry types
are added to the TFSC plugin.

---

## Frontend: key design decisions

### `API_BASE` derivation
```javascript
const API_BASE = (() => {
  const path = window.location.pathname.replace(/\/$/, '');
  const last = path.split('/').pop();
  // Keep the last segment if it has no dot (it's a directory/app root, not a file)
  return last && !last.includes('.') ? path : path.replace(/\/[^/]*$/, '') || '/';
})();
```
Works for both `/uploadqc` and `/uploadqc/` without hard-coding any path prefix.

### SPA navigation
There are no real page navigations — three `<div class="screen">` elements are
shown/hidden by `show()`/`hide()`.  The active screen is controlled by
`showLoginPrompt()`, `showList()`, `showDetail(uploadId)`.

### Tab wiring
Tabs are wired once on `DOMContentLoaded` by reading `data-tab` attributes.
Adding a new tab requires: an HTML `<button class="tab-btn" data-tab="tab-X">`
and a matching `<div id="tab-X" class="tab-panel hidden">`.

---

## How to add a new feature

### New backend endpoint
1. Add a route in `routers/uploads.py` (or a new file in `routers/`).
2. Register it in `upload_qc.py` with `app.include_router(…)`.

### New dashboard section (new tab on the detail page)
1. Add the tab button + panel HTML to `index.html`.
2. Add a `renderXxxTab(data)` function in `app.js`.
3. Call it from `loadUploadDetail()`.
4. Fetch the data from the new endpoint (or extend the existing `/detail` response).

### New entry type
Add it to `_SAMPLE_TYPES` / `_PROCESS_TYPES` / `_RAW_TYPES` in `uploads.py`
**and** the matching frozenset in `parsers.py`.

---

## Known pitfalls

| Pitfall | Notes |
|---|---|
| `api_url` positional arg | First arg is `ssl: bool`, not `api`. Always use `api='api/v1'` as keyword. |
| `api_base_path` is path-only | It has no scheme/host. Never use it alone to build URLs. |
| Module-level `_NOMAD_API` | Evaluated at import time. If config changes after import (e.g. in tests), the value won't update. |
| Token forwarding | The Bearer token is forwarded without server-side validation. For sensitive Oasis deployments, add `python-keycloak` introspection in `require_auth()` (see the commented block in `auth.py`). |
