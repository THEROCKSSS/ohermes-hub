---
name: ohermes-hub-frontend-webpage-setup
description: "Build the static frontend for an ohermes-hub-style project index -- plain HTML/CSS/vanilla JS served by nginx, consuming a data-provider backend's /api/ endpoints. Local-only setup. Use after the backend-provider-setup skill, or when you already have a JSON API and just need a safe, dependency-free page to display it."
---

# ohermes-hub: frontend webpage setup

This builds the **webpage** — no framework, no build step, no npm install.
Plain HTML/CSS/JS served by nginx, which also reverse-proxies `/api/` to
your backend provider. This skill assumes the
`ohermes-hub-backend-provider-setup` skill (or an equivalent JSON API) is
already running on port 8000. Local-only — nothing here involves a real
domain, Tailscale, or DuckDNS.

## The core safety rule, before anything else

**Every piece of API-sourced content gets rendered with `textContent` /
`createElement`, never `innerHTML`.** A repo name, description, or commit
message is text you don't fully control (it's whatever's in that GitHub
repo) — if you ever render it with `innerHTML`, a repo description
containing `<img src=x onerror=...>` becomes a working XSS payload the
moment someone views your page. This is not a theoretical concern; it's the
single most important thing this skill teaches. If you only take one
practice from this, take this one.

```js
// Wrong -- untrusted content parsed as HTML
card.innerHTML = "<h3>" + project.name + "</h3>";

// Right -- untrusted content only ever treated as text
const h3 = document.createElement("h3");
h3.textContent = project.name;
card.appendChild(h3);
```

Same logic applies to a README preview: render it as plain preformatted
text (`white-space: pre-wrap` in CSS), never run it through a markdown-to-
HTML converter unless that converter is a vetted library with real
sanitization — a hand-rolled one is very easy to get wrong.

## Structure

```
frontend/
  Dockerfile
  nginx.conf
  public/
    index.html
    css/style.css
    js/app.js
    partials/nav.html
    partials/footer.html
    js/partials.js
```

Keep the Dockerfile and nginx.conf **outside** the directory you copy into
nginx's web root (`public/`), so they never accidentally get served as
static files:

```dockerfile
FROM nginx:alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY public/ /usr/share/nginx/html/
```

## Talking to the backend

`nginx.conf` reverse-proxies API calls to the backend container over the
Docker network (works out of the box if both are in the same
`docker-compose.yml` — no extra networking needed):

```nginx
server {
    listen 80;
    root /usr/share/nginx/html;
    index index.html;

    location /api/ {
        proxy_pass http://hub-api:8000;
        proxy_set_header Host $http_host;
    }

    location / {
        try_files $uri $uri/ =404;
    }
}
```

`hub-api` here is the backend's *service name* in `docker-compose.yml`, not
`localhost` — Docker Compose gives every service a resolvable hostname on
the shared network automatically.

## Fetching and rendering data (the actual pattern)

```js
fetch("/api/projects")
  .then(r => r.json())
  .then(data => {
    const grid = document.getElementById("project-grid");
    grid.textContent = "";
    data.projects.forEach(p => {
      const card = document.createElement("div");
      card.className = "card";
      const h3 = document.createElement("h3");
      const a = document.createElement("a");
      a.textContent = p.name;        // textContent, not innerHTML
      a.href = p.github_url;
      h3.appendChild(a);
      card.appendChild(h3);
      const desc = document.createElement("p");
      desc.textContent = p.description;
      card.appendChild(desc);
      grid.appendChild(card);
    });
  })
  .catch(() => {
    // Always handle the failure case -- show a real "couldn't load" message,
    // never leave a silently broken/blank page.
  });
```

## A shared nav without duplicating it on every page

Once you have more than a couple of pages, don't paste the same `<nav>`
block into every HTML file — one small change (a new page, a renamed link)
then means editing N files and inevitably missing one. Instead:

`partials/nav.html` and `partials/footer.html` hold the real markup. Every
page has empty placeholder slots:

```html
<div id="nav-slot"></div>
<!-- page content -->
<div id="footer-slot"></div>
<script src="js/partials.js"></script>
```

`js/partials.js`:
```js
(function () {
  function inject(selector, url) {
    const slot = document.querySelector(selector);
    if (!slot) return Promise.resolve();
    return fetch(url).then(r => r.text()).then(html => { slot.outerHTML = html; })
      .catch(() => {}); // fail silently -- page content still works without chrome
  }
  Promise.all([
    inject("#nav-slot", "/partials/nav.html"),
    inject("#footer-slot", "/partials/footer.html"),
  ]);
})();
```

Now every page shares one nav/footer source of truth — add a page, add one
link in `partials/nav.html`, done.

## Testing it locally

```bash
docker compose up -d --build
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8500/
```

Open `http://localhost:8500/` in a real browser too — a 200 status code
doesn't prove the JavaScript actually ran without errors; check the
console.

## Security checklist before calling it done

- [ ] `grep -rn "innerHTML" public/` returns nothing (or only intentional,
      reviewed uses on fully-trusted static strings you wrote yourself)
- [ ] Security headers set at the nginx level too, not just the backend:
      `add_header X-Frame-Options "DENY" always;` etc.
- [ ] Any user-facing search/filter is client-side only — no user input
      ever gets sent to the backend and reflected back unsanitized
- [ ] A custom `404.html` exists and nginx's `error_page 404 /404.html`
      points at it, so broken links don't leak nginx's default error page
