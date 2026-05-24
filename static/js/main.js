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

});