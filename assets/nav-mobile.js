(function(){
  var nav = document.querySelector('.rw-nav');
  if (!nav) return;

  var btn = document.createElement('button');
  btn.className = 'rw-nav__hamburger';
  btn.type = 'button';
  btn.setAttribute('aria-label', 'Menu');
  btn.setAttribute('aria-expanded', 'false');
  btn.innerHTML = '<span></span><span></span><span></span>';

  var cta = nav.querySelector('.rw-nav__cta');
  if (cta) {
    nav.insertBefore(btn, cta);
  } else {
    nav.appendChild(btn);
  }

  btn.addEventListener('click', function(e){
    e.stopPropagation();
    var open = nav.classList.toggle('rw-nav--open');
    btn.classList.toggle('rw-nav__hamburger--open', open);
    btn.setAttribute('aria-expanded', open ? 'true' : 'false');
  });

  document.addEventListener('click', function(e){
    if (!nav.contains(e.target) && nav.classList.contains('rw-nav--open')) {
      nav.classList.remove('rw-nav--open');
      btn.classList.remove('rw-nav__hamburger--open');
      btn.setAttribute('aria-expanded', 'false');
    }
  });

  var links = nav.querySelectorAll('.rw-nav__links a');
  for (var i = 0; i < links.length; i++) {
    links[i].addEventListener('click', function(){
      nav.classList.remove('rw-nav--open');
      btn.classList.remove('rw-nav__hamburger--open');
      btn.setAttribute('aria-expanded', 'false');
    });
  }
})();
