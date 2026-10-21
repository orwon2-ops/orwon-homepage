(function () {
  var root = document.documentElement;
  root.classList.add('js');
  var reduce = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
  var hasIO = 'IntersectionObserver' in window;
  var play = function (v, src) {
    if (!v.getAttribute('src')) v.src = src;
    var p = v.play();
    if (p && p.catch) p.catch(function () {});
  };

  // header: transparent over the hero, solid after scrolling or with the menu open
  var hdr = document.querySelector('.hdr');
  var menuBtn = document.querySelector('.menu-btn');
  var mnav = document.getElementById('mnav');
  function syncHeader() {
    var open = menuBtn.getAttribute('aria-expanded') === 'true';
    hdr.classList.toggle('solid', open || window.scrollY > 24);
  }
  function setMenu(open) {
    menuBtn.setAttribute('aria-expanded', String(open));
    menuBtn.setAttribute('aria-label', open ? '메뉴 닫기' : '메뉴 열기');
    mnav.hidden = !open;
    syncHeader();
  }
  window.addEventListener('scroll', syncHeader, { passive: true });
  menuBtn.addEventListener('click', function () { setMenu(menuBtn.getAttribute('aria-expanded') !== 'true'); });
  mnav.addEventListener('click', function (e) { if (e.target.closest('a')) setMenu(false); });
  window.addEventListener('resize', function () { if (window.innerWidth > 960) setMenu(false); });
  syncHeader();

  // videos: load and play only while on screen
  var vids = document.querySelectorAll('video[data-src]');
  if (!reduce) {
    if (hasIO) {
      var vio = new IntersectionObserver(function (es) {
        es.forEach(function (e) {
          if (e.isIntersecting) play(e.target, e.target.dataset.src);
          else if (!e.target.paused) e.target.pause();
        });
      }, { rootMargin: '160px 0px' });
      vids.forEach(function (v) { vio.observe(v); });
    } else {
      vids.forEach(function (v) { play(v, v.dataset.src); });
    }
  }

  // things measured while their tab was hidden get measured again when it opens
  var onShow = [];

  // people walls (sponsored creators, ad actors): while a section is pinned, each bit of scroll drops in one more person
  var coarse = window.matchMedia && matchMedia('(pointer: coarse)').matches;
  var pin = function (sec) {
    var stage = sec.querySelector('.cases-stage');
    var grid = sec.querySelector('.cases-grid');
    var all = Array.prototype.slice.call(grid.querySelectorAll('.ct'));
    var STEP = 44;
    var list = [], shown = -1, inView = !hasIO, start = 0, top = 0, pad = 0, ticking = false;
    var sync = function () {
      list.forEach(function (t) {
        var v = t.querySelector('video');
        if (!v) return;
        if (t.classList.contains('on') && inView) play(v, v.dataset.csrc);
        else if (!v.paused) v.pause();
      });
    };
    var update = function () {
      ticking = false;
      var scrolled = top - sec.getBoundingClientRect().top - pad;
      var n = Math.max(0, Math.min(list.length, Math.ceil((scrolled - start) / STEP)));
      if (n === shown) return;
      shown = n;
      list.forEach(function (t, i) { t.classList.toggle('on', i < n); });
      sync();
    };
    var layout = function () {
      grid.style.maxWidth = '';
      sec.style.height = '';
      list = all.filter(function (t) { return t.offsetParent !== null; })
        .sort(function (a, b) { return a.dataset.o - b.dataset.o; });
      var vh = window.innerHeight, hh = hdr.offsetHeight;
      var avail = vh - hh - 12;
      pad = parseFloat(getComputedStyle(sec).paddingTop) || 0;
      // phone layout: the heading sits above the wall in one column
      var stacked = window.innerWidth < 720;
      var h = stage.offsetHeight;
      var shrink = function (need, min) { // narrow the grid until the stage is `need` px shorter
        var gw = grid.offsetWidth, gh = grid.offsetHeight;
        grid.style.maxWidth = Math.floor(gw * Math.max(min, (gh - need) / gh)) + 'px';
        h = stage.offsetHeight;
      };
      if (h > avail && !stacked) shrink(h - avail, 0.62);
      if (h <= avail + 2) {
        top = hh + 6 + Math.round((avail - h) / 2);
      } else {
        // keep every face on screen; the heading above was read on the way in
        if (h - grid.offsetTop > avail) shrink(h - grid.offsetTop - avail, 0.5);
        var a = grid.offsetTop;
        top = h - a <= avail ? hh + 6 - a : vh - h;
      }
      stage.style.top = top + 'px';
      start = -Math.round(vh * 0.3);
      sec.style.height = (pad + h + Math.max(0, list.length * STEP + start + Math.round(vh * 0.35))) + 'px';
      shown = -1;
      update();
    };
    window.addEventListener('scroll', function () {
      if (!ticking) { ticking = true; requestAnimationFrame(update); }
    }, { passive: true });
    var rt, lw = window.innerWidth, lh = window.innerHeight;
    window.addEventListener('resize', function () {
      var w = window.innerWidth, vh = window.innerHeight;
      if (coarse && w === lw && Math.abs(vh - lh) < 160) return; // phone toolbars sliding in and out
      lw = w; lh = vh;
      clearTimeout(rt); rt = setTimeout(layout, 120);
    });
    layout();
    onShow.push(layout);
    window.addEventListener('load', layout);
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(layout);
    if (hasIO) {
      new IntersectionObserver(function (es) { inView = es[0].isIntersecting; sync(); }, { rootMargin: '80px 0px' }).observe(sec);
    }
  };
  if (!reduce) {
    root.classList.add('cases-on');
    document.querySelectorAll('.cases').forEach(pin);
  }

  // stars over the space opening on the home tab: they twinkle and drift while the hero is on screen
  (function () {
    var c = document.querySelector('.starfield');
    if (!c || !c.getContext) return function () {};
    var ctx = c.getContext('2d'), dots = [], w = 0, h = 0, raf = 0, on = !hasIO;
    var dpr = Math.min(window.devicePixelRatio || 1, 2);
    var moving = function () { return on && !reduce; };
    var draw = function (time) {
      var move = moving();
      ctx.clearRect(0, 0, w, h);
      for (var i = 0; i < dots.length; i++) {
        var p = dots[i];
        if (move) { p.x -= p.s * p.r * 0.35; if (p.x < -2) p.x = w + 2; }
        ctx.globalAlpha = move ? p.a * (0.65 + 0.35 * Math.sin(time / 900 + p.t)) : p.a;
        ctx.fillStyle = p.r > 1.1 ? '#cfe6ff' : '#fff';
        ctx.beginPath(); ctx.arc(p.x, p.y, p.r, 0, 6.2832); ctx.fill();
      }
      ctx.globalAlpha = 1;
    };
    // new stars whenever the hero changes size (a hidden tab measures 0, so this also runs when home opens)
    var size = function () {
      var r = c.getBoundingClientRect();
      if (!r.width || (r.width === w && r.height === h)) return;
      w = r.width; h = r.height;
      c.width = Math.round(w * dpr); c.height = Math.round(h * dpr);
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      dots = [];
      for (var n = Math.round(w * h / 9000); n > 0; n--) {
        dots.push({ x: Math.random() * w, y: Math.random() * h, r: Math.random() * 1.25 + 0.25, a: Math.random() * 0.6 + 0.25, t: Math.random() * 6.28, s: Math.random() * 0.25 + 0.05 });
      }
      draw(0);
    };
    var loop = function (t) { raf = 0; draw(t); if (moving()) raf = requestAnimationFrame(loop); };
    var sync = function () {
      size();
      if (moving()) { if (!raf) raf = requestAnimationFrame(loop); }
      else { cancelAnimationFrame(raf); raf = 0; draw(0); }
    };
    var rt;
    window.addEventListener('resize', function () { clearTimeout(rt); rt = setTimeout(sync, 150); });
    if (hasIO) new IntersectionObserver(function (es) { on = es[0].isIntersecting; sync(); }).observe(c);
    onShow.push(sync);
    sync();
    return sync;
  })();

  // tabs: each menu item is its own page in this one file, picked by the address hash
  var pages = Array.prototype.slice.call(document.querySelectorAll('.page'));
  var home = document.getElementById('home');
  var tabLinks = Array.prototype.slice.call(document.querySelectorAll('.nav a, .mnav a, .ftr-links a'));
  var baseTitle = document.title;
  var current = null;
  // scroll to the top (y = 0) or to an element; anything but a same-tab click lands at once
  var jump = function (to, smooth) {
    root.style.scrollBehavior = smooth ? '' : 'auto';
    if (typeof to === 'number') window.scrollTo({ top: to, behavior: smooth ? 'smooth' : 'auto' });
    else to.scrollIntoView({ block: 'start', behavior: smooth ? 'smooth' : 'auto' });
    root.style.scrollBehavior = '';
  };
  // [page, element inside it] for a hash, or null when it points outside the pages (#top, #main)
  var resolve = function (hash) {
    var id = (hash || '').replace(/^#/, '');
    try { id = decodeURIComponent(id); } catch (e) {}
    var el = id && document.getElementById(id);
    if (!el) return [home, null];
    var page = el.closest('.page');
    return page ? [page, el === page ? null : el] : null;
  };
  var show = function (hash, how) {
    var hit = resolve(hash);
    if (!hit) return false;
    var page = hit[0], el = hit[1], changed = page !== current;
    if (changed) {
      // the space opening plays once; coming back to home shows it settled
      if (current === home) root.classList.add('cosmos-seen');
      pages.forEach(function (p) { p.hidden = p !== page; });
      current = page;
      tabLinks.forEach(function (a) {
        if (a.getAttribute('href') === '#' + page.id) a.setAttribute('aria-current', 'page');
        else a.removeAttribute('aria-current');
      });
      var t = page.getAttribute('data-title');
      document.title = t ? t + ' | ' + baseTitle : baseTitle;
      onShow.forEach(function (f) { f(); });
      jump(0);
    }
    if (el) jump(el, !changed && how === 'click' && !reduce);
    else if (!changed && how === 'click') jump(0, !reduce);
    if (changed && how === 'click') {
      var h = page.querySelector('h1');
      if (h) { h.setAttribute('tabindex', '-1'); h.focus({ preventScroll: true }); }
    }
    syncHeader();
    return true;
  };
  document.addEventListener('click', function (e) {
    var a = e.target.closest && e.target.closest('a[href^="#"]');
    if (!a || e.defaultPrevented || e.button || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
    var hash = a.getAttribute('href');
    if (hash === '#' || !resolve(hash)) return;
    e.preventDefault();
    show(hash, 'click');
    try { history.pushState(null, '', hash === '#home' ? location.href.split('#')[0] : hash); } catch (err) {}
  });
  window.addEventListener('popstate', function () { show(location.hash, 'pop'); });
  window.addEventListener('hashchange', function () { show(location.hash, 'pop'); });
  try { history.scrollRestoration = 'manual'; } catch (e) {}
  show(location.hash, 'load');
  root.classList.add('routed');

  // inquiry form: on the site it goes to Web3Forms, which mails it to kim@orwon.kr; the preview has no key and only shows the done screen
  var form = document.getElementById('propose');
  var done = document.getElementById('done');
  var fail = form.querySelector('.f-err');
  var send = form.querySelector('.f-submit');
  var finish = function () {
    form.hidden = true;
    done.hidden = false;
    done.focus();
  };
  form.addEventListener('submit', function (e) {
    e.preventDefault();
    if (!form.reportValidity()) return;
    var key = form.getAttribute('data-key');
    var f = form.elements;
    if (!key || f.botcheck.checked) { finish(); return; }
    if (send.disabled) return;
    var who = f.company.value.trim(), reach = f.contact.value.trim();
    var data = {
      access_key: key,
      subject: '[오르원 홈페이지] 제품 제안: ' + who,
      from_name: '오르원 홈페이지',
      '회사명 또는 성함': who,
      '연락처': reach,
      '제품 소개': f.message.value.trim(),
      '개인정보 수집과 이용': '동의함'
    };
    if (/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(reach)) data.replyto = reach;
    fail.hidden = true;
    send.disabled = true;
    var label = send.textContent;
    send.textContent = '보내는 중입니다';
    fetch('https://api.web3forms.com/submit', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify(data)
    }).then(function (r) {
      return r.json().catch(function () { return {}; }).then(function (j) {
        if (!r.ok || !j.success) throw new Error(j.message || 'HTTP ' + r.status);
      });
    }).then(finish, function () {
      fail.hidden = false;
    }).then(function () {
      send.disabled = false;
      send.textContent = label;
    });
  });
  document.getElementById('again').addEventListener('click', function () {
    form.reset();
    fail.hidden = true;
    done.hidden = true;
    form.hidden = false;
  });

  var yr = document.getElementById('yr');
  if (yr) yr.textContent = new Date().getFullYear();
})();
