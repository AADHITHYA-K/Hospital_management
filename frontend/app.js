const API_BASE =
  (typeof window !== 'undefined' && window.location.origin && window.location.origin.startsWith('http'))
    ? window.location.origin
    : 'http://localhost:8000';

function getToken() {
  return localStorage.getItem('token');
}

function setToken(token) {
  if (token) localStorage.setItem('token', token);
  else localStorage.removeItem('token');
}

async function api(path, options = {}) {
  const url = `${API_BASE}${path}`;
  const headers = { 'Content-Type': 'application/json', ...options.headers };
  const token = getToken();
  if (token) headers['Authorization'] = `Bearer ${token}`;

  const res = await fetch(url, { ...options, headers });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    const msg = Array.isArray(data.detail)
      ? data.detail.map((d) => d.msg || d.loc?.join('.')).join(', ')
      : (typeof data.detail === 'string' ? data.detail : data.detail?.message) || res.statusText || 'Request failed';
    throw new Error(msg);
  }
  return data;
}

function showMessage(el, text, type = '') {
  const m = document.getElementById(el);
  if (!m) return;
  m.textContent = text;
  m.className = 'message ' + type;
}

function showToast(text, type = 'info') {
  const toast = document.getElementById('toast');
  if (toast) {
    toast.textContent = text;
    toast.className = 'toast toast-' + type;
    toast.classList.add('show');
    setTimeout(() => toast.classList.remove('show'), 3000);
  } else {
    alert(text);
  }
}

function showPage(id) {
  document.querySelectorAll('.page').forEach(p => p.style.display = 'none');
  const page = document.getElementById('page-' + id);
  if (page) page.style.display = 'block';
}

function setLoggedIn(user) {
  document.getElementById('header').style.display = 'flex';
  document.getElementById('page-login').style.display = 'none';
  document.getElementById('user-email').textContent = user?.email || '';
  document.getElementById('user-role').textContent = user?.role || '';
  const deptEl = document.getElementById('user-dept');
  if (deptEl) {
    if (user?.effective_department) {
      deptEl.textContent = 'Dept: ' + user.effective_department;
      deptEl.style.display = 'inline';
    } else {
      deptEl.style.display = 'none';
    }
  }
  const analyticsNav = document.getElementById('nav-analytics');
  const analyticsCard = document.getElementById('card-analytics');
  if (user?.role === 'Admin') {
    if (analyticsNav) analyticsNav.style.display = 'inline';
    if (analyticsCard) analyticsCard.style.display = 'block';
  } else {
    if (analyticsNav) analyticsNav.style.display = 'none';
    if (analyticsCard) analyticsCard.style.display = 'none';
  }
}

function setLoggedOut() {
  setToken(null);
  document.getElementById('header').style.display = 'none';
  document.getElementById('page-login').style.display = 'block';
  document.getElementById('form-login').style.display = 'block';
  document.getElementById('form-register').style.display = 'none';
  document.querySelector('.tab[data-tab="login"]').classList.add('active');
  document.querySelector('.tab[data-tab="register"]').classList.remove('active');
  showMessage('auth-message', '');
}

async function loadUser() {
  const token = getToken();
  if (!token) return null;
  try {
    const user = await api('/auth/me');
    setLoggedIn(user);
    return user;
  } catch {
    setLoggedOut();
    return null;
  }
}

// Tabs
document.querySelectorAll('.tab').forEach(t => {
  t.addEventListener('click', () => {
    const tab = t.dataset.tab;
    document.querySelectorAll('.tab').forEach(x => x.classList.remove('active'));
    t.classList.add('active');
    document.getElementById('form-login').style.display = tab === 'login' ? 'block' : 'none';
    document.getElementById('form-register').style.display = tab === 'register' ? 'block' : 'none';
    showMessage('auth-message', '');
  });
});

// Login
document.getElementById('form-login').addEventListener('submit', async (e) => {
  e.preventDefault();
  const fd = new FormData(e.target);
  try {
    const data = await api('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email: fd.get('email'), password: fd.get('password') }),
    });
    setToken(data.access_token);
    await loadUser();
    showMessage('auth-message', 'Logged in.', 'success');
    location.hash = '#/';
  } catch (err) {
    showMessage('auth-message', err.message || 'Login failed', 'error');
  }
});

// Register
document.getElementById('form-register').addEventListener('submit', async (e) => {
  e.preventDefault();
  const fd = new FormData(e.target);
  try {
    await api('/auth/register', {
      method: 'POST',
      body: JSON.stringify({
        name: fd.get('name'),
        email: fd.get('email'),
        password: fd.get('password'),
        role: fd.get('role'),
      }),
    });
    showMessage('auth-message', 'Registered. Please log in.', 'success');
  } catch (err) {
    showMessage('auth-message', err.message || 'Registration failed', 'error');
  }
});

