/* ================================================================
   SecureHub — Global Application JavaScript
   Loaded in <head> so all helpers are available to page scripts
   ================================================================ */

'use strict';

// ── Token Management ──────────────────────────────────────────────

const Auth = {
  getAccessToken()  { return localStorage.getItem('access_token'); },
  getRefreshToken() { return localStorage.getItem('refresh_token'); },
  setTokens(access, refresh) {
    localStorage.setItem('access_token', access);
    if (refresh) localStorage.setItem('refresh_token', refresh);
  },
  clearTokens() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
  },
  getUser() {
    try { return JSON.parse(localStorage.getItem('user') || 'null'); }
    catch { return null; }
  },
  setUser(user) { localStorage.setItem('user', JSON.stringify(user)); },
  isLoggedIn()  { return !!this.getAccessToken(); },
  isAdmin()     { return this.getUser()?.role === 'admin'; },
};


// ── API Client ────────────────────────────────────────────────────

const API = {
  baseURL: '/api',

  async request(method, endpoint, data = null, auth = true) {
    const headers = { 'Content-Type': 'application/json' };
    if (auth) {
      const token = Auth.getAccessToken();
      if (token) headers['Authorization'] = `Bearer ${token}`;
    }

    const options = { method: method.toUpperCase(), headers };
    if (data) options.body = JSON.stringify(data);

    try {
      let res = await fetch(`${this.baseURL}${endpoint}`, options);

      // Token expiry → try refresh
      if (res.status === 401 && auth) {
        const refreshed = await this.refreshAccessToken();
        if (refreshed) {
          headers['Authorization'] = `Bearer ${Auth.getAccessToken()}`;
          res = await fetch(`${this.baseURL}${endpoint}`, { ...options, headers });
        } else {
          Auth.clearTokens();
          window.location.href = '/login';
          return null;
        }
      }

      return await res.json();
    } catch (err) {
      console.error('API error:', err);
      Toast.error('Network error. Please try again.');
      return null;
    }
  },

  get(endpoint, auth = true)       { return this.request('GET',    endpoint, null, auth); },
  post(endpoint, data, auth = true) { return this.request('POST',   endpoint, data, auth); },
  put(endpoint, data, auth = true)  { return this.request('PUT',    endpoint, data, auth); },
  delete(endpoint, auth = true)     { return this.request('DELETE', endpoint, null, auth); },

  async refreshAccessToken() {
    const refreshToken = Auth.getRefreshToken();
    if (!refreshToken) return false;
    try {
      const res = await fetch(`${this.baseURL}/auth/refresh`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${refreshToken}`,
        },
      });
      const data = await res.json();
      if (data.success && data.access_token) {
        Auth.setTokens(data.access_token, null);
        return true;
      }
    } catch {}
    return false;
  },
};


// ── Toast Notifications ───────────────────────────────────────────

const Toast = {
  init() {
    if (document.getElementById('toast-container')) return;
    const el = document.createElement('div');
    el.id = 'toast-container';
    document.body.appendChild(el);
  },

  show(message, type = 'info', duration = 4000) {
    this.init();
    const container = document.getElementById('toast-container');
    const icons = {
      success: 'bi-check-circle-fill',
      error:   'bi-x-circle-fill',
      info:    'bi-info-circle-fill',
      warning: 'bi-exclamation-triangle-fill'
    };
    const toast = document.createElement('div');
    toast.className = `toast toast-${type === 'warning' ? 'info' : type}`;
    toast.innerHTML = `<i class="bi ${icons[type] || icons.info}" style="flex-shrink:0;margin-top:2px"></i><span>${message}</span>`;
    container.appendChild(toast);
    setTimeout(() => { if (toast.parentNode) toast.remove(); }, duration + 300);
  },

  success(msg) { this.show(msg, 'success'); },
  error(msg)   { this.show(msg, 'error'); },
  info(msg)    { this.show(msg, 'info'); },
};


// ── Password Strength Meter ───────────────────────────────────────

function initPasswordStrength(inputId, fillId, labelId) {
  const input = document.getElementById(inputId);
  const fill  = document.getElementById(fillId);
  const label = document.getElementById(labelId);
  if (!input || !fill) return;

  input.addEventListener('input', () => {
    const val = input.value;
    let score = 0;
    if (val.length >= 8)          score++;
    if (/[A-Z]/.test(val))        score++;
    if (/[a-z]/.test(val))        score++;
    if (/\d/.test(val))           score++;
    if (/[^A-Za-z0-9]/.test(val)) score++;

    const pct    = (score / 5) * 100;
    const colors = ['', '#f43f5e', '#f59e0b', '#f59e0b', '#10b981', '#10b981'];
    const labels = ['', 'Very weak', 'Weak', 'Fair', 'Strong', 'Very strong'];

    fill.style.width      = `${pct}%`;
    fill.style.background = colors[score] || 'transparent';
    if (label) label.textContent = val.length ? labels[score] : '';
  });
}


// ── Form Helpers ──────────────────────────────────────────────────

function showFieldError(fieldId, message) {
  const el  = document.getElementById(fieldId);
  const err = document.getElementById(`${fieldId}-error`);
  if (el)  el.classList.add('error');
  if (err) { err.textContent = message; err.classList.add('visible'); }
}

function clearFieldErrors() {
  document.querySelectorAll('.form-control.error').forEach(el => el.classList.remove('error'));
  document.querySelectorAll('.form-error.visible').forEach(el => el.classList.remove('visible'));
}

function setButtonLoading(btn, loading) {
  if (!btn) return;
  if (loading) {
    btn.classList.add('btn-loading');
    btn.disabled = true;
    btn.dataset.originalHtml = btn.innerHTML;
    btn.innerHTML = `<span class="btn-text">${btn.dataset.originalHtml}</span>`;
  } else {
    btn.classList.remove('btn-loading');
    btn.disabled = false;
    if (btn.dataset.originalHtml) btn.innerHTML = btn.dataset.originalHtml;
  }
}


// ── Password Toggle ───────────────────────────────────────────────

function initPasswordToggles() {
  document.querySelectorAll('[data-toggle-password]').forEach(btn => {
    btn.addEventListener('click', () => {
      const input = document.getElementById(btn.dataset.togglePassword);
      if (!input) return;
      const show = input.type === 'password';
      input.type  = show ? 'text' : 'password';
      btn.innerHTML = show
        ? '<i class="bi bi-eye-slash"></i>'
        : '<i class="bi bi-eye"></i>';
    });
  });
}


// ── Navigation Guards ─────────────────────────────────────────────

function guardRoute(requiresAuth = true, requiresAdmin = false) {
  const loggedIn = Auth.isLoggedIn();

  if (requiresAuth && !loggedIn) {
    window.location.href = '/login';
    return false;
  }
  if (!requiresAuth && loggedIn) {
    // Already logged in — redirect away from auth pages
    const user = Auth.getUser();
    window.location.href = (user && user.role === 'admin') ? '/admin' : '/dashboard';
    return false;
  }
  if (requiresAdmin && !Auth.isAdmin()) {
    window.location.href = '/access-denied';
    return false;
  }
  return true;
}


// ── Render User Info ──────────────────────────────────────────────

function renderUserInfo() {
  const user = Auth.getUser();
  if (!user) return;

  document.querySelectorAll('[data-user-name]').forEach(el => {
    el.textContent = user.full_name || user.username || 'User';
  });
  document.querySelectorAll('[data-user-email]').forEach(el => {
    el.textContent = user.email || '';
  });
  document.querySelectorAll('[data-user-role]').forEach(el => {
    el.textContent = user.role || 'user';
  });
  document.querySelectorAll('[data-user-avatar]').forEach(el => {
    const f = user.first_name ? user.first_name[0] : '';
    const l = user.last_name  ? user.last_name[0]  : (user.username ? user.username[0] : '?');
    el.textContent = (f + l).toUpperCase();
  });
}


// ── Logout ────────────────────────────────────────────────────────

async function logout() {
  try { await API.post('/auth/logout'); } catch {}
  Auth.clearTokens();
  Toast.success('Logged out successfully.');
  setTimeout(() => { window.location.href = '/login'; }, 800);
}


// ── Init on DOM Ready ─────────────────────────────────────────────

document.addEventListener('DOMContentLoaded', () => {
  initPasswordToggles();
  renderUserInfo();
  // Note: logout click is handled by base.html modal via event delegation
});
