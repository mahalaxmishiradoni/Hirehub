/**
 * HireHub — Main JavaScript
 * Handles: auto-dismiss alerts, skills tag input, file drag-drop,
 * fetch-based API helpers, and general UI enhancements.
 */

/* ---- Auto-dismiss flash alerts ---- */
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.alert.alert-dismissible').forEach(alert => {
    setTimeout(() => {
      const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
      bsAlert?.close();
    }, 5000);
  });
});

/* ---- Active nav link highlight ---- */
document.addEventListener('DOMContentLoaded', () => {
  const path = window.location.pathname;
  document.querySelectorAll('.navbar .nav-link').forEach(link => {
    if (link.getAttribute('href') && path.startsWith(link.getAttribute('href')) && link.getAttribute('href') !== '/') {
      link.classList.add('active');
    }
  });
});

/* ---- Skills tag display helper ---- */
function renderSkillTags(inputId, containerId) {
  const input = document.getElementById(inputId);
  const container = document.getElementById(containerId);
  if (!input || !container) return;

  function update() {
    container.innerHTML = '';
    input.value.split(',').map(s => s.trim()).filter(Boolean).forEach(skill => {
      const tag = document.createElement('span');
      tag.className = 'badge bg-primary bg-opacity-10 text-primary skill-badge me-1';
      tag.textContent = skill;
      container.appendChild(tag);
    });
  }
  input.addEventListener('input', update);
  update();
}

/* ---- File drag-and-drop on upload area ---- */
document.addEventListener('DOMContentLoaded', () => {
  const dropzone = document.getElementById('dropzone');
  const fileInput = document.getElementById('resumeFile');
  if (!dropzone || !fileInput) return;

  dropzone.addEventListener('click', () => fileInput.click());

  dropzone.addEventListener('dragover', e => {
    e.preventDefault();
    dropzone.classList.add('bg-primary', 'bg-opacity-10');
  });
  dropzone.addEventListener('dragleave', () => {
    dropzone.classList.remove('bg-primary', 'bg-opacity-10');
  });
  dropzone.addEventListener('drop', e => {
    e.preventDefault();
    dropzone.classList.remove('bg-primary', 'bg-opacity-10');
    if (e.dataTransfer.files.length) {
      fileInput.files = e.dataTransfer.files;
      fileInput.dispatchEvent(new Event('change'));
    }
  });
});

/* ---- API helper functions (Fetch-based) ---- */
const HireHubAPI = {
  /**
   * Generic JSON request helper.
   */
  async request(method, url, body = null) {
    const opts = {
      method,
      headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
      credentials: 'same-origin',
    };
    if (body) opts.body = JSON.stringify(body);
    const res = await fetch(url, opts);
    return res.json();
  },

  get(url)         { return this.request('GET', url); },
  post(url, body)  { return this.request('POST', url, body); },
  put(url, body)   { return this.request('PUT', url, body); },
  delete(url)      { return this.request('DELETE', url); },

  /** Apply to a job via REST API and update UI without page reload */
  async applyJob(jobId) {
    const data = await this.post(`/api/jobs/${jobId}/apply`);
    return data;
  },

  /** Mark all notifications as read */
  async markAllNotificationsRead(userId) {
    return this.post('/api/applications'); // placeholder — actual endpoint is session-based
  },
};

/* ---- Confirmation dialogs ---- */
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('[data-confirm]').forEach(el => {
    el.addEventListener('click', e => {
      if (!confirm(el.dataset.confirm)) e.preventDefault();
    });
  });
});

/* ---- Tooltip initialisation ---- */
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(el => {
    new bootstrap.Tooltip(el);
  });
});

/* ---- Expose globally ---- */
window.HireHubAPI = HireHubAPI;
window.renderSkillTags = renderSkillTags;
