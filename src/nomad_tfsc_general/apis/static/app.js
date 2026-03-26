/**
 * Upload Quality Check – SPA JavaScript
 *
 * Screens:  login  →  app (upload list)  →  detail (single upload)
 */

'use strict';

// ── Globals ──────────────────────────────────────────────────────────────────
let keycloak = null;

// Root path of THIS FastAPI app derived from the current URL.
// Works for both /uploadqc and /uploadqc/ (trailing slash).
const API_BASE = (() => {
  const path = window.location.pathname.replace(/\/$/, '');
  const last = path.split('/').pop();
  return last && !last.includes('.') ? path : path.replace(/\/[^/]*$/, '') || '/';
})();

// ── Startup ──────────────────────────────────────────────────────────────────
window.addEventListener('DOMContentLoaded', initAuth);

async function initAuth() {
  let cfg;
  try {
    const res = await fetch(`${API_BASE}/auth/config`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    cfg = await res.json();
  } catch (err) {
    showError(`Cannot reach backend: ${err.message}`);
    return;
  }

  await loadScript(`${cfg.keycloak_url}/js/keycloak.js`);

  keycloak = new Keycloak({
    url: cfg.keycloak_url,
    realm: cfg.keycloak_realm,
    clientId: cfg.keycloak_client_id,
  });

  let authenticated;
  try {
    authenticated = await keycloak.init({ onLoad: 'check-sso', checkLoginIframe: false });
  } catch (err) {
    showError(`Keycloak init failed: ${err}`);
    return;
  }

  setInterval(async () => {
    try { await keycloak.updateToken(60); }
    catch (_) { showError('Session expired – please sign in again.'); showLoginPrompt(); }
  }, 30_000);

  if (authenticated) showList();
  else showLoginPrompt();
}

// ── Screen helpers ────────────────────────────────────────────────────────────
function showLoginPrompt() {
  show('login-screen'); hide('app-screen'); hide('detail-screen');
  document.getElementById('btn-login').onclick = () => keycloak.login();
}

function showList() {
  hide('login-screen'); show('app-screen'); hide('detail-screen');

  const parsed = keycloak.tokenParsed || {};
  const name = parsed.name || parsed.preferred_username || '';
  document.getElementById('user-name').textContent = name;
  document.getElementById('btn-logout').onclick = () =>
    keycloak.logout({ redirectUri: window.location.href });
  document.getElementById('btn-refresh').onclick = loadDashboard;

  loadDashboard();
}

function showDetail(uploadId) {
  hide('login-screen'); hide('app-screen'); show('detail-screen');

  const parsed = keycloak.tokenParsed || {};
  document.getElementById('detail-user-name').textContent =
    parsed.name || parsed.preferred_username || '';
  document.getElementById('detail-btn-logout').onclick = () =>
    keycloak.logout({ redirectUri: window.location.href });
  document.getElementById('btn-back').onclick = showList;

  // Reset tabs to first tab
  document.querySelectorAll('.tab-btn').forEach((b, i) => {
    b.classList.toggle('active', i === 0);
  });
  document.querySelectorAll('.tab-panel').forEach((p, i) => {
    p.classList.toggle('hidden', i !== 0);
  });
  // Show loading state in each tab
  ['types-container', 'processes-container', 'measurements-container', 'errors-container']
    .forEach(id => { document.getElementById(id).innerHTML = '<p class="placeholder">Loading…</p>'; });

  loadUploadDetail(uploadId);
}

// ── Tab wiring ────────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
      document.querySelectorAll('.tab-panel').forEach(p => p.classList.add('hidden'));
      btn.classList.add('active');
      show(btn.dataset.tab);
    });
  });
});

// ── Dashboard (upload list) ───────────────────────────────────────────────────
async function loadDashboard() {
  document.getElementById('table-container').innerHTML = '<p class="placeholder">Loading…</p>';
  const summary = await apiFetch('/uploads/summary');
  if (!summary) return;
  renderSummaryCards(summary);
  renderUploadsTable(summary.uploads);
}

// ── Upload detail ─────────────────────────────────────────────────────────────
async function loadUploadDetail(uploadId) {
  const data = await apiFetch(`/uploads/${uploadId}/detail`);
  if (!data) return;

  const u = data.upload;
  document.getElementById('detail-title').textContent = u.upload_name || uploadId;
  document.getElementById('detail-total').textContent = data.total_entries ?? '–';
  document.getElementById('detail-published').textContent = u.published ? 'Yes' : 'No';
  document.getElementById('detail-errors').textContent = data.entries_with_errors?.length ?? 0;

  renderTypeCountsTab(data.type_counts);
  renderProcessesTab(data.process_to_samples);
  renderMeasurementsTab(data.sample_to_measurements);
  renderErrorsTab(data.entries_with_errors, data.unknown_entries);
}

