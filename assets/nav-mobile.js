(function(){
  var nav = document.querySelector('nav');
  if (!nav) return;

  var btn = document.createElement('button');
  btn.className = 'nav-hamburger';
  btn.setAttribute('aria-label', 'Menu');
  btn.setAttribute('aria-expanded', 'false');
  btn.innerHTML = '<span></span><span></span><span></span>';

  var cta = nav.querySelector('.nav-cta');
  if (cta) {
    nav.insertBefore(btn, cta);
  } else {
    nav.appendChild(btn);
  }

  btn.addEventListener('click', function(e){
    e.stopPropagation();
    var open = nav.classList.toggle('nav-open');
    btn.setAttribute('aria-expanded', open ? 'true' : 'false');
  });

  document.addEventListener('click', function(e){
    if (!nav.contains(e.target) && nav.classList.contains('nav-open')) {
      nav.classList.remove('nav-open');
      btn.setAttribute('aria-expanded', 'false');
    }
  });

  var links = nav.querySelectorAll('.nav-links a');
  for (var i = 0; i < links.length; i++) {
    links[i].addEventListener('click', function(){
      nav.classList.remove('nav-open');
      btn.setAttribute('aria-expanded', 'false');
    });
  }
})();
