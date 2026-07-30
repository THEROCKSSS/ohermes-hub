// Points the hidden footer glyph at personal-docker-umbrella's own PIN
// page, on its own port, resolved against whatever host this page is
// currently being viewed from (localhost / Tailscale IP / the real domain)
// -- umbrella-gate's login/unlock routes are hardcoded absolute paths at
// its own root, so it needs its own port rather than a proxied sub-path.
(function () {
  "use strict";
  var link = document.getElementById("secret-entry");
  if (!link) return;
  var UMBRELLA_PORT = 8108;
  link.href = window.location.protocol + "//" + window.location.hostname + ":" + UMBRELLA_PORT + "/";
})();
