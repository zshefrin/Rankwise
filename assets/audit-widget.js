/* Instant audit widget — hero search bar → Places lookup → specimen scorecard.
   Progressive enhancement: the static booking CTA stays in the hero markup;
   this script only adds the widget UI, and every failure path degrades to the
   booking link. Endpoint = Supabase Edge Function `instant-audit`. */
(function () {
  "use strict";
  var mount = document.getElementById("audit-widget");
  if (!mount || !window.fetch) return;
  var ENDPOINT = mount.getAttribute("data-endpoint");
  if (!ENDPOINT) return;
  // Cloudflare Turnstile — inert until the operator sets the site key here
  // AND TURNSTILE_SECRET on the Edge Function (the two must ship together;
  // the function only gates the audit action, search stays type-and-go).
  var TS_SITEKEY = mount.getAttribute("data-turnstile-sitekey") || "";
  var tsWidgetId = null;

  var BOOK_URL = "/audit/?utm_source=home&utm_medium=widget&utm_content=";
  var INTERNAL = document.cookie.split(";").some(function (c) {
    return c.trim() === "internal_traffic=true";
  });

  function track(name, params) {
    if (typeof window.rwTrack === "function") window.rwTrack(name, params);
  }
  function el(tag, cls, text) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text) n.textContent = text;
    return n;
  }
  function bookLink(label, content) {
    var a = el("a", "btn-primary", label);
    a.href = BOOK_URL + encodeURIComponent(content);
    a.addEventListener("click", function () {
      track("audit_booking", { cta_location: "widget-" + content });
    });
    return a;
  }

  // --- build the search UI ---------------------------------------------
  var wrap = el("div", "aw");
  var label = el("div", "aw-label");
  label.appendChild(document.createTextNode("Instant profile check · "));
  label.appendChild(el("span", "aw-free", "free — no email, 20 seconds"));
  var form = el("form", "aw-form");
  var input = el("input", "aw-input");
  input.type = "text";
  input.name = "q";
  input.autocomplete = "organization";
  input.maxLength = 120;
  input.placeholder = "Your company name — e.g. “Acme Heating, Surrey”";
  input.setAttribute("aria-label", "Search your business to run a free instant profile check");
  var btn = el("button", "aw-btn", "Run the check");
  btn.type = "submit";
  form.appendChild(input);
  form.appendChild(btn);
  var out = el("div");
  out.setAttribute("aria-live", "polite");
  wrap.appendChild(label);
  wrap.appendChild(form);
  wrap.appendChild(out);
  mount.appendChild(wrap);

  if (TS_SITEKEY) {
    window.__awTsReady = function () {
      var holder = el("div", "aw-ts");
      wrap.appendChild(holder);
      tsWidgetId = window.turnstile.render(holder, {
        sitekey: TS_SITEKEY,
        appearance: "interaction-only",
      });
    };
    var ts = document.createElement("script");
    ts.src = "https://challenges.cloudflare.com/turnstile/v0/api.js?onload=__awTsReady";
    ts.async = true;
    ts.defer = true;
    document.head.appendChild(ts);
  }
  function tsToken() {
    if (!TS_SITEKEY || !window.turnstile || tsWidgetId === null) return "";
    return window.turnstile.getResponse(tsWidgetId) || "";
  }
  function tsReset() {
    if (TS_SITEKEY && window.turnstile && tsWidgetId !== null) window.turnstile.reset(tsWidgetId);
  }

  function setStatus(html) {
    out.textContent = "";
    if (html) out.appendChild(html);
  }
  function statusLine(text) {
    return el("div", "aw-status", text);
  }
  function fallback(text, content) {
    var box = el("div", "aw-status");
    box.appendChild(document.createTextNode(text + " "));
    var a = document.createElement("a");
    a.href = BOOK_URL + encodeURIComponent(content);
    a.textContent = "Book the free 15-minute call instead →";
    a.addEventListener("click", function () {
      track("audit_booking", { cta_location: "widget-" + content });
    });
    box.appendChild(a);
    return box;
  }

  function call(payload) {
    payload.internal = INTERNAL;
    return fetch(ENDPOINT, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    }).then(function (r) { return r.json(); });
  }

  // --- flows -------------------------------------------------------------
  form.addEventListener("submit", function (e) {
    e.preventDefault();
    var q = input.value.trim();
    if (q.length < 3) {
      setStatus(statusLine("Type your business name — three characters or more."));
      return;
    }
    btn.disabled = true;
    setStatus(statusLine("Checking Google for your profile…"));
    track("audit_search", { query_length: q.length });
    call({ action: "search", query: q })
      .then(function (res) {
        if (!res.ok) {
          btn.disabled = false;
          return setStatus(failureFor(res.reason, "search-fallback"));
        }
        if (!res.candidates.length) {
          btn.disabled = false;
          return setStatus(fallback("No Google Business Profile found for that name — which is itself a finding.", "no-profile"));
        }
        // stay disabled through a single-candidate auto-audit so a second
        // submit can't race the in-flight audit
        if (res.candidates.length === 1) return runAudit(res.candidates[0].placeId);
        btn.disabled = false;
        renderPicker(res.candidates);
      })
      .catch(function () {
        btn.disabled = false;
        setStatus(fallback("The lookup didn't respond.", "search-error"));
      });
  });

  function failureFor(reason, content) {
    if (reason === "capped") {
      return fallback("Today's instant checks are spoken for — we pull profiles live on the call instead.", content);
    }
    if (reason === "rate_limited") {
      return fallback("That's the daily limit for instant checks from this connection.", content);
    }
    return fallback("The lookup didn't respond.", content);
  }

  function renderPicker(candidates) {
    var box = el("div", "aw-results");
    box.appendChild(el("div", "aw-results-head", "Which one is you? · results from Google"));
    candidates.forEach(function (c) {
      var b = el("button", "aw-pick", c.name);
      b.type = "button";
      b.appendChild(el("small", null, c.address));
      b.addEventListener("click", function () { runAudit(c.placeId); });
      box.appendChild(b);
    });
    setStatus(box);
  }

  function runAudit(placeId) {
    setStatus(statusLine("Pulling the profile and running it against the city benchmarks…"));
    call({ action: "audit", placeId: placeId, turnstileToken: tsToken() })
      .then(function (res) {
        btn.disabled = false;
        tsReset();
        if (res.reason === "turnstile") {
          return setStatus(statusLine("Quick verification needed — give it a second, then pick your business again."));
        }
        if (!res.ok) return setStatus(failureFor(res.reason, "audit-fallback"));
        if (res.unsupported === "out_of_area") {
          track("audit_result", { found: false, reason: "out_of_area" });
          return setStatus(fallback("Our benchmarks cover Metro Vancouver trades — that profile sits outside the area.", "out-of-area"));
        }
        if (res.unsupported === "not_trade") {
          track("audit_result", { found: false, reason: "not_trade" });
          return setStatus(fallback("Our benchmarks cover trades businesses — HVAC first. That profile looks like a different line of work.", "not-trade"));
        }
        track("audit_result", { found: true, cached: res.cached === true, city: res.card.city || "unknown" });
        renderCard(res.card);
      })
      .catch(function () {
        btn.disabled = false;
        setStatus(fallback("The audit didn't respond.", "audit-error"));
      });
  }

  function cell(heading, value) {
    var d = document.createElement("div");
    d.appendChild(el("strong", null, heading));
    d.appendChild(el("span", null, value));
    return d;
  }

  function renderCard(card) {
    var b = card.benchmark;
    var c = el("div", "specimen-card");
    c.appendChild(el("div", "specimen-head",
      "Your instant profile check · live from Google · " + (card.city || "Metro Vancouver")));

    var grid = el("div", "specimen-grid");
    grid.appendChild(cell("Company", card.name + (card.city ? " · " + card.city : "")));
    grid.appendChild(cell("Google reviews",
      card.reviewCount + (card.rating ? " · " + card.rating + "★" : "") +
      " · median " + b.medianReviews + " in " + b.city));
    grid.appendChild(cell("Profile photos",
      card.photoDisplay + (card.photoCount <= 3 ? " — reads as inactive" : "")));
    grid.appendChild(cell("Website", card.hasWebsite ? "linked on profile" : "none on profile"));
    grid.appendChild(cell("Hours", card.hasHours ? "listed" : "missing"));
    grid.appendChild(cell("Top competitor", Number(b.topReviews).toLocaleString("en-CA") + " reviews · " + b.city));
    c.appendChild(grid);

    var finding = el("div", "specimen-finding");
    finding.appendChild(el("strong", null, "Finding"));
    finding.appendChild(el("span", null, card.finding));
    c.appendChild(finding);

    var cta = el("div", "aw-card-cta");
    cta.appendChild(bookLink("Get the full audit — free 15-minute call", "scorecard"));
    c.appendChild(cta);

    c.appendChild(el("p", "specimen-note",
      "This covers what Google's API shows. Profile description, posts, Q&A and your live " +
      "map-pack position — the other half of the audit — we pull on the call."));
    c.appendChild(el("p", "specimen-note aw-attrib",
      "Benchmark: median of the " + b.label + " · " +
      "as of " + b.asOf + " · listing data powered by Google"));
    setStatus(c);
    c.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }
})();
