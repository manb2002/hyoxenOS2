// ============================================================
//  HYOXEN · Frontend JavaScript
//  Custom cursor, scroll reveals, animated counters,
//  live stats polling, India map dots, newsletter form
// ============================================================

(function () {
  'use strict';

  // ----------------------------------------------------------
  //  Custom cursor (desktop only)
  // ----------------------------------------------------------
  const cursor = document.querySelector('.cursor');
  const cursorDot = document.querySelector('.cursor-dot');

  if (cursor && window.matchMedia('(min-width: 900px)').matches) {
    let mouseX = 0, mouseY = 0;
    let cursorX = 0, cursorY = 0;

    document.addEventListener('mousemove', (e) => {
      mouseX = e.clientX;
      mouseY = e.clientY;
      cursorDot.style.transform = `translate(${mouseX}px, ${mouseY}px) translate(-50%, -50%)`;
    });

    function animateCursor() {
      cursorX += (mouseX - cursorX) * 0.18;
      cursorY += (mouseY - cursorY) * 0.18;
      cursor.style.transform = `translate(${cursorX}px, ${cursorY}px) translate(-50%, -50%)`;
      requestAnimationFrame(animateCursor);
    }
    animateCursor();

    // Hover state for interactive elements
    document.querySelectorAll('a, button, .product-card, .pillar, .join-card, .chip, input, textarea').forEach((el) => {
      el.addEventListener('mouseenter', () => cursor.classList.add('is-hover'));
      el.addEventListener('mouseleave', () => cursor.classList.remove('is-hover'));
    });
  }

  // ----------------------------------------------------------
  //  Nav scroll state
  // ----------------------------------------------------------
  const nav = document.getElementById('nav');
  if (nav) {
    window.addEventListener('scroll', () => {
      if (window.scrollY > 60) nav.classList.add('scrolled');
      else nav.classList.remove('scrolled');
    }, { passive: true });
  }

  // ----------------------------------------------------------
  //  Reveal on scroll
  // ----------------------------------------------------------
  const revealObserver = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add('in');
        revealObserver.unobserve(entry.target);
      }
    });
  }, { threshold: 0.12, rootMargin: '0px 0px -80px 0px' });

  document.querySelectorAll('.reveal, .reveal-children').forEach((el) => {
    revealObserver.observe(el);
  });

  // ----------------------------------------------------------
  //  Animated counters (data-stat attribute)
  // ----------------------------------------------------------
  function formatNumber(n, format) {
    if (format === 'millions') {
      return (n / 1000000).toFixed(1) + 'M';
    }
    return Math.floor(n).toLocaleString('en-IN');
  }

  function animateCounter(el, target, format) {
    const duration = 1800;
    const start = performance.now();
    const startVal = 0;

    function tick(now) {
      const progress = Math.min((now - start) / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      const value = startVal + (target - startVal) * eased;
      el.textContent = formatNumber(value, format);
      if (progress < 1) requestAnimationFrame(tick);
    }
    requestAnimationFrame(tick);
  }

  // Trigger counters when they enter view, fetching live data from Flask
  const counterEls = document.querySelectorAll('[data-stat]');
  const counterObserver = new IntersectionObserver((entries) => {
    entries.forEach(async (entry) => {
      if (entry.isIntersecting && !entry.target.dataset.animated) {
        entry.target.dataset.animated = 'true';
        try {
          const res = await fetch('/api/stats');
          const stats = await res.json();
          counterEls.forEach((el) => {
            const key = el.dataset.stat;
            const format = el.dataset.format;
            if (stats[key] !== undefined) {
              animateCounter(el, stats[key], format);
            }
          });
        } catch (err) {
          // Fallback: animate using default placeholder values
          counterEls.forEach((el) => {
            const fallback = {
              vehicles_streaming: 12847,
              battery_cells: 6200000,
              km_today: 84310,
              co2_avoided: 312,
              active_stations: 412,
              swaps_this_month: 84210,
            };
            const key = el.dataset.stat;
            if (fallback[key]) animateCounter(el, fallback[key], el.dataset.format);
          });
        }
        counterObserver.disconnect();
      }
    });
  }, { threshold: 0.3 });

  if (counterEls.length) {
    counterObserver.observe(counterEls[0].closest('section') || counterEls[0]);
  }

  // ----------------------------------------------------------
  //  Hero "vehicles streaming" live ticker
  // ----------------------------------------------------------
  const heroVeh = document.getElementById('hero-vehicles');
  if (heroVeh) {
    let base = 12847;
    setInterval(() => {
      base += Math.floor(Math.random() * 4) + 1;
      heroVeh.textContent = base.toLocaleString('en-IN');
    }, 5000);
  }

  // ----------------------------------------------------------
  //  India map — generate scatter dots + flashing
  // ----------------------------------------------------------
  const indiaDots = document.getElementById('india-dots');
  if (indiaDots) {
    // Approximate India outline polygon
    const indiaPath = [
      [200, 30], [240, 40], [280, 70], [310, 120], [330, 160],
      [320, 200], [310, 240], [290, 290], [260, 340], [230, 380],
      [200, 400], [170, 380], [140, 340], [120, 290], [110, 240],
      [100, 200], [110, 160], [130, 120], [160, 80], [180, 50]
    ];

    function pointInPolygon(x, y, poly) {
      let inside = false;
      for (let i = 0, j = poly.length - 1; i < poly.length; j = i++) {
        const xi = poly[i][0], yi = poly[i][1];
        const xj = poly[j][0], yj = poly[j][1];
        const intersect = ((yi > y) !== (yj > y)) &&
                          (x < (xj - xi) * (y - yi) / (yj - yi) + xi);
        if (intersect) inside = !inside;
      }
      return inside;
    }

    const svgNS = 'http://www.w3.org/2000/svg';
    const dots = [];
    for (let y = 30; y < 420; y += 8) {
      for (let x = 100; x < 340; x += 8) {
        if (pointInPolygon(x, y, indiaPath)) {
          const c = document.createElementNS(svgNS, 'circle');
          c.setAttribute('cx', x);
          c.setAttribute('cy', y);
          c.setAttribute('r', '1');
          c.setAttribute('class', 'dot');
          c.setAttribute('fill', 'rgba(255,255,255,0.15)');
          indiaDots.appendChild(c);
          dots.push(c);
        }
      }
    }

    // Random flash a few dots in Ion blue
    setInterval(() => {
      const idx = Math.floor(Math.random() * dots.length);
      const dot = dots[idx];
      dot.setAttribute('fill', '#00D4FF');
      dot.style.filter = 'drop-shadow(0 0 4px #00D4FF)';
      setTimeout(() => {
        dot.setAttribute('fill', 'rgba(255,255,255,0.15)');
        dot.style.filter = '';
      }, 1200);
    }, 250);
  }

  // ----------------------------------------------------------
  //  Newsletter form
  // ----------------------------------------------------------
  const newsletterForm = document.getElementById('newsletter-form');
  if (newsletterForm) {
    newsletterForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const formData = new FormData(newsletterForm);
      const email = formData.get('email');
      const msg = document.getElementById('newsletter-msg');
      msg.textContent = 'Subscribing...';
      try {
        const res = await fetch('/api/subscribe', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email })
        });
        const json = await res.json();
        msg.textContent = json.ok ? '✓ ' + json.message : '✗ ' + (json.error || 'Error');
        if (json.ok) newsletterForm.reset();
      } catch (err) {
        msg.textContent = '✗ Network error.';
      }
    });
  }

  // ----------------------------------------------------------
  //  Smooth anchor scrolling
  // ----------------------------------------------------------
  document.querySelectorAll('a[href^="#"]').forEach((link) => {
    link.addEventListener('click', (e) => {
      const href = link.getAttribute('href');
      if (href === '#' || href.length < 2) return;
      const target = document.querySelector(href);
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });

})();
