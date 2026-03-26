/**
 * Upload Quality Check – SPA JavaScript
 *
 * Auth flow
 * ---------
 * 1. Fetch /auth/config  → get Keycloak server URL, realm, clientId
 * 2. Dynamically load the Keycloak JS adapter from the Keycloak server
 *    (ensures version compatibility with the server).
 * 3. Initialise Keycloak with check-sso so returning users are recognised
 *    without a full redirect.
 * 4. All API requests include the Bearer token; the token is silently
 *    refreshed before expiry.
 *
 * Adding a new dashboard section
 * --------------------------------
 * 1. Add a router in  apis/routers/<name>.py  and register it in upload_qc.py
 * 2. Add a fetch helper in the "API helpers" section below
 * 3. Add a render function in the "Render helpers" section
 * 4. Call both from loadDashboard()
 */

'use strict';

// ── Globals ──────────────────────────────────────────────────────────────────
let keycloak = null;

// The root path of THIS FastAPI app (same origin, no CORS needed).
// Derived from the current page URL so it works regardless of deployment path.
// We strip any trailing slash first, then strip the last path segment only if
// it looks like a file (contains a dot), so both /uploadqc and /uploadqc/
// correctly resolve to /nomad-oasis/uploadqc.
const API_BASE = (() => {
  const path = window.location.pathname.replace(/\/$/, ''); // strip trailing slash
  // If the last segment has no dot it's a directory/app root – keep as-is
  const last = path.split('/').pop();
  return last && !last.includes('.') ? path : path.replace(/\/[^/]*$/, '') || '/';
})();

// ── Startup ──────────────────────────────────────────────────────────────────
window.addEventListener('DOMContentLoaded', initAuth);

async function initAuth() {
  // 1. Fetch Keycloak config from the backend
  let cfg;
  try {
    const res = await fetch(`${API_BASE}/auth/config`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    cfg = await res.json();
  } catch (err) {
    showError(`Cannot reach backend: ${err.message}`);
    return;
  }

  // 2. Dynamically inject the Keycloak JS adapter
  await loadScript(`${cfg.keycloak_url}/js/keycloak.js`);

  // 3. Initialise Keycloak
  keycloak = new Keycloak({
    url: cfg.keycloak_url,
    realm: cfg.keycloak_realm,
    clientId: cfg.keycloak_client_id,
  });

  let authenticated;
  try {
    authenticated = await keycloak.init({
      onLoad: 'check-sso',
      checkLoginIframe: false,
    });
  } catch (err) {
    showError(`Keycloak init failed: ${err}`);
    return;
  }

  // 4. Wire up token refresh (refresh 60 s before expiry)
  setInterval(async () => {
    try {
      await keycloak.updateToken(60);
    } catch (_) {
      showError('Session expired – please sign in again.');
      showLoginPrompt();
    }
  }, 30_000);

  if (authenticated) {
    showApp();
  } else {
    showLoginPrompt();
  }
}

// ── Screen helpers ────────────────────────────────────────────────────────────
function showLoginPrompt() {
  show('login-screen');
  hide('app-screen');
  document.getElementById('btn-login').onclick = () => keycloak.login();
}

function showApp() {
  hide('login-screen');
  show('app-screen');

  // Show user name in the header
  const parsed = keycloak.tokenParsed || {};
  document.getElementById('user-name').textContent =
    parsed.name || parsed.preferred_username || '';

  document.getElementById('btn-logout').onclick = () =>
    keycloak.logout({ redirectUri: window.location.href });

  document.getElementById('btn-refresh').onclick = loadDashboard;

  loadDashboard();
}

// ── Dashboard data loading ────────────────────────────────────────────────────
async function loadDashboard() {
  document.getElementById('table-container').innerHTML =
    '<p class="placeholder">Loading…</p>';

  const summary = await apiFetch('/uploads/summary');
  if (!summary) return;

  renderSummaryCards(summary);
  renderUploadsTable(summary.uploads);
}

// ── API helpers ───────────────────────────────────────────────────────────────
/**
 * Authenticated GET request to the FastAPI backend.
 * Returns parsed JSON on success, null on failure (error shown to user).
 */
async function apiFetch(path) {
  try {
    await keycloak.updateToken(30);
  } catch (_) {
    showError('Could not refresh token.');
    return null;
  }

  let res;
  try {
    res = await fetch(`${API_BASE}${path}`, {
      headers: { Authorization: `Bearer ${keycloak.token}` },
    });
  } catch (err) {
    showError(`Network error: ${err.message}`);
    return null;
  }

  if (!res.ok) {
    const text = await res.text().catch(() => res.statusText);
    showError(`API error ${res.status}: ${text}`);
    return null;
  }

  return res.json();
}

// ── Render helpers ────────────────────────────────────────────────────────────
function renderSummaryCards(summary) {
  document.getElementById('stat-total').textContent = summary.total ?? '–';

  const published = summary.uploads.filter((u) => u.published).length;
  const errors = summary.uploads.filter((u) => u.processing_failed > 0).length;

  document.getElementById('stat-published').textContent = published;
  document.getElementById('stat-errors').textContent = errors;
}

function renderUploadsTable(uploads) {
  const container = document.getElementById('table-container');

  if (!uploads || uploads.length === 0) {
    container.innerHTML = '<p class="placeholder">No uploads found.</p>';
    return;
  }

  const rows = uploads
    .map((u) => {
      const date = u.upload_create_time
        ? new Date(u.upload_create_time).toLocaleString()
        : '–';
      const errorClass = u.processing_failed > 0 ? 'error' : '';
      return `
        <tr>
          <td><code>${u.upload_id}</code></td>
          <td>${escHtml(u.upload_name ?? '')}</td>
          <td>${date}</td>
          <td>${u.published ? '✅' : '⬜'}</td>
          <td>${u.n_entries}</td>
          <td class="${errorClass}">${u.processing_failed}</td>
        </tr>`;
    })
    .join('');

  container.innerHTML = `
    <table class="data-table">
      <thead>
        <tr>
          <th>Upload ID</th>
          <th>Name</th>
          <th>Created</th>
          <th>Published</th>
          <th>Entries</th>
          <th>Errors</th>
        </tr>
      </thead>
      <tbody>${rows}</tbody>
    </table>`;
}

// ── Utility ───────────────────────────────────────────────────────────────────
function show(id) {
  document.getElementById(id).classList.remove('hidden');
}
function hide(id) {
  document.getElementById(id).classList.add('hidden');
}

function showError(msg) {
  const banner = document.getElementById('error-banner');
  banner.textContent = `⚠ ${msg}`;
  banner.classList.remove('hidden');
  setTimeout(() => banner.classList.add('hidden'), 8000);
}

function escHtml(str) {
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function loadScript(src) {
  return new Promise((resolve, reject) => {
    const s = document.createElement('script');
    s.src = src;
    s.onload = resolve;
    s.onerror = () => reject(new Error(`Failed to load script: ${src}`));
    document.head.appendChild(s);
  });
}
