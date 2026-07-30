// ohermes-hub frontend — no framework, no build step.
// All rendering uses textContent/createElement, never innerHTML with
// API-sourced data, to keep this safe against a compromised or malicious
// repo description reaching the page unsanitized.

(function () {
  "use strict";

  var LANGUAGE_COLORS = {
    HTML: "#e34c26",
    Python: "#3572A5",
    TypeScript: "#3178c6",
    JavaScript: "#f1e05a",
    CSS: "#563d7c",
  };

  var allProjects = [];
  var activeTags = new Set();
  var searchTerm = "";
  var sortMode = "recent";
  var compactView = false;

  function el(tag, opts) {
    const node = document.createElement(tag);
    if (opts) {
      if (opts.className) node.className = opts.className;
      if (opts.text !== undefined) node.textContent = opts.text;
      if (opts.attrs) {
        for (const [k, v] of Object.entries(opts.attrs)) node.setAttribute(k, v);
      }
    }
    return node;
  }

  function timeAgo(iso) {
    if (!iso) return "";
    const then = new Date(iso).getTime();
    const diffMs = Date.now() - then;
    const days = Math.floor(diffMs / 86400000);
    if (days < 1) return "today";
    if (days === 1) return "1 day ago";
    if (days < 30) return `${days} days ago`;
    const months = Math.floor(days / 30);
    if (months < 12) return `${months} mo ago`;
    return `${Math.floor(months / 12)} yr ago`;
  }

  function renderNowBuilding() {
    const withDates = allProjects.filter((p) => p.pushed_at);
    const box = document.getElementById("now-building");
    if (!box) return;
    if (!withDates.length) {
      box.hidden = true;
      return;
    }
    const newest = withDates.reduce((a, b) => (a.pushed_at > b.pushed_at ? a : b));
    document.getElementById("now-building-name").textContent = newest.name;
    const tag = document.getElementById("now-building-tag");
    if (tag) {
      tag.textContent = newest.live ? "LIVE DATA" : "NON-LIVE DATA";
      tag.className = "data-tag " + (newest.live ? "live" : "static");
    }
    box.hidden = false;
  }

  function renderTagFilters() {
    const tagSet = new Set();
    allProjects.forEach((p) => (p.tags || []).forEach((t) => tagSet.add(t)));
    const container = document.getElementById("tag-filters");
    if (!container) return;
    container.textContent = "";
    Array.from(tagSet)
      .sort()
      .forEach((tag) => {
        const chip = el("button", { className: "tag-chip", text: tag });
        chip.type = "button";
        chip.setAttribute("aria-pressed", activeTags.has(tag) ? "true" : "false");
        chip.addEventListener("click", () => {
          if (activeTags.has(tag)) activeTags.delete(tag);
          else activeTags.add(tag);
          renderTagFilters();
          renderGrid();
        });
        container.appendChild(chip);
      });
  }

  function matchesFilters(p) {
    if (activeTags.size > 0) {
      const tags = p.tags || [];
      if (![...activeTags].every((t) => tags.includes(t))) return false;
    }
    if (searchTerm) {
      const hay = (p.name + " " + p.description).toLowerCase();
      if (!hay.includes(searchTerm.toLowerCase())) return false;
    }
    return true;
  }

  function sortProjects(list) {
    const copy = list.slice();
    if (sortMode === "stars") {
      copy.sort((a, b) => (b.stars || 0) - (a.stars || 0));
    } else if (sortMode === "alpha") {
      copy.sort((a, b) => a.name.localeCompare(b.name));
    } else {
      copy.sort((a, b) => (b.pushed_at || "").localeCompare(a.pushed_at || ""));
    }
    return copy;
  }

  function buildSparkline(weeks) {
    const wrap = el("div", { className: "sparkline" });
    if (!weeks || !weeks.length) return wrap;
    const max = Math.max(1, ...weeks);
    weeks.forEach((count) => {
      const bar = el("span");
      bar.style.height = Math.max(2, Math.round((count / max) * 18)) + "px";
      if (count === 0) bar.classList.add("zero");
      wrap.appendChild(bar);
    });
    return wrap;
  }

  function buildCard(p, allTags) {
    const card = el("div", { className: "card" });
    if (p.featured) card.classList.add("featured");

    const h3 = el("h3");
    const link = el("a", { text: p.name });
    link.href = "/project.html?repo=" + encodeURIComponent(p.repo);
    h3.appendChild(link);
    if (p.language && LANGUAGE_COLORS[p.language]) {
      const dot = el("span", { className: "lang-dot" });
      dot.style.background = LANGUAGE_COLORS[p.language];
      dot.title = p.language;
      h3.appendChild(dot);
    }
    card.appendChild(h3);

    card.appendChild(el("p", { text: p.description }));

    if (!compactView) {
      card.appendChild(buildSparkline(p.sparkline));
    }

    const badges = el("div", { className: "card-badges" });
    if (p.license) {
      const lbl = p.license === "NOASSERTION" ? "custom license" : p.license;
      badges.appendChild(el("span", { className: "data-tag", text: lbl }));
    }
    if (typeof p.open_issues === "number" && p.open_issues > 0) {
      badges.appendChild(el("span", { className: "data-tag", text: p.open_issues + " open issues" }));
    }
    if (badges.childNodes.length) card.appendChild(badges);

    const meta = el("div", { className: "card-meta" });
    const tagsWrap = el("div", { className: "card-tags" });
    (p.tags || []).forEach((t) => tagsWrap.appendChild(el("span", { text: t })));
    meta.appendChild(tagsWrap);

    const right = el("span");
    const bits = [];
    if (typeof p.stars === "number") bits.push(`★ ${p.stars}`);
    if (p.pushed_at) bits.push(timeAgo(p.pushed_at));
    right.textContent = bits.join(" · ");
    meta.appendChild(right);

    card.appendChild(meta);

    // "Similar projects" -- other cards sharing at least one tag.
    if (allTags && (p.tags || []).length) {
      const similar = allProjects.filter(
        (o) => o.repo !== p.repo && (o.tags || []).some((t) => (p.tags || []).includes(t))
      );
      if (similar.length) {
        const simWrap = el("div", { className: "similar" });
        simWrap.appendChild(el("span", { className: "similar-label", text: "Similar: " }));
        similar.slice(0, 3).forEach((s, i) => {
          if (i > 0) simWrap.appendChild(document.createTextNode(", "));
          const a = el("a", { text: s.name });
          a.href = "/project.html?repo=" + encodeURIComponent(s.repo);
          simWrap.appendChild(a);
        });
        card.appendChild(simWrap);
      }
    }

    return card;
  }

  function renderGrid() {
    const grid = document.getElementById("project-grid");
    if (!grid) return;
    const noResults = document.getElementById("no-results");
    grid.textContent = "";
    grid.classList.toggle("compact", compactView);
    let visible = allProjects.filter(matchesFilters);
    visible = sortProjects(visible);
    if (!visible.length) {
      if (noResults) noResults.hidden = false;
      return;
    }
    if (noResults) noResults.hidden = true;
    visible.forEach((p) => grid.appendChild(buildCard(p, true)));
  }

  function renderChangelog(entries) {
    const list = document.getElementById("changelog-list");
    if (!list) return;
    list.textContent = "";
    if (!entries.length) {
      list.appendChild(
        el("p", { className: "empty-state", text: "No recent activity available right now." })
      );
      return;
    }
    entries.forEach((e) => {
      const row = el("div", { className: "changelog-item" });

      const time = el("time", { text: timeAgo(e.date) });
      time.dateTime = e.date;
      row.appendChild(time);

      const middle = el("div");
      const repoSpan = el("span", { className: "repo-name", text: e.repo + " " });
      middle.appendChild(repoSpan);
      const msgLink = el("a", { className: "msg", text: e.message });
      msgLink.href = e.commit_url;
      msgLink.target = "_blank";
      msgLink.rel = "noopener noreferrer";
      middle.appendChild(msgLink);
      row.appendChild(middle);

      row.appendChild(el("span", { className: "sha", text: e.sha }));
      list.appendChild(row);
    });
  }

  async function loadProjects() {
    try {
      const res = await fetch("/api/projects");
      if (!res.ok) throw new Error("bad response");
      const data = await res.json();
      allProjects = data.projects || [];
      renderNowBuilding();
      renderTagFilters();
      renderGrid();
    } catch (err) {
      const grid = document.getElementById("project-grid");
      if (!grid) return;
      grid.textContent = "";
      grid.appendChild(
        el("p", {
          className: "empty-state",
          text: "Couldn't load the project list right now — try refreshing.",
        })
      );
    }
  }

  async function loadChangelog() {
    try {
      const res = await fetch("/api/changelog");
      if (!res.ok) throw new Error("bad response");
      const data = await res.json();
      renderChangelog(data.entries || []);
    } catch (err) {
      renderChangelog([]);
    }
  }

  const searchInput = document.getElementById("search");
  if (searchInput) {
    searchInput.addEventListener("input", (e) => {
      searchTerm = e.target.value;
      renderGrid();
    });
  }

  const sortSelect = document.getElementById("sort-select");
  if (sortSelect) {
    sortSelect.addEventListener("change", (e) => {
      sortMode = e.target.value;
      renderGrid();
    });
  }

  const viewToggle = document.getElementById("view-toggle");
  if (viewToggle) {
    viewToggle.addEventListener("click", () => {
      compactView = !compactView;
      viewToggle.setAttribute("aria-pressed", String(compactView));
      viewToggle.textContent = compactView ? "Card view" : "Compact view";
      renderGrid();
    });
  }

  const randomBtn = document.getElementById("random-project");
  if (randomBtn) {
    randomBtn.addEventListener("click", () => {
      const visible = allProjects.filter(matchesFilters);
      if (!visible.length) return;
      const pick = visible[Math.floor(Math.random() * visible.length)];
      window.location.href = "/project.html?repo=" + encodeURIComponent(pick.repo);
    });
  }

  loadProjects();
  loadChangelog();
})();
