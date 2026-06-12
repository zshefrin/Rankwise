(function(){
  var nav = document.querySelector('.rw-nav');
  if (!nav) return;

  var linksEl = nav.querySelector('.rw-nav__links');
  if (linksEl && !linksEl.id) linksEl.id = 'rw-nav-links';

  var btn = document.createElement('button');
  btn.className = 'rw-nav__hamburger';
  btn.type = 'button';
  btn.setAttribute('aria-label', 'Menu');
  btn.setAttribute('aria-expanded', 'false');
  if (linksEl) btn.setAttribute('aria-controls', linksEl.id);
  btn.innerHTML = '<span></span><span></span><span></span>';

  var cta = nav.querySelector('.rw-nav__cta');
  if (cta) {
    nav.insertBefore(btn, cta);
    cta.addEventListener('click', function(){
      if (typeof gtag !== 'function') return;
      gtag('event', 'nav_cta_clicked', {
        event_category: 'lead',
        event_label: 'global_nav',
        page_path: window.location.pathname,
        destination: cta.href
      });
    });
  } else {
    nav.appendChild(btn);
  }

  btn.addEventListener('click', function(e){
    e.stopPropagation();
    var open = nav.classList.toggle('rw-nav--open');
    btn.classList.toggle('rw-nav__hamburger--open', open);
    btn.setAttribute('aria-expanded', open ? 'true' : 'false');
  });

  function closeMenu(){
    nav.classList.remove('rw-nav--open');
    btn.classList.remove('rw-nav__hamburger--open');
    btn.setAttribute('aria-expanded', 'false');
  }

  document.addEventListener('click', function(e){
    if (!nav.contains(e.target) && nav.classList.contains('rw-nav--open')) {
      closeMenu();
    }
  });

  document.addEventListener('keydown', function(e){
    if (e.key === 'Escape' && nav.classList.contains('rw-nav--open')) {
      closeMenu();
      btn.focus();
    }
  });

  var links = nav.querySelectorAll('.rw-nav__links a');
  for (var i = 0; i < links.length; i++) {
    links[i].addEventListener('click', closeMenu);
  }

  // Fallback sticky-CTA sync for pages without their own (blog, lab, about).
  // Pages with booking embeds (home, audit, city pages) ship an inline sync
  // with proximity suppression and set window.__rwStickyCtaSync — defer to it,
  // otherwise this unsuppressed toggle overlays the CTA on the Cal.com embed.
  var stickyCta = document.querySelector('.mobile-sticky-cta');
  function syncStickyCta(){
    if (!stickyCta) return;
    var shouldShow = window.innerWidth <= 1000 && window.scrollY > window.innerHeight * 0.72;
    document.body.classList.toggle('show-mobile-cta', shouldShow);
  }

  if (stickyCta && !window.__rwStickyCtaSync) {
    window.__rwStickyCtaSync = true;
    syncStickyCta();
    window.addEventListener('scroll', syncStickyCta, { passive: true });
    window.addEventListener('resize', syncStickyCta);
  }
})();
