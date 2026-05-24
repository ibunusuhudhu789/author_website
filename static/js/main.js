// ============================================================
//  AUTHOR WEBSITE — SHARED JS
// ============================================================

/* ── Nav scroll effect ── */
window.addEventListener('scroll', () => {
  const nav = document.querySelector('.navbar');
  if (nav) nav.classList.toggle('scrolled', window.scrollY > 40);
});

/* ── Mobile toggle ── */
document.addEventListener('DOMContentLoaded', () => {
  const toggle = document.getElementById('navToggle');
  const links  = document.getElementById('navLinks');
  if (toggle && links) {
    toggle.addEventListener('click', () => {
      links.classList.toggle('open');
      const spans = toggle.querySelectorAll('span');
      spans[0].style.transform = links.classList.contains('open') ? 'rotate(45deg) translate(5px, 5px)' : '';
      spans[1].style.opacity   = links.classList.contains('open') ? '0' : '1';
      spans[2].style.transform = links.classList.contains('open') ? 'rotate(-45deg) translate(5px, -5px)' : '';
    });
    document.addEventListener('click', e => {
      if (!toggle.contains(e.target) && !links.contains(e.target)) {
        links.classList.remove('open');
        toggle.querySelectorAll('span').forEach(s => { s.style.transform = ''; s.style.opacity = ''; });
      }
    });
  }

  /* ── Active nav link ── */
  const page = location.pathname.split('/').pop() || 'index.html';
  document.querySelectorAll('.nav-links a').forEach(a => {
    if (a.getAttribute('href') === page) a.classList.add('active');
  });

  /* ── Intersection Observer (fade-up) ── */
  const obs = new IntersectionObserver(entries => {
    entries.forEach(e => {
      if (e.isIntersecting) { e.target.classList.add('animate-fadeup'); obs.unobserve(e.target); }
    });
  }, { threshold: 0.15 });
  document.querySelectorAll('[data-animate]').forEach(el => obs.observe(el));

/* ── Newsletter form ── */
  const nlForm = document.getElementById('newsletterForm');
  if (nlForm) {
    nlForm.addEventListener('submit', e => {
      e.preventDefault();
      const email = nlForm.querySelector('input[type="email"]').value;
      if (email) {
        fetch('/subscribers', {
          method: 'POST',
          headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
          body: `subscribers=${encodeURIComponent(email)}`
        })
        .then(res => res.json())
        .then(data => {
          nlForm.innerHTML = `<p style="color:rgba(255,255,255,0.8);font-family:var(--font-ui);font-size:0.9rem;">
            ✓ Thank you! You're now subscribed.
          </p>`;
        })
        .catch(err => console.error(err));
      }
    });
  }

}); // ← this closes the DOMContentLoaded block

/* ── Book filter ── */
function initBookFilter() {
  const btns  = document.querySelectorAll('.filter-btn');
  const cards = document.querySelectorAll('.book-card[data-genre]');
  if (!btns.length) return;
  btns.forEach(btn => {
    btn.addEventListener('click', () => {
      btns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      const genre = btn.dataset.filter;
      cards.forEach(c => {
        c.style.display = (genre === 'all' || c.dataset.genre === genre) ? '' : 'none';
      });
    });
  });
}

/* ── Contact form ── */
function initContactForm() {
  const form = document.getElementById('contactForm');
  if (!form) return;
  form.addEventListener('submit', e => {
    e.preventDefault();
    const btn = form.querySelector('button[type="submit"]');
    btn.disabled = true;
    btn.textContent = 'Sending…';
    setTimeout(() => {
      form.innerHTML = `
        <div class="alert alert-success" style="margin:0;">
          <span>✓</span>
          <span>Your message has been received! We'll get back to you within 2–3 business days.</span>
        </div>`;
    }, 1200);
  });
}

/* ── Auth forms (basic client validation) ── */
function initAuthForms() {
  const form = document.getElementById('authForm');
  if (!form) return;
  form.addEventListener('submit', e => {
    e.preventDefault();
    const btn = form.querySelector('button[type="submit"]');
    btn.disabled = true;
    btn.textContent = 'Please wait…';
    // Backend handles the rest
    setTimeout(() => { btn.disabled = false; btn.textContent = btn.dataset.label || 'Submit'; }, 2000);
  });
}

/* ── Order page type toggle ── */
function initOrderPage() {
  const params = new URLSearchParams(location.search);
  const type   = params.get('type') || 'physical';
  const typeEl = document.getElementById('orderType');
  const titleEl = document.getElementById('orderTitle');
  if (typeEl) typeEl.textContent = type === 'ebook' ? 'eBook' : 'Physical Book';
  if (titleEl) titleEl.textContent = type === 'ebook' ? 'eBook Download' : 'Physical Copy';
}

document.addEventListener('DOMContentLoaded', () => {
  initBookFilter();
  initContactForm();
  initAuthForms();
  initOrderPage();
});
