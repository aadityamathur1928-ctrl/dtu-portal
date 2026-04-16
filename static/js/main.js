// ── Sidebar mobile toggle ──────────────────────────────────
const sidebar     = document.getElementById('sidebar');
const menuToggle  = document.getElementById('menuToggle');
const overlay     = document.createElement('div');

if (sidebar && menuToggle) {
  overlay.style.cssText = `
    position:fixed; inset:0; background:rgba(0,0,0,0.5);
    z-index:99; display:none;
  `;
  document.body.appendChild(overlay);

  menuToggle.addEventListener('click', () => {
    sidebar.classList.toggle('open');
    overlay.style.display = sidebar.classList.contains('open') ? 'block' : 'none';
  });

  overlay.addEventListener('click', () => {
    sidebar.classList.remove('open');
    overlay.style.display = 'none';
  });
}

// ── Password visibility toggle ─────────────────────────────
function togglePassword(fieldId, btn) {
  const field = document.getElementById(fieldId);
  if (!field) return;
  const isPassword = field.type === 'password';
  field.type = isPassword ? 'text' : 'password';
  btn.style.color = isPassword ? 'var(--primary)' : 'var(--text-muted)';
}

// ── Auto-dismiss flash messages ────────────────────────────
document.querySelectorAll('.alert').forEach(alert => {
  setTimeout(() => {
    alert.style.opacity = '0';
    alert.style.transition = 'opacity 0.4s';
    setTimeout(() => alert.remove(), 400);
  }, 5000);
});

// ── Notice category filter ─────────────────────────────────
const tabBtns   = document.querySelectorAll('.tab-btn');
const notices   = document.querySelectorAll('.notice-card');

tabBtns.forEach(btn => {
  btn.addEventListener('click', () => {
    tabBtns.forEach(b => b.classList.remove('active'));
    btn.classList.add('active');

    const filter = btn.dataset.filter;
    notices.forEach(notice => {
      if (filter === 'all' || notice.dataset.category === filter) {
        notice.style.display = 'flex';
      } else {
        notice.style.display = 'none';
      }
    });
  });
});

// ── Highlight active nav on page load ─────────────────────
// (Handled by Jinja2 class injection, but ensure no flicker)

// ── Table row highlight for today's exam ──────────────────
document.querySelectorAll('.row-today').forEach(row => {
  row.style.background = 'var(--primary-bg)';
  row.style.fontWeight = '500';
});
