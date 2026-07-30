// Loads the shared nav/footer into every page from one source of truth,
// instead of duplicating the (now fairly large) nav across ~19 pages.
// No framework, no build step -- just fetch + outerHTML swap.
(function () {
  "use strict";

  function inject(selector, url) {
    var slot = document.querySelector(selector);
    if (!slot) return Promise.resolve();
    return fetch(url)
      .then(function (r) {
        if (!r.ok) throw new Error("partial fetch failed");
        return r.text();
      })
      .then(function (html) {
        slot.outerHTML = html;
      })
      .catch(function () {
        // Fail silently -- the page's actual content still works without
        // nav/footer chrome; better than a broken page over a missing partial.
      });
  }

  window.ohermesPartialsReady = Promise.all([
    inject("#nav-slot", "/partials/nav.html"),
    inject("#footer-slot", "/partials/footer.html"),
  ]).then(function () {
    // secret-entry.js needs the real footer link in the DOM, which only
    // exists after the footer partial above has been injected.
    var script = document.createElement("script");
    script.src = "/js/secret-entry.js";
    document.body.appendChild(script);
  });
})();