// ── API helpers ───────────────────────────────────────────────────────────────
async function apiFetch(path) {
  try { await keycloak.updateToken(30); }
  catch (_) { showError('Could not refresh token.'); return null; }

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

// ── Render – upload list ──────────────────────────────────────────────────────
function renderSummaryCards(summary) {
  document.getElementById('stat-total').textContent = summary.total ?? '–';
  const published = summary.uploads.filter(u => u.published).length;
  const errors = summary.uploads.filter(u => u.processing_failed > 0).length;
  document.getElementById('stat-published').textContent = published;
  document.getElementById('stat-errors').textContent = errors;
}

function renderUploadsTable(uploads) {
  const container = document.getElementById('table-container');
  if (!uploads || uploads.length === 0) {
    container.innerHTML = '<p class="placeholder">No uploads found.</p>';
    return;
  }
  const rows = uploads.map(u => {
    const date = u.upload_create_time ? new Date(u.upload_create_time).toLocaleString() : '–';
    const errCls = u.processing_failed > 0 ? 'error' : '';
    return `<tr>
      <td><a class="upload-link" data-id="${escHtml(u.upload_id)}" href="#">
            <code>${escHtml(u.upload_id ?? '')}</code></a></td>
      <td>${escHtml(u.upload_name ?? '')}</td>
      <td>${date}</td>
      <td>${u.published ? '✅' : '⬜'}</td>
      <td>${u.n_entries}</td>
      <td class="${errCls}">${u.processing_failed}</td>
    </tr>`;
  }).join('');

  container.innerHTML = `
    <table class="data-table">
      <thead><tr>
        <th>Upload ID</th><th>Name</th><th>Created</th>
        <th>Published</th><th>Entries</th><th>Errors</th>
      </tr></thead>
      <tbody>${rows}</tbody>
    </table>`;

  container.querySelectorAll('.upload-link').forEach(a => {
    a.addEventListener('click', e => { e.preventDefault(); showDetail(a.dataset.id); });
  });
}

// ── Render – detail tabs ──────────────────────────────────────────────────────
function renderTypeCountsTab(typeCounts) {
  const el = document.getElementById('types-container');
  if (!typeCounts || typeCounts.length === 0) {
    el.innerHTML = '<p class="placeholder">No entries found.</p>'; return;
  }
  const max = typeCounts[0].count;
  const rows = typeCounts.map(t => `
    <tr>
      <td>${escHtml(t.entry_type)}</td>
      <td>${t.count}</td>
      <td><div class="bar-wrap"><div class="bar" style="width:${Math.round(t.count / max * 100)}%"></div></div></td>
    </tr>`).join('');
  el.innerHTML = `
    <table class="data-table">
      <thead><tr><th>Entry type</th><th>Count</th><th>Distribution</th></tr></thead>
      <tbody>${rows}</tbody>
    </table>`;
}

function renderProcessesTab(processList) {
  const el = document.getElementById('processes-container');
  if (!processList || processList.length === 0) {
    el.innerHTML = '<p class="placeholder">No process entries found.</p>'; return;
  }
  const rows = processList.map(p => `
    <tr>
      <td>${escHtml(p.process_name)}</td>
      <td><span class="tag">${escHtml(p.process_type ?? '')}</span></td>
      <td>${p.samples.length ? p.samples.map(s => `<span class="chip">${escHtml(s)}</span>`).join(' ')
                             : '<span class="muted">–</span>'}</td>
    </tr>`).join('');
  el.innerHTML = `
    <table class="data-table">
      <thead><tr><th>Process</th><th>Type</th><th>Connected samples</th></tr></thead>
      <tbody>${rows}</tbody>
    </table>`;
}

function renderMeasurementsTab(sampleList) {
  const el = document.getElementById('measurements-container');
  if (!sampleList || sampleList.length === 0) {
    el.innerHTML = '<p class="placeholder">No sample–measurement links found.</p>'; return;
  }
  const rows = sampleList.map(s => `
    <tr>
      <td><strong>${escHtml(s.sample_name)}</strong></td>
      <td>${s.measurements.map(m =>
        `<div><span class="chip">${escHtml(m.name)}</span> <span class="muted">${escHtml(m.type ?? '')}</span></div>`
      ).join('')}</td>
    </tr>`).join('');
  el.innerHTML = `
    <table class="data-table">
      <thead><tr><th>Sample</th><th>Measurements</th></tr></thead>
      <tbody>${rows}</tbody>
    </table>`;
}

function renderErrorsTab(errorList, unknownList) {
  const el = document.getElementById('errors-container');
  const noErrors = (!errorList || errorList.length === 0);
  const noUnknown = (!unknownList || unknownList.length === 0);
  if (noErrors && noUnknown) {
    el.innerHTML = '<p class="placeholder">✅ No processing errors found.</p>'; return;
  }
  let html = '';
  if (!noErrors) {
    const rows = errorList.map(e => `
      <tr>
        <td>${escHtml(e.entry_name)}</td>
        <td><span class="tag">${escHtml(e.entry_type)}</span></td>
        <td class="error">${e.errors.map(err => escHtml(String(err))).join('<br>')}</td>
      </tr>`).join('');
    html += `<h3 class="section-title">Processing errors</h3>
      <table class="data-table">
        <thead><tr><th>Entry</th><th>Type</th><th>Errors</th></tr></thead>
        <tbody>${rows}</tbody>
      </table>`;
  }
  if (!noUnknown) {
    html += `<h3 class="section-title" style="margin-top:1.25rem">Unknown entry types (${unknownList.length})</h3>
      <ul class="plain-list">${unknownList.map(n => `<li><code>${escHtml(n)}</code></li>`).join('')}</ul>`;
  }
  el.innerHTML = html;
}

// ── Utility ───────────────────────────────────────────────────────────────────
function show(id) { document.getElementById(id).classList.remove('hidden'); }
function hide(id) { document.getElementById(id).classList.add('hidden'); }

function showError(msg) {
  const banner = document.getElementById('error-banner');
  banner.textContent = `⚠ ${msg}`;
  banner.classList.remove('hidden');
  setTimeout(() => banner.classList.add('hidden'), 8000);
}

function escHtml(str) {
  return String(str)
    .replace(/&/g, '&amp;').replace(/</g, '&lt;')
    .replace(/>/g, '&gt;').replace(/"/g, '&quot;');
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
