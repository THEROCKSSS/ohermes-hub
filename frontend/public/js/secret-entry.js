// Points the hidden footer glyph at personal-docker-umbrella's own PIN page.
//
// umbrella-gate's /login, /unlock, /whoami and /console are hardcoded
// absolute paths at its root, so it can't be proxied under a sub-path --
// it needs its own origin. Two ways to give it one:
//
//   * On a real *.duckdns.org domain: a sibling host label
//     (umbrella.ohermes.duckdns.org) that Caddy routes to :8108 by Host.
//     DuckDNS resolves arbitrary labels under an owned domain to the same
//     A record, so no extra DNS registration is needed, and this keeps the
//     public entry on 443 -- no extra port to forward, real TLS.
//   * Anywhere else (localhost / Tailscale IP): the port directly, since
//     there's no cert or Host-routing in play there.
(function () {
  "use strict";
  var link = document.getElementById("secret-entry");
  if (!link) return;

  var UMBRELLA_PORT = 8108;
  var host = window.location.hostname;

  if (/\.duckdns\.org$/i.test(host)) {
    // ohermes.duckdns.org -> umbrella.ohermes.duckdns.org
    // (already-prefixed hosts are left alone rather than double-prefixed)
    var target = /^umbrella\./i.test(host) ? host : "umbrella." + host;
    link.href = "https://" + target + "/";
    return;
  }

  link.href = window.location.protocol + "//" + host + ":" + UMBRELLA_PORT + "/";
})();