// Logout
document.getElementById('logout-btn').addEventListener('click', () => {
  setLoggedOut();
});

// Router
function route() {
  const hash = (location.hash || '#/').slice(2) || 'dashboard';
  const page = hash.split('/')[0] || 'dashboard';
  showPage(page);

  const detailPanel = document.getElementById('request-detail');
  if (detailPanel) detailPanel.style.display = 'none';

  if (page === 'patients') loadPatients();
  else if (page === 'requests') loadRequests();
  else if (page === 'tasks') loadTasks();
  else if (page === 'workflows') loadWorkflows();
  else if (page === 'analytics') loadAnalytics();
}

window.addEventListener('hashchange', route);
window.addEventListener('load', async () => {
  const user = await loadUser();
  if (user) route();
  else showPage('login');
});

// Patients
async function loadPatients() {
  try {
    const list = await api('/patients/');
    const tbody = document.getElementById('patients-tbody');
    tbody.innerHTML = list.map(p => `
      <tr>
        <td>${p.id}</td>
        <td>${p.name}</td>
        <td>${p.age}</td>
        <td>${p.gender}</td>
        <td>${p.contact}</td>
      </tr>
    `).join('');
  } catch (err) {
    document.getElementById('patients-tbody').innerHTML = `<tr><td colspan="5">${err.message}</td></tr>`;
  }
}

document.getElementById('btn-new-patient').addEventListener('click', () => {
  document.getElementById('modal-patient').classList.add('open');
});

document.getElementById('modal-patient').addEventListener('click', (e) => {
  if (e.target.id === 'modal-patient') e.target.classList.remove('open');
});

document.getElementById('form-patient').addEventListener('submit', async (e) => {
  e.preventDefault();
  const fd = new FormData(e.target);
  try {
    await api('/patients/', {
      method: 'POST',
      body: JSON.stringify({
        name: fd.get('name'),
        age: parseInt(fd.get('age'), 10),
        gender: fd.get('gender'),
        contact: fd.get('contact'),
      }),
    });
    document.getElementById('modal-patient').classList.remove('open');
    e.target.reset();
    loadPatients();
  } catch (err) {
    showToast(err.message || 'Failed to create patient', 'error');
  }
});

// Requests
async function loadRequests() {
  try {
    const list = await api('/requests/');
    const tbody = document.getElementById('requests-tbody');
    tbody.innerHTML = list.map(r => `
      <tr>
        <td>${r.id}</td>
        <td>${r.patient_id}</td>
        <td>${r.request_type}</td>
        <td>${r.current_department}</td>
        <td>${r.status}</td>
        <td>${r.priority || 'Normal'}</td>
        <td>
          <button type="button" class="btn btn-ghost" data-request-id="${r.id}">View</button>
        </td>
      </tr>
    `).join('');
    tbody.querySelectorAll('[data-request-id]').forEach(btn => {
      btn.addEventListener('click', () => showRequestDetail(parseInt(btn.dataset.requestId, 10)));
    });
  } catch (err) {
    document.getElementById('requests-tbody').innerHTML = `<tr><td colspan="7">${err.message}</td></tr>`;
  }
}

async function showRequestDetail(requestId) {
  const panel = document.getElementById('request-detail');
  panel.style.display = 'block';
  document.getElementById('detail-request-id').textContent = requestId;

  try {
    const [req, status, tasks, audit] = await Promise.all([
      api(`/requests/${requestId}`),
      api(`/requests/${requestId}/status`),
      api(`/requests/${requestId}/tasks`),
      api(`/audit/request/${requestId}`),
    ]);

    document.getElementById('detail-status').innerHTML = `
      <p><strong>Current department:</strong> ${status.current_department} &nbsp; <strong>Status:</strong> ${status.status}</p>
      <p>Steps: ${status.steps_completed} / ${status.total_steps}</p>
    `;

    document.getElementById('detail-tasks').innerHTML = `
      <strong>Task history</strong>
      <ul>${tasks.map(t => `
        <li>${t.department}: ${t.status}
          ${t.completed_at ? ` (completed ${t.completed_at})` : ''}
          ${t.sla_breached ? ' ⚠ SLA breached' : ''}
        </li>
      `).join('')}</ul>
    `;

    document.getElementById('detail-audit').innerHTML = `
      <strong>Audit log</strong>
      <ul>${audit.map(a => `<li>${a.timestamp} – ${a.action} by ${a.performed_by} (${a.department})</li>`).join('')}</ul>
    `;

    const user = await api('/auth/me');
    const completeBtn = document.getElementById('btn-complete-task');
    const restrictionEl = document.getElementById('detail-restriction');
    const canComplete =
      req.status !== 'Completed' &&
      user.effective_department &&
      req.current_department === user.effective_department;
    if (canComplete) {
      completeBtn.style.display = 'inline-block';
      completeBtn.onclick = () => completeRequest(requestId);
      if (restrictionEl) restrictionEl.style.display = 'none';
    } else {
      completeBtn.style.display = 'none';
      if (restrictionEl && req.status !== 'Completed') {
        restrictionEl.textContent =
          user.effective_department
            ? `Only ${req.current_department} department can complete this task. (Your dept: ${user.effective_department})`
            : `Only ${req.current_department} department can complete this task.`;
        restrictionEl.style.display = 'block';
      }
    }
  } catch (err) {
    document.getElementById('detail-status').textContent = err.message;
  }
}

