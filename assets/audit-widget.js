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

  function num(n) { return (Number(n) || 0).toLocaleString("en-CA"); }

  // Reviews gap bar — HVAC/trades only, where a city benchmark exists. Bar is
  // scaled to the leader (the max).
  function reviewBar(you, median, top) {
    you = Number(you) || 0;
    median = Number(median) || 0;
    top = Number(top) || 0;
    var max = Math.max(you, median, top, 1);
    var box = el("div", "aw-bar-box");
    var track = el("div", "aw-bar");
    var fill = el("div", "aw-bar-fill" + (median > 0 && you < median ? " aw-bar-low" : ""));
    fill.style.width = Math.max(3, Math.round((you / max) * 100)) + "%";
    track.appendChild(fill);
    if (median > 0) {
      var mark = el("div", "aw-bar-mark");
      mark.style.left = Math.min(98, Math.round((median / max) * 100)) + "%";
      mark.setAttribute("title", "City median: " + num(median));
      track.appendChild(mark);
    }
    box.appendChild(track);
    var legend = el("div", "aw-bar-legend");
    legend.appendChild(el("span", "aw-bar-you", "You " + num(you)));
    legend.appendChild(el("span", null, "Median " + num(median)));
    legend.appendChild(el("span", null, "Leader " + num(top)));
    box.appendChild(legend);
    return box;
  }

  // Optional, post-scorecard. Captures an email onto the lead the audit already
  // logged (action: lead_email). The widget never sends mail — copy must not
  // promise one; the address is a warm-lead signal for the call.
  function emailCapture(placeId) {
    var box = el("div", "aw-email");
    box.appendChild(el("p", "aw-email-copy",
      "Your live Map Pack rank — the number that moves the phone — we reveal on the call. " +
      "Leave your email and we'll connect this profile to your booking."));
    var f = el("form", "aw-email-form");
    var i = el("input", "aw-email-input");
    i.type = "email";
    i.name = "email";
    i.autocomplete = "email";
    i.maxLength = 254;
    i.placeholder = "you@yourcompany.com";
    i.setAttribute("aria-label", "Email to prep your full audit");
    var bb = el("button", "aw-email-btn", "Prep my breakdown");
    bb.type = "submit";
    f.appendChild(i);
    f.appendChild(bb);
    box.appendChild(f);
    box.appendChild(el("p", "aw-email-note",
      "No automated email is sent. This only saves the profile signal."));
    f.addEventListener("submit", function (e) {
      e.preventDefault();
      var email = (i.value || "").trim();
      if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) { i.focus(); return; }
      bb.disabled = true;
      bb.textContent = "Saving…";
      call({ action: "lead_email", placeId: placeId, email: email })
        .then(function (r) {
          track("audit_email_captured", { ok: !!(r && r.ok) });
          box.textContent = "";
          box.appendChild(el("p", "aw-email-done",
            "Got it — your full breakdown will be ready at your audit. Grab a time:"));
          box.appendChild(bookLink("Book your free 15-minute audit", "email-capture"));
        })
        .catch(function () {
          bb.disabled = false;
          bb.textContent = "Prep my breakdown";
          i.value = "";
          i.placeholder = "Didn't save — try again";
        });
    });
    return box;
  }

  function renderCard(card) {
    var b = card.benchmark || null;
    var profileOnly = !b || card.vertical === "other_local";
    var c = el("div", "specimen-card");
    c.appendChild(el("div", "specimen-head",
      "Your instant profile check · live from Google · " + (card.city || "Metro Vancouver")));

    // Gaps headline — count the cheap-to-name problems; the expensive one (live
    // map-pack rank) stays gated to the call.
    var gaps = [];
    if (!profileOnly && b.medianReviews != null && card.reviewCount < b.medianReviews) gaps.push("reviews under the city median");
    if (!card.hasWebsite) gaps.push("no website linked");
    if (card.photoCount <= 3) gaps.push("too few photos");
    if (!card.hasHours) gaps.push("no hours listed");
    var head = el("div", "aw-gaps " + (gaps.length ? "aw-gaps-warn" : "aw-gaps-ok"));
    if (profileOnly) {
      head.appendChild(el("span", null,
        "Collected for manual review. No local benchmark is applied to this business; this card only records the Google profile fields."));
    } else if (gaps.length) {
      head.appendChild(el("strong", "aw-gaps-n", String(gaps.length)));
      head.appendChild(el("span", null,
        (gaps.length === 1 ? " gap is" : " gaps are") +
        " holding your Map Pack visibility back — " + gaps.join(" · ") + "."));
    } else {
      head.appendChild(el("span", null,
        "Fundamentals hold up. Your edge now is in what Google hides — description, posts, Q&A and your live map-pack rank."));
    }
    c.appendChild(head);

    if (!profileOnly) c.appendChild(reviewBar(card.reviewCount, b.medianReviews, b.topReviews));

    var grid = el("div", "specimen-grid");
    grid.appendChild(cell("Company", card.name + (card.city ? " · " + card.city : "")));
    if (profileOnly) {
      grid.appendChild(cell("Google reviews",
        card.reviewCount + (card.rating ? " · " + card.rating + "★" : "") +
        " · no industry benchmark applied"));
    } else {
      grid.appendChild(cell("Google reviews",
        card.reviewCount + (card.rating ? " · " + card.rating + "★" : "") +
        " · median " + b.medianReviews + " in " + b.city));
    }
    grid.appendChild(cell("Profile photos",
      card.photoDisplay + (card.photoCount <= 3 ? " — reads as inactive" : "")));
    grid.appendChild(cell("Website", card.hasWebsite ? "linked on profile" : "none on profile"));
    grid.appendChild(cell("Hours", card.hasHours ? "listed" : "missing"));
    if (!profileOnly) grid.appendChild(cell("Top competitor", num(b.topReviews) + " reviews · " + b.city));
    if (profileOnly) grid.appendChild(cell("Capture mode", "profile-only lead · no automated email or outreach"));
    c.appendChild(grid);

    var finding = el("div", "specimen-finding");
    finding.appendChild(el("strong", null, "Finding"));
    finding.appendChild(el("span", null, card.finding));
    c.appendChild(finding);

    var cta = el("div", "aw-card-cta");
    cta.appendChild(bookLink("Get the full audit — free 15-minute call", "scorecard"));
    c.appendChild(cta);

    c.appendChild(emailCapture(card.placeId));

    if (profileOnly) {
      c.appendChild(el("p", "specimen-note",
        "This covers what Google's API shows. We collected the profile fields only; no email or automated outreach is sent."));
      c.appendChild(el("p", "specimen-note aw-attrib",
        "No local benchmark applied · listing data powered by Google"));
    } else {
      c.appendChild(el("p", "specimen-note",
        "This covers what Google's API shows. Profile description, posts, Q&A and your live " +
        "map-pack position — the other half of the audit — we pull on the call."));
      c.appendChild(el("p", "specimen-note aw-attrib",
        "Benchmark: median of the " + b.label + " · " +
        "as of " + b.asOf + " · listing data powered by Google"));
    }
    setStatus(c);
    c.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }
})();