async function completeRequest(requestId) {
  try {
    const data = await api(`/requests/${requestId}/complete`, { method: 'POST' });
    showToast(data.message, 'success');
    showRequestDetail(requestId);
    loadRequests();
    loadTasks();
  } catch (err) {
    showToast(err.message || 'Failed to complete', 'error');
  }
}

document.getElementById('btn-new-request').addEventListener('click', async () => {
  try {
    const patients = await api('/patients/');
    const sel = document.getElementById('request-patient-id');
    if (!patients.length) {
      showToast('Create a patient first in the Patients section', 'error');
      return;
    }
    sel.innerHTML = patients.map(p => `<option value="${p.id}">${p.name} (ID ${p.id})</option>`).join('');
  } catch (err) {
    showToast(err.message || 'Failed to load patients', 'error');
    return;
  }
  document.getElementById('modal-request').classList.add('open');
});

document.getElementById('modal-request').addEventListener('click', (e) => {
  if (e.target.id === 'modal-request') e.target.classList.remove('open');
});

document.getElementById('form-request').addEventListener('submit', async (e) => {
  e.preventDefault();
  const fd = new FormData(e.target);
  try {
    await api('/requests/', {
      method: 'POST',
      body: JSON.stringify({
        patient_id: parseInt(fd.get('patient_id'), 10),
        request_type: fd.get('request_type'),
        priority: fd.get('priority') || 'Normal',
      }),
    });
    document.getElementById('modal-request').classList.remove('open');
    e.target.reset();
    loadRequests();
  } catch (err) {
    showToast(err.message || 'Failed to create request', 'error');
  }
});

// Tasks
async function loadTasks() {
  try {
    const list = await api('/tasks/my-tasks');
    const tbody = document.getElementById('tasks-tbody');
    tbody.innerHTML = list.map(t => `
      <tr>
        <td>${t.id}</td>
        <td>${t.request_id}</td>
        <td>${t.department}</td>
        <td>${t.status}</td>
        <td>${t.created_at || '-'}</td>
        <td><button type="button" class="btn btn-primary" data-request-id="${t.request_id}">Complete</button></td>
      </tr>
    `).join('');
    tbody.querySelectorAll('[data-request-id]').forEach(btn => {
      btn.addEventListener('click', () => completeRequest(parseInt(btn.dataset.requestId, 10)));
    });
  } catch (err) {
    document.getElementById('tasks-tbody').innerHTML = `<tr><td colspan="6">${err.message}</td></tr>`;
  }
}

// Workflows
async function loadWorkflows() {
  try {
    const data = await api('/workflows/definitions');
    const div = document.getElementById('workflows-content');
    let html = '<h4>Workflows</h4>';
    for (const [name, steps] of Object.entries(data.workflows)) {
      html += `<div class="workflow-row"><strong>${name}</strong> <span class="workflow-steps">${steps.join(' → ')}</span></div>`;
    }
    html += '<h4>SLA limits (seconds)</h4><ul class="sla-list">';
    for (const [dept, sec] of Object.entries(data.sla_limits_seconds)) {
      html += `<li>${dept}: ${sec}s</li>`;
    }
    html += '</ul>';
    div.innerHTML = html;
  } catch (err) {
    document.getElementById('workflows-content').innerHTML = `<p class="message error">${err.message}</p>`;
  }
}

// Analytics
async function loadAnalytics() {
  try {
    const list = await api('/analytics/department-performance');
    const tbody = document.getElementById('analytics-tbody');
    tbody.innerHTML = list.map(r => `
      <tr>
        <td>${r.department}</td>
        <td>${r.total_tasks}</td>
        <td>${r.completed_tasks}</td>
        <td>${r.avg_completion_time_seconds}</td>
        <td>${r.sla_breaches}</td>
      </tr>
    `).join('');
  } catch (err) {
    document.getElementById('analytics-tbody').innerHTML = `<tr><td colspan="5">${err.message}</td></tr>`;
  }
}
