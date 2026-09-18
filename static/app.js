/* HEP Graph front-end: no external runtime; all data is read from the local API. */
(() => {
  "use strict";
  const $ = (s, root = document) => root.querySelector(s);
  const $$ = (s, root = document) => [...root.querySelectorAll(s)];
  const state = {
    dataset: null,
    mode: "database",
    people: new Map(),
    source: null,
    target: null,
    lastPath: null,
    displayGraph: null,
    revision: 0,
    pathRequest: 0,
    deepJob: null,
    profileRequest: 0,
    lineage: null,
    lineageRequest: 0,
    graph: {
      nodes: new Map(),
      edges: [],
      scale: 1,
      tx: 0,
      ty: 0,
      drag: null,
      pan: null,
    },
    searches: { source: [], target: [] },
    timers: {},
    filterSignature: null,
    preparation: {
      timers: new Map(),
      inflight: new Map(),
      completed: new Set(),
    },
    restoring: false,
  };
  const allowedHosts = new Set([
    "inspirehep.net",
    "arxiv.org",
    "doi.org",
    "doi.org",
  ]);
  const choiceValue = (selectId, customId) =>
    $(selectId).value === "custom"
      ? $(customId).value.trim()
      : $(selectId).value;
  const filters = () => ({
    min_authors: choiceValue("#min-authors", "#min-authors-custom"),
    max_authors: choiceValue("#max-authors", "#max-authors-custom"),
    min_shared: choiceValue("#min-shared", "#min-shared-custom"),
    year_start: $("#year-start").value,
    year_end: $("#year-end").value,
    genealogy: $("#genealogy").checked ? "true" : "false",
  });
  const formatDate = (value) =>
    value
      ? new Date(value).toLocaleString(undefined, {
          dateStyle: "medium",
          timeStyle: "short",
        })
      : "not recorded";
  const personName = (p) => (p && (p.name || p.id)) || "Unknown researcher";
  const canonicalFilters = (f = filters()) => ({
    min_authors: String(f?.min_authors ?? 1),
    max_authors: f?.max_authors == null ? "all" : String(f.max_authors),
    min_shared: String(f?.min_shared ?? 1),
    year_start: String(f?.year_start ?? ""),
    year_end: String(f?.year_end ?? ""),
    genealogy: String(f?.genealogy ?? "false"),
  });
  const filterKey = () => JSON.stringify([state.mode, canonicalFilters()]);
  const queryKey = () =>
    JSON.stringify([state.mode, canonicalFilters(), state.source?.id, state.target?.id,
                    ...(state.stopKeys || []).map((key) => state[key]?.id || null)]);
  const updateDate = (value) => {
    const date = value ? new Date(value) : null;
    return date && !Number.isNaN(date.getTime())
      ? new Intl.DateTimeFormat("en-US", {
          timeZone: "America/Chicago", month: "2-digit", day: "2-digit", year: "numeric",
        }).format(date)
      : "09/16/2026";
  };
  const lastUpdatedText = () =>
    `Last updated ${updateDate(state.dataset?.source_cutoff || state.dataset?.created_at)}`;
  const canQuery = (person) =>
    Boolean(person && (person.queryable === true || person.indexed === true));
  const teamSizeDescription = (f) => {
    const min = Number(f?.min_authors ?? 1);
    const max = f?.max_authors == null || f.max_authors === "all"
      ? null
      : Number(f.max_authors);
    if (min === 1 && max === 10) return "small-team papers (up to 10 authors)";
    if (min === 11 && max == null) return "large-team papers (more than 10 authors)";
    if (min === 1 && max == null) return "all paper team sizes";
    if (max == null) return `papers with at least ${min} authors`;
    if (min === max) return `papers with exactly ${min} authors`;
    return `papers with ${min}–${max} authors`;
  };
  const filterDescription = (f) => {
    const active = { min_authors: 1, min_shared: 1, ...f };
    return `${teamSizeDescription(active)} · ${active.min_shared} shared work minimum · ${active.year_start || "all years"} to ${active.year_end || "all years"} · ${active.genealogy === false || active.genealogy === "false" ? "adviser records excluded" : "adviser records included"}`;
  };
  const remember = (person) => {
    if (person?.id) state.people.set(person.id, person);
    return person;
  };
  const byId = (id) =>
    state.graph.nodes.get(id)?.person ||
    state.people.get(id) || { id, name: id };
  const setStatus = (message, kind = "") => {
    const el = $("#global-status");
    el.className = `notice ${kind}`;
    el.textContent = message;
  };
  const clearStatus = () => ($("#global-status").className = "notice hidden");
  const safeHref = (href) => {
    try {
      const u = new URL(href);
      return u.protocol === "https:" && allowedHosts.has(u.hostname)
        ? u.href
        : null;
    } catch {
      return null;
    }
  };
  const link = (text, href) => {
    const a = document.createElement("a");
    a.textContent = text;
    const safe = safeHref(href);
    if (safe) {
      a.href = safe;
      a.target = "_blank";
      a.rel = "noopener noreferrer";
    } else {
      a.removeAttribute("href");
    }
    return a;
  };
  const api = async (path) => {
    const response = await fetch(path, {
      headers: { Accept: "application/json" },
    });
    let body;
    try {
      body = await response.json();
    } catch {
      body = { message: "The service returned an unreadable response." };
    }
    if (!response.ok) {
      const e = new Error(
        body.message || `Request failed (${response.status}).`,
      );
      e.body = body;
      e.status = response.status;
      throw e;
    }
    return body;
  };
  const urlWithFilters = (pathname, extras = {}) => {
    const u = new URL(pathname, location.origin);
    const f = filters();
    Object.entries({ ...f, ...extras, mode: "database" }).forEach(([k, v]) => {
      if (v !== "" && v != null) u.searchParams.set(k, v);
    });
    return u.pathname + "?" + u.searchParams.toString();
  };
  const setLoading = (button, loading, label) => {
    button.dataset.label ??= button.textContent;
    button.disabled = loading;
    if (loading) {
      button.textContent = label || "Loading…";
    } else button.textContent = button.dataset.label || button.textContent;
  };

  function validateFilters() {
    const f = filters();
    const numeric = [
      ["Minimum authors", f.min_authors, 1, 100000],
      ["Maximum authors", f.max_authors, 1, 100000],
      ["Minimum shared works", f.min_shared, 1, 1000],
    ];
    for (const [label, value, min, max] of numeric) {
      if (value === "all" && label === "Maximum authors") continue;
      if (
        !/^[1-9][0-9]*$/.test(value) ||
        Number(value) < min ||
        Number(value) > max
      ) {
        setStatus(
          `${label} must be a whole number from ${min} to ${max}.`,
          "error",
        );
        return false;
      }
    }
    if (f.max_authors !== "all" && Number(f.min_authors) > Number(f.max_authors)) {
      setStatus("Minimum authors cannot exceed maximum authors.", "error");
      return false;
    }
    return true;
  }

  function clearPreparation() {
    state.preparation.timers.forEach((timer) => clearTimeout(timer));
    state.preparation.timers.clear();
    state.preparation.inflight.forEach((entry) => entry.controller.abort());
    state.preparation.inflight.clear();
  }

  function preparationUrl(person, activeFilters) {
    const u = new URL("/api/prepare", location.origin);
    const params = {
      mode: "live",
      person: String(person.id),
      ...canonicalFilters(activeFilters),
    };
    Object.entries(params).forEach(([key, value]) => u.searchParams.set(key, value));
    return u.pathname + "?" + u.searchParams.toString();
  }

  async function preparePerson(person, signature, activeFilters) {
    if (state.mode !== "live" || !canQuery(person) || signature !== filterKey()) return;
    if (![state.source?.id, state.target?.id].some((id) => String(id) === String(person.id))) return;
    const key = JSON.stringify([String(person.id), canonicalFilters(activeFilters)]);
    if (state.preparation.completed.has(key) || state.preparation.inflight.has(key)) return;
    const controller = new AbortController();
    state.preparation.inflight.set(key, { controller });
    try {
      const response = await fetch(preparationUrl(person, activeFilters), {
        method: "POST",
        headers: { Accept: "application/json" },
        signal: controller.signal,
      });
      try { await response.json(); } catch { /* Preparation is an optional warm-up. */ }
      if (response.ok) state.preparation.completed.add(key);
    } catch (error) {
      if (error.name !== "AbortError") {
        /* A failed warm-up must not block identity selection or path search. */
      }
    } finally {
      state.preparation.inflight.delete(key);
    }
  }

  function schedulePreparation(people, delay = 0, timerKey = "selection") {
    if (state.mode !== "live") return;
    const old = state.preparation.timers.get(timerKey);
    if (old) clearTimeout(old);
    const signature = filterKey();
    const activeFilters = canonicalFilters();
    const unique = [...new Map(
      people.filter(Boolean).map((person) => [String(person.id), person]),
    ).values()];
    const timer = setTimeout(() => {
      state.preparation.timers.delete(timerKey);
      unique.forEach((person) => preparePerson(person, signature, activeFilters));
    }, delay);
    state.preparation.timers.set(timerKey, timer);
  }

  function invalidateResults() {
    const hadDeepJob = Boolean(state.deepJob);
    cancelDeepJob();
    state.revision++;
    $("#person-panel").classList.add("hidden");
    $("#person-content").replaceChildren();
    $("#edge-inspector").classList.add("hidden");
    $("#edge-inspector").replaceChildren();
    setLoading($("#find-connection"), false);
    if (state.lastPath || state.displayGraph) {
      $("#path-meta").textContent =
        "Inputs changed. Run the connection query again; the previous result is no longer in scope.";
      $("#path-message").className = "notice warning";
      $("#path-message").textContent =
        "Previous path cleared because the selected inputs changed.";
      $("#path-cards").replaceChildren();
      hideRouteOffer();
      state.lastPath = null;
      state.displayGraph = null;
      state.graph.nodes.clear();
      state.graph.edges = [];
      renderGraph();
    }
    if (hadDeepJob) {
      $("#connection-empty").classList.remove("hidden");
      $("#connection-results").classList.add("hidden");
    }
  }
  function updateCustomVisibility() {
    ["min-authors", "max-authors", "min-shared"].forEach((base) => {
      const custom = $(`#${base}-custom`);
      custom.classList.toggle("hidden", $(`#${base}`).value !== "custom");
    });
  }
  function applyTeamSizePreset(value) {
    const presets = {
      small: ["1", "10"],
      large: ["11", "all"],
      all: ["1", "all"],
    };
    const preset = presets[value];
    if (!preset) return;
    $("#min-authors").value = preset[0];
    $("#max-authors").value = preset[1];
  }
  function syncTeamSizeFromBounds() {
    const f = filters();
    const min = String(f.min_authors);
    const max = String(f.max_authors);
    $("#paper-team-size").value =
      min === "1" && max === "10" ? "small" :
        min === "11" && max === "all" ? "large" :
          min === "1" && max === "all" ? "all" : "custom";
  }
  function updateFilterSummary({ invalidate = true } = {}) {
    updateCustomVisibility();
    const f = filters();
    const customInvalid =
      ($("#min-authors").value === "custom" &&
        (!/^[1-9][0-9]*$/.test(f.min_authors) ||
          Number(f.min_authors) > 100000)) ||
      ($("#max-authors").value === "custom" &&
        (!/^[1-9][0-9]*$/.test(f.max_authors) ||
          Number(f.max_authors) > 100000)) ||
      ($("#min-shared").value === "custom" &&
        (!/^[1-9][0-9]*$/.test(f.min_shared) || Number(f.min_shared) > 1000));
    const nextSignature = JSON.stringify(canonicalFilters(f));
    const changed = state.filterSignature !== null && nextSignature !== state.filterSignature;
    state.filterSignature = nextSignature;
    $("#filter-summary").textContent =
      `${teamSizeDescription(f)} · ${f.min_shared} shared work${f.min_shared === "1" ? "" : "s"} · ${f.genealogy === "true" ? "adviser records included" : "adviser records excluded"}`;
    if (invalidate && changed) {
      invalidateResults();
      clearPreparation();
      schedulePreparation([state.source, state.target], 400, "filters");
    }
    if (customInvalid)
      setStatus(
        "Enter a positive whole number in the visible custom filter field before running a calculation.",
        "error",
      );
    if (!state.restoring) syncUrl();
  }
  function syncUrl() {
    const u = new URL(location.href),
      f = filters();
    Object.entries(f).forEach(([k, v]) =>
      v === "" ? u.searchParams.delete(k) : u.searchParams.set(k, v),
    );
    u.searchParams.set("mode", "database");
    u.searchParams.delete("version");
    if (state.source) u.searchParams.set("source", state.source.id);
    else u.searchParams.delete("source");
    if (state.target) u.searchParams.set("target", state.target.id);
    else u.searchParams.delete("target");
    const via = (state.stopKeys || []).map((key) => state[key]?.id).filter(Boolean);
    u.searchParams.delete("then");
    if (via.length) u.searchParams.set("with", via.join(","));
    else u.searchParams.delete("with");
    history.replaceState(null, "", u);
  }
  function setFilterFromUrl(base, value) {
    const select = $(`#${base.replace("_", "-")}`),
      custom = $(`#${base.replace("_", "-")}-custom`);
    if (!value) return;
    if ([...select.options].some((o) => o.value === value))
      select.value = value;
    else {
      select.value = "custom";
      custom.value = value;
    }
  }
  function restoreUrl() {
    state.restoring = true;
    const u = new URL(location.href);
    setFilterFromUrl("min_authors", u.searchParams.get("min_authors") || "1");
    setFilterFromUrl("max_authors", u.searchParams.get("max_authors"));
    setFilterFromUrl("min_shared", u.searchParams.get("min_shared"));
    for (const key of ["year_start", "year_end"])
      if (u.searchParams.has(key))
        $(`#${key.replace("_", "-")}`).value = u.searchParams.get(key);
    if (u.searchParams.has("genealogy"))
      $("#genealogy").checked = u.searchParams.get("genealogy") === "true";
    state.restore = {
      source: u.searchParams.get("source"),
      target: u.searchParams.get("target"),
      // "then" is the name the parameter had while groups were ordered routes.
      then: (u.searchParams.get("with") || u.searchParams.get("then") || "").split(",").map((id) => id.trim())
        .filter((id) => /^\d{1,12}$/.test(id)),
    };
    state.mode = "database";
    syncTeamSizeFromBounds();
    updateFilterSummary({ invalidate: false });
    state.restoring = false;
  }
  function coverageText(coverage) {
    if (!coverage) return "Coverage metadata is unavailable.";
    return `Last updated ${updateDate(state.dataset?.source_cutoff || state.dataset?.created_at)}. ${coverage.complete ? "Coverage verified for this release." : "Coverage is partial or bounded."}`;
  }

  function showTab(id) {
    document.body.dataset.tab = id;
    $$(".tab").forEach((x) => {
      const active = x.dataset.tab === id;
      x.classList.toggle("is-active", active);
      x.setAttribute("aria-selected", active ? "true" : "false");
    });
    $$(".view").forEach((x) => x.classList.toggle("is-active", x.id === id));
    // The forest map is fetched the first time it is actually looked at.
    if (id === "lineage-map") ensureLineageMap();
    const active = $(`.tab[data-tab="${id}"]`);
    if (active) active.scrollIntoView({ block: "nearest", inline: "nearest" });
    updateNavFade();
  }

  /* On a phone the tab strip can overflow; fade whichever edge has more tabs
     beyond it, so the strip reads as something that scrolls. */
  function updateNavFade() {
    const nav = $(".site-header nav");
    if (!nav) return;
    const more = nav.scrollWidth - nav.clientWidth;
    nav.classList.toggle("can-scroll-left", more > 2 && nav.scrollLeft > 2);
    nav.classList.toggle("can-scroll-right", more > 2 && nav.scrollLeft < more - 2);
  }

  function setupPageChrome() {
    document.body.dataset.tab =
      $(".tab.is-active")?.dataset.tab || "connections";
    const nav = $(".site-header nav");
    if (nav) {
      nav.addEventListener("scroll", updateNavFade, { passive: true });
      window.addEventListener("resize", updateNavFade);
      updateNavFade();
    }
    const show = $("#show-disclaimer");
    if (show)
      show.addEventListener("click", () => {
        $("#project-disclaimer").classList.add("is-open");
        $("#project-disclaimer-short").classList.add("is-hidden");
        show.setAttribute("aria-expanded", "true");
        $("#project-disclaimer").scrollIntoView({ behavior: "smooth", block: "start" });
      });
  }

  function renderPicker(which) {
    const p = state[which],
      holder = $(`#${which}-selected`);
    holder.replaceChildren();
    holder.hidden = !p;
    if (!p) return;
    remember(p);
    // The name stays in the field, where the reader typed it; the line below
    // carries the identifier and availability instead of repeating the name.
    $(`#${which}-query`).value = personName(p);
    const sub = document.createElement("span");
    sub.textContent = `INSPIRE ${p.id}`;
    holder.append(sub);
    const badge = document.createElement("span");
    badge.className = `status ${p.indexed === false ? "unindexed" : "indexed"}`;
    badge.textContent = p.indexed === false ? "not in this release" : "available";
    holder.append(badge);
  }
  function clearPicker(which) {
    if (which === "lineage") {
      clearLineage();
      return;
    }
    invalidateResults();
    state[which] = null;
    $(`#${which}-query`).value = "";
    $(`#${which}-results`).replaceChildren();
    $(`#${which}-results`).classList.remove("inline-search-notice");
    renderPicker(which);
    syncUrl();
  }
  function choosePerson(which, result) {
    const chosen = result.person || result;
    if (which === "lineage") {
      // The lineage root is independent of the connection query, so picking
      // one must not disturb a path result already on screen.
      setLineageRoot({ ...chosen, indexed: result.indexed ?? chosen.indexed });
      return;
    }
    invalidateResults();
    const p = result.person || result;
    state[which] = remember({
      ...p,
      indexed: result.indexed ?? p.indexed,
      queryable: result.queryable ?? p.queryable ?? false,
      indexed_publications:
        result.indexed_publications ?? p.indexed_publications,
    });
    $(`#${which}-results`).replaceChildren();
    $(`#${which}-results`).classList.remove("inline-search-notice");
    $(`#${which}-query`).setAttribute("aria-expanded", "false");
    renderPicker(which);
    syncUrl();
    schedulePreparation([state[which]], 0, which);
  }
  function searchResultText(result) {
    const p = result.person || result;
    const parts = [];
    parts.push(`INSPIRE ${p.id}`);
    if (p.affiliations?.length) parts.push(p.affiliations.join("; "));
    if (p.orcid) parts.push(`ORCID ${p.orcid}`);
    if (result.indexed === false) parts.push("not in this release");
    else if (result.indexed_publications != null)
      parts.push(
        `${result.indexed_publications} indexed publication${result.indexed_publications === 1 ? "" : "s"}`,
      );
    if (result.representative_work?.title)
      parts.push(result.representative_work.title);
    return parts.join(" · ");
  }
  function renderSearches(which, data) {
    const menu = $(`#${which}-results`);
    menu.replaceChildren();
    menu.classList.remove("inline-search-notice");
    state.searchResults = state.searchResults || {};
    state.searchResults[which] = data.results || [];
    if (data.status === "not_found") {
      const x = document.createElement("div");
      x.className = "search-result search-notice";
      x.textContent = data.message || "No matching researcher found.";
      menu.append(x);
      menu.classList.add("inline-search-notice");
      return;
    }
    if (data.status === "ambiguous") {
      const x = document.createElement("div");
      x.className = "search-result";
      x.textContent = data.message || "Several matches found — choose one.";
      menu.append(x);
    }
    if (data.status === "upstream_unavailable") {
      const x = document.createElement("div");
      x.className = "search-result";
      x.textContent =
        data.message ||
        "Live lookup is unavailable. Local results are shown if available.";
      menu.append(x);
    }
    if (data.status === "search_incomplete") {
      const x = document.createElement("div");
      x.className = "search-result search-notice";
      x.textContent = data.message || "Live search returned a bounded partial result.";
      menu.append(x);
    }
    (data.results || []).forEach((r, i) => {
      const b = document.createElement("button");
      b.type = "button";
      b.className = "search-result";
      b.setAttribute("role", "option");
      b.dataset.index = i;
      const strong = document.createElement("strong");
      strong.textContent = personName(r.person || r);
      b.append(strong);
      const small = document.createElement("small");
      small.textContent = searchResultText(r);
      b.append(small);
      b.addEventListener("click", () => choosePerson(which, r));
      menu.append(b);
    });
    $(`#${which}-query`).setAttribute(
      "aria-expanded",
      (data.results || []).length ? "true" : "false",
    );
  }

  function setupSearch(which) {
    const input = $(`#${which}-query`);
    input.addEventListener("input", () => {
      invalidateResults();
      if (state[which]) {
        state[which] = null;
        renderPicker(which);
        syncUrl();
      }
      state.searches[which] = {
        query: input.value,
        token: (state.searches[which]?.token || 0) + 1,
      };
      clearTimeout(state.timers[which]);
      state.timers[which] = setTimeout(() => searchPeople(which), 220);
    });
    input.addEventListener("keydown", (e) => {
      const buttons = $$(
        '.search-result[role="option"]',
        $(`#${which}-results`),
      );
      if (e.key === "Escape") {
        $(`#${which}-results`).replaceChildren();
      }
      if (e.key === "ArrowDown" && buttons[0]) {
        e.preventDefault();
        buttons[0].focus();
      }
    });
  }

  function statusForPath(data) {
    if (data.client_message) return data.client_message;
    if (data.status === "ok") return null;
    if (data.mode === "database" && data.status === "settled") {
      if (data.route_status === "exact_route_proven") return null;
      if (data.paths?.length) return "This route is documented, but a shorter one has not been ruled out.";
      if (data.route_status === "no_path") return "No connection was found in this release under the selected filters.";
      return data.message || "The search ended without a proven connection. The absence of a route is not conclusive.";
    }
    const hasPath = Boolean(data.paths?.length);
    if (hasPath) {
      const withPath = {
        searching:
          "A verified route is shown. The exact search continues in the background; if a shorter route is found it is announced above the result and never swapped in by itself.",
        search_incomplete:
          "A verified path is shown, but the exact graph search is incomplete. A shorter path may still be found.",
        resource_limit:
          "A verified path is shown, but the graph search reached its current resource limit. Continue the search to look for a shorter route.",
        cancelled:
          "The graph search was stopped. The verified path shown is supported by retrieved evidence, but shortestness is not established.",
        upstream_unavailable:
          "Source details became unavailable after a route was found. The result remains scoped to this release, and the search is incomplete.",
      };
      if (data.status === "searching") return withPath.searching;
      if (withPath[data.status]) return data.message || withPath[data.status];
    }
    const messages = {
      not_indexed:
        "At least one selected researcher is not included in this release, so no connection claim can be calculated.",
      no_path:
        "No documented connection was found within the indexed data and selected filters.",
      not_found: "The selected researcher was not found by the active source.",
      search_incomplete:
        "The search ended before exploration was complete; any route shown is scoped to this release.",
      searching:
        "The search is still exploring source records; no complete connection claim is available yet.",
      cancelled:
        "The search was stopped. Any route shown is an incomplete result from this release.",
      upstream_unavailable:
        "The search service is temporarily unavailable. Try again shortly.",
      resource_limit:
        "This calculation reached a resource limit before a path could be established.",
    };
    return (
      data.message ||
      messages[data.status] ||
      "No result is available for this request."
    );
  }

  function deepJobCurrent(job) {
    return state.deepJob === job && !job.cancelled &&
      job.revision === state.revision && job.mode === state.mode &&
      job.key === queryKey();
  }

  function deepEndpoint(job, suffix = "") {
    return `/api/search-jobs/${encodeURIComponent(job.jobId)}${suffix}?mode=${encodeURIComponent(job.mode)}`;
  }

  function sendDeepCancel(job) {
    if (!job?.jobId || job.cancelSent) return;
    job.cancelSent = true;
    fetch(deepEndpoint(job, "/cancel"), {
      method: "POST",
      headers: { Accept: "application/json" },
    }).catch(() => {});
  }

  function cancelDeepJob() {
    const job = state.deepJob;
    if (!job) return;
    job.cancelled = true;
    if (job.timer) clearTimeout(job.timer);
    job.timer = null;
    sendDeepCancel(job);
    forgetDeepJob(job);
    state.deepJob = null;
    hideRouteOffer();
    $("#deep-progress")?.classList.add("hidden");
  }

  // Only a temporary job handle and query configuration are kept in this tab.
  // Author and paper records remain in the server's bounded memory workspace.
  function rememberDeepJob(job) {
    if (!job.jobId || job.cancelled) return;
    try {
      sessionStorage.setItem("hep-graph-active-search", JSON.stringify({
        jobId: job.jobId, source: job.source, target: job.target,
        filters: canonicalFilters(job.filters), savedAt: Date.now(),
      }));
    } catch { /* Storage-disabled browsers still support ordinary searches. */ }
  }

  function forgetDeepJob(job) {
    try {
      const raw = sessionStorage.getItem("hep-graph-active-search");
      if (raw && JSON.parse(raw).jobId === job.jobId)
        sessionStorage.removeItem("hep-graph-active-search");
    } catch { /* No stored handle needs to be cleared. */ }
  }

  function retainedDeepJob(job) {
    try {
      const raw = sessionStorage.getItem("hep-graph-active-search");
      if (!raw || raw.length > 2000) return null;
      const saved = JSON.parse(raw);
      if (!/^[a-f0-9]{32}$/.test(saved.jobId) ||
          String(saved.source) !== String(job.source) || String(saved.target) !== String(job.target) ||
          !Number.isFinite(saved.savedAt) || Date.now() - saved.savedAt > 3 * 60 * 60 * 1000 ||
          !Object.hasOwn(saved.filters || {}, "min_authors") ||
          JSON.stringify(canonicalFilters(saved.filters)) !== JSON.stringify(canonicalFilters(job.filters))) return null;
      return saved.jobId;
    } catch { return null; }
  }

  function deepProgressText(progress = {}) {
    const people = progress.people_explored ?? 0;
    const works = progress.works_retrieved ?? 0;
    const elapsed = progress.elapsed_seconds == null
      ? "elapsed time unavailable"
      : `${Math.max(0, Math.round(progress.elapsed_seconds))}s elapsed`;
    const stageLabels = {
      expand_target: "Checking researchers from the target side",
      expand_source: "Checking researchers from the source side",
      check_candidate: "Checking a candidate route",
      retrieve_works: "Retrieving documented works",
      retrieve_people: "Retrieving neighboring researchers",
      source_profile: "Confirming the starting researcher",
      target_profile: "Confirming the target researcher",
      direct_pair: "Checking direct evidence",
      cross_frontier: "Checking links between both sides",
      validate_identity: "Checking profile and paper author names",
      guide_verify: "Verifying a possible connection",
      guide_profile_missing: "Checking another possible connection",
      guide_pair_cap: "Continuing the broader search",
      continue_search: "Continuing automatically with the records already retrieved",
      prove_shortest: "Looking for a shorter route",
      rate_limit_wait: "Waiting for INSPIRE’s rate limit, then continuing automatically",
      retry_upstream: "Waiting briefly for INSPIRE, then retrying automatically",
      discover_coauthors: "Exploring INSPIRE’s coauthor summaries from both ends",
    };
    const stage = stageLabels[progress.stage] || progress.stage || "exploring source records";
    if (progress.expansions != null)
      return `${progress.expansions} search steps · ${stage}`;
    return `${people} people explored · ${works} works retrieved · ${elapsed} · ${stage}`;
  }

  function renderDeepProgress(data, job) {
    const box = $("#deep-progress");
    box.classList.remove("hidden");
    const terminal = data.status !== "searching";
    $("#deep-title").textContent = data.status === "searching"
      ? (job?.displayed ? "Looking for a shorter route…" : "Finding a connection…")
      : data.status === "cancelled"
        ? "Search stopped"
      : data.status === "resource_limit"
          ? "Search reached its current limit"
      : data.status === "search_incomplete"
            ? "Search is incomplete"
            : "Search finished";
    $("#deep-summary").textContent = data.progress
      ? deepProgressText(data.progress)
      : data.message || (terminal ? "The search has ended." : "The search is starting.");
    const stop = $("#deep-stop"), cont = $("#deep-continue");
    const retryableFailure = data.status === "upstream_unavailable" && job?.jobId;
    stop.classList.toggle("hidden", (terminal && !retryableFailure) || job?.cancelled || job?.continuing);
    const verified = Boolean(data.paths?.length || job?.displayed || job?.best);
    cont.textContent = verified ? "Continue exact search" : "Continue search";
    cont.classList.toggle("hidden", !(terminal && data.can_continue === true));
  }

  // The server reports the best route it can currently stand behind
  // (best_route); which route this tab shows (job.displayed) is decided here
  // and is never swapped under the reader. A shorter route is offered in
  // #route-update and shown only when the reader asks for it.
  function routeSnapshot(data) {
    if (!data.paths?.length) return null;
    const best = data.best_route || {
      route_id: data.paths[0].route_id || (data.paths[0].people || []).map((p) => p.id).join(">"),
      hops: data.paths[0].hops,
    };
    return {
      routeId: best.route_id, hops: best.hops, paths: data.paths,
      version: data.version, foundAt: best.found_at_seconds ?? null,
    };
  }

  function routeState(data, job) {
    const displayed = job?.displayed, best = data.best_route;
    if (displayed && best && best.hops < displayed.hops) return "BETTER_ROUTE_AVAILABLE";
    // A route shorter than the server's best (a job restarted on another
    // server that has not re-found it): the server's proof is about a
    // different length and says nothing about this route.
    // Likewise when the server currently has no route at all.
    if (displayed && (!best || best.hops > displayed.hops))
      return data.status === "searching" ? "VERIFIED_ROUTE_FOUND"
        : data.status === "cancelled" ? "VERIFIED_SEARCH_STOPPED" : "SEARCH_INCOMPLETE";
    switch (data.route_status) {
      case "searching_no_path": return "SEARCHING_NO_PATH";
      case "verified_route_found": return "VERIFIED_ROUTE_FOUND";
      case "exact_route_proven": return "EXACT_ROUTE_PROVEN";
      case "verified_search_stopped": return "VERIFIED_SEARCH_STOPPED";
      case "no_path": return "NO_PATH";
      case undefined: return undefined;
      default: return "SEARCH_INCOMPLETE";
    }
  }

  function displayedResult(data, job) {
    const displayed = job.displayed;
    if (!displayed) return { ...data, route_state: routeState(data, job) };
    const best = data.best_route;
    const isBest = Boolean(best && best.route_id === displayed.routeId);
    // A proof closes on a hop count: every verified route of that length is a
    // shortest one, whichever of them is on screen.
    const proven = data.global_shortest_proven === true && Boolean(best) && displayed.hops === best.hops;
    return {
      ...data, paths: displayed.paths, version: displayed.version || data.version,
      ...(job.note ? { client_message: job.note } : {}),
      global_shortest_proven: proven,
      exact_for_retrieved_graph: isBest ? data.exact_for_retrieved_graph : false,
      displayed_route_id: displayed.routeId, displayed_is_best: isBest,
      route_state: routeState(data, job),
    };
  }

  function renderDisplayed(data, job, cards) {
    const shown = displayedResult(data, job);
    if (cards || !job.rendered) renderPath(shown); else renderPathHeading(shown);
    job.rendered = true;
  }

  function showRouteOffer(job, kind) {
    const best = job.best, displayed = job.displayed;
    if (!best || !displayed) return;
    const plural = (n) => `${n} hop${n === 1 ? "" : "s"}`;
    $("#route-update-text").textContent = kind === "exact"
      ? `Exact shortest path found: ${plural(best.hops)}. The ${plural(displayed.hops)} route shown is verified but not the shortest.`
      : `Shorter route found: ${plural(displayed.hops)} → ${plural(best.hops)}. The route shown stays until you switch.`;
    $("#route-update-show").textContent = kind === "exact" ? "Show exact route" : "Show shorter route";
    $("#route-update").classList.remove("hidden");
    state.routeOffer = {
      apply() {
        job.displayed = job.best;
        job.note = null;
        hideRouteOffer();
        if (job.lastData) renderDisplayed(job.lastData, job, true);
      },
    };
  }

  function hideRouteOffer() {
    state.routeOffer = null;
    $("#route-update")?.classList.add("hidden");
  }

  function consumeDeepResponse(data, job) {
    if (!deepJobCurrent(job)) return;
    // Versions come from the server. An update older than one already applied
    // is ignored whole, whatever it says; only its polling obligation remains.
    if (Number.isInteger(data.sequence_number) && data.sequence_number < job.sequence) {
      if (data.status === "searching" && !job.cancelled) scheduleDeepPoll(job);
      return;
    }
    const applied = job.sequence;
    if (Number.isInteger(data.sequence_number)) job.sequence = data.sequence_number;
    job.lastData = data;
    job.progress = data.progress || job.progress;
    const best = routeSnapshot(data);
    const displayed = job.displayed;
    // Only a withdrawal the server reports for the route on screen, in a
    // version newer than the last one applied, may take that route down.
    const withdrawn = Boolean(displayed) && (data.events || []).some((e) =>
      e.type === "route_withdrawn" && e.previous_route_id === displayed.routeId &&
      (!Number.isInteger(e.sequence_number) || e.sequence_number > applied));
    job.best = best;
    let cards = false;
    if (best && !displayed) {
      job.displayed = best;
      job.note = null;
      cards = true;
      hideRouteOffer();
    } else if (withdrawn) {
      // The engine's identity guard retracted the route on screen. A route
      // that is no longer verified must not stay up as if it were.
      job.displayed = best;
      job.note = best
        ? `The route shown earlier was withdrawn after identity checks. The best verified route now has ${best.hops} hop${best.hops === 1 ? "" : "s"}.`
        : "The route shown earlier was withdrawn after identity checks. No verified route is currently known.";
      cards = true;
      hideRouteOffer();
    } else if (best && displayed && best.routeId !== displayed.routeId) {
      if (best.hops < displayed.hops) {
        showRouteOffer(job, data.global_shortest_proven === true ? "exact" : "shorter");
      } else {
        // An equal-length route is not an improvement, and a longer one is
        // not better: keep what is shown, and offer nothing.
        hideRouteOffer();
      }
    } else if (!best && displayed) {
      // The route that was on offer is gone; the one on screen stands.
      hideRouteOffer();
    } else if (best && displayed && best.paths.length !== displayed.paths.length) {
      // Same primary route, more (or fewer) equal-length alternatives.
      job.displayed = best;
      cards = true;
    }
    if (job.displayed || data.status !== "searching") renderDisplayed(data, job, cards);
    renderDeepProgress(data, job);
    if (data.status === "searching") {
      if (!job.cancelled) scheduleDeepPoll(job);
      return;
    }
    job.done = true;
    setLoading($("#find-connection"), false);
    if (data.can_continue !== true) {
      forgetDeepJob(job);
      state.deepJob = null;
      $("#deep-progress").classList.add("hidden");
    }
  }

  function scheduleDeepPoll(job) {
    if (!deepJobCurrent(job)) return;
    if (job.timer) clearTimeout(job.timer);
    // The search advances only inside a poll. A poll that took a while was
    // doing that work, so ask again at once rather than idling; a quick one
    // found the job busy or paused, so there is nothing to gain by hurrying.
    const delay = job.lastPollMs > 1000 ? 250 : 1500;
    job.timer = setTimeout(() => pollDeepJob(job), delay);
  }

  async function pollDeepJob(job) {
    job.timer = null;
    if (!deepJobCurrent(job)) return;
    const startedAt = performance.now();
    try {
      const data = await api(deepEndpoint(job));
      job.lastPollMs = performance.now() - startedAt;
      if (!deepJobCurrent(job)) return;
      job.pollFailures = 0;
      consumeDeepResponse(data, job);
    } catch (e) {
      if (!deepJobCurrent(job)) return;
      if (!e.status || e.status >= 500 || e.status === 429) {
        job.pollFailures = (job.pollFailures || 0) + 1;
        renderDeepProgress({ status: "searching", progress: {
          ...job.progress, stage: "Reconnecting to the running search…",
        } }, job);
        job.timer = setTimeout(() => pollDeepJob(job), Math.min(30000, 2000 * job.pollFailures));
        return;
      }
      if (e.status === 404 && !job.done && (job.restarts || 0) < 2) {
        // The job is unknown to the process that answered: the search state
        // lives in one server process, and a poll can reach a different one.
        // Start the same search again there rather than dead-ending. Progress
        // counters begin again with it, and the stage says so.
        job.restarts = (job.restarts || 0) + 1;
        forgetDeepJob(job);
        job.jobId = null;
        job.sequence = -1;
        renderDeepProgress({ status: "searching", progress: {
          ...job.progress, stage: "The search moved to another server; starting it again there…",
        } }, job);
        try {
          const data = await api(urlWithFilters("/api/path", { source: job.source, target: job.target }));
          if (!deepJobCurrent(job)) {
            // The user moved on while the restart was in flight; do not leave
            // the fresh server job running for nobody.
            if (data.job_id) { job.jobId = data.job_id; sendDeepCancel(job); }
            return;
          }
          if (data.job_id) job.jobId = data.job_id;
          rememberDeepJob(job);
          consumeDeepResponse(data, job);
        } catch (restartError) {
          if (!deepJobCurrent(job)) return;
          job.done = true;
          renderDeepProgress({ status: "upstream_unavailable", message: restartError.message, can_continue: true }, job);
          setLoading($("#find-connection"), false);
        }
        return;
      }
      job.done = true;
      renderDeepProgress({ status: "upstream_unavailable", message: e.message, can_continue: true }, job);
      setLoading($("#find-connection"), false);
    }
  }

  async function continueDeepSearch(job) {
    if (!deepJobCurrent(job) || !job.done || job.continuing) return;
    job.continuing = true;
    renderDeepProgress({ status: "searching", progress: job.progress, message: "Continuing the search." }, job);
    try {
      const response = await fetch(deepEndpoint(job, "/continue"), {
        method: "POST",
        headers: { Accept: "application/json" },
      });
      let data;
      try { data = await response.json(); } catch { data = { message: "The service returned an unreadable response." }; }
      if (!response.ok) {
        const error = new Error(data.message || `Request failed (${response.status}).`);
        error.body = data;
        error.status = response.status;
        throw error;
      }
      if (!deepJobCurrent(job)) return;
      job.continuing = false;
      job.done = false;
      consumeDeepResponse(data, job);
    } catch (e) {
      if (!deepJobCurrent(job)) return;
      job.continuing = false;
      job.done = true;
      renderDeepProgress({ status: "upstream_unavailable", message: e.message, can_continue: true }, job);
    }
  }

  function stopDeepSearch() {
    const job = state.deepJob;
    if (!job) return;
    job.cancelled = true;
    if (job.timer) clearTimeout(job.timer);
    job.timer = null;
    sendDeepCancel(job);
    forgetDeepJob(job);
    state.deepJob = null;
    const last = job.lastData || {};
    // The route on screen was verified before Stop was pressed; Stop only
    // ends the search for a shorter one. A pending offer stays: that shorter
    // route is verified too.
    const data = {
      ...last, status: "cancelled", can_continue: false, mode: "database",
      version: last.version || job.version, filters: last.filters || job.filters,
      coverage: last.coverage || job.coverage,
      paths: job.displayed ? last.paths || [] : [],
      route_status: job.displayed ? "verified_search_stopped" : "search_incomplete",
      message: job.displayed
        ? "The exact search was stopped. The route shown is verified by retrieved evidence; whether a shorter one exists was not established."
        : "The search was stopped before a route was verified; this result is incomplete.",
    };
    job.lastData = data;
    job.done = true;
    renderDisplayed(data, job, false);
    $("#deep-progress").classList.add("hidden");
    setLoading($("#find-connection"), false);
  }

  async function startDeepSearch({ source, target, revision, request, key }) {
    const job = {
      source, target, revision, request, key, mode: "database", jobId: null,
      version: state.dataset?.version, filters: canonicalFilters(), coverage: state.dataset?.coverage,
      cancelled: false, cancelSent: false, timer: null, done: false,
      continuing: false, progress: {}, lastData: null,
      // Versioned delivery: the last applied server version, the best route
      // the server reports, and the route this tab is showing.
      sequence: -1, best: null, displayed: null, rendered: false, note: null,
    };
    state.deepJob = job;
    hideRouteOffer();
    setLoading($("#find-connection"), true, "Exploring…");
    renderDeepProgress({ status: "searching", progress: job.progress }, job);
    $("#connection-empty").classList.add("hidden");
    $("#connection-results").classList.remove("hidden");
    try {
      let data;
      const retained = retainedDeepJob(job);
      if (retained) {
        job.jobId = retained;
        try { data = await api(deepEndpoint(job)); }
        catch (error) {
          if (!error.status || error.status >= 500 || error.status === 429) {
            if (!deepJobCurrent(job)) return;
            renderDeepProgress({ status: "searching", progress: {
              ...job.progress, stage: "Reconnecting to the running search…",
            } }, job);
            scheduleDeepPoll(job);
            return;
          }
          if (error.status !== 404) throw error;
          forgetDeepJob(job);
          job.jobId = null;
        }
      }
      if (!data) data = await api(urlWithFilters("/api/path", { source, target }));
      if (data.job_id) job.jobId = data.job_id;
      job.version = data.version || job.version;
      job.filters = canonicalFilters(data.filters || job.filters);
      job.coverage = data.coverage || job.coverage;
      job.progress = data.progress || job.progress;
      if (!deepJobCurrent(job)) {
        if (job.jobId) sendDeepCancel(job);
        return;
      }
      rememberDeepJob(job);
      consumeDeepResponse(data, job);
    } catch (e) {
      if (!deepJobCurrent(job)) {
        if (e.body?.job_id) { job.jobId = e.body.job_id; sendDeepCancel(job); }
        return;
      }
      job.done = true;
      renderDeepProgress({ status: "upstream_unavailable", message: e.message }, job);
      setLoading($("#find-connection"), false);
      state.deepJob = null;
    }
  }

  async function findPath() {
    clearStatus();
    if (!validateFilters()) return;
    if (!state.source || !state.target) {
      setStatus(
        "Choose a queryable researcher in both fields before finding a connection.",
        "warning",
      );
      return;
    }
    if (!canQuery(state.source) || !canQuery(state.target)) {
      setStatus(
        "One of the selected researchers is not included in this release. Choose another result.",
        "warning",
      );
      return;
    }
    const ys = Number($("#year-start").value),
      ye = Number($("#year-end").value);
    if (ys && ye && ys > ye) {
      setStatus(
        "The starting year must be before or equal to the ending year.",
        "error",
      );
      return;
    }
    const btn = $("#find-connection"),
      revision = state.revision,
      request = ++state.pathRequest,
      key = queryKey(),
      current = () =>
        revision === state.revision &&
        request === state.pathRequest &&
        key === queryKey();
    const extras = state.stopKeys.map((stop) => state[stop]);
    if (extras.length) {
      if (extras.some((person) => !person)) {
        setStatus("Choose a researcher in every added field, or remove the empty ones.", "warning");
        return;
      }
      if (extras.some((person) => !canQuery(person))) {
        setStatus("One of the added researchers is not included in this release. Choose another result.", "warning");
        return;
      }
      findWeb(groupPeople(), { revision, request, key });
      return;
    }
    startDeepSearch({ source: state.source.id, target: state.target.id, revision, request, key });
  }

  /* A group is answered as a web: the shortest connection between every
     pair, each an ordinary two-person search with its own proof. Searches
     spend their time waiting on the network, not working, so several run at
     once and the web is drawn as they arrive. Six, not more: one server
     instance admits eight searches at a time and turns the rest away as
     busy, and a browser's parallel requests tend to land on one instance. */
  const WEB_CONCURRENCY = 6;
  const PAIR_TIMEOUT_MS = 120000;

  /* "Busy" and "rate limited" mean ask again shortly, not "no route". */
  async function patiently(request) {
    for (let attempt = 0; ; attempt += 1) {
      try {
        return await request();
      } catch (error) {
        if (![503, 429].includes(error.status) || attempt >= 5) throw error;
        const wait = error.status === 429 ? 4000 : 400 * 2 ** attempt;
        await new Promise((resolve) => setTimeout(resolve, wait + Math.random() * 300));
      }
    }
  }

  async function runPair(source, target, current) {
    const began = performance.now();
    let data = await patiently(() => api(urlWithFilters("/api/path", { source, target })));
    let restarts = 0;
    while (data.status === "searching" && current()) {
      if (performance.now() - began > PAIR_TIMEOUT_MS) {
        return { ...data, status: "search_incomplete", pair_timed_out: true };
      }
      await new Promise((resolve) => setTimeout(resolve, 300));
      try {
        data = await patiently(() => api(`/api/search-jobs/${encodeURIComponent(data.job_id)}?mode=database`));
      } catch (error) {
        // The job lives in one server process and a poll can reach another;
        // start the same search again there, as the single search does.
        if (error.status === 404 && restarts < 2) {
          restarts += 1;
          data = await patiently(() => api(urlWithFilters("/api/path", { source, target })));
          continue;
        }
        throw error;
      }
    }
    return data;
  }

  async function findWeb(people, { revision, request, key }) {
    const current = () =>
      revision === state.revision && request === state.pathRequest && key === queryKey();
    const seen = new Set();
    for (const person of people) {
      const id = String(person.id);
      if (seen.has(id)) {
        setStatus(`${personName(person)} is in the list twice. Remove one of them.`, "warning");
        return;
      }
      seen.add(id);
    }
    const pairs = [];
    for (let i = 0; i < people.length; i += 1)
      for (let k = i + 1; k < people.length; k += 1)
        pairs.push({ a: people[i], b: people[k], data: null, error: null, done: false });
    hideRouteOffer();
    $("#relation-crosslink")?.remove();
    setLoading($("#find-connection"), true, "Exploring…");
    $("#connection-empty").classList.add("hidden");
    $("#connection-results").classList.remove("hidden");
    $("#path-message").className = "notice hidden";
    $("#path-cards").replaceChildren();
    $("#deep-progress").classList.remove("hidden");
    $("#deep-stop").classList.add("hidden");
    $("#deep-continue").classList.add("hidden");
    $("#deep-title").textContent = `Connecting ${people.length} people…`;
    const web = { people, pairs, selected: 0, began: performance.now() };
    state.web = web;
    let finished = 0;
    let drawTimer = null;
    const report = () => {
      $("#deep-summary").textContent =
        `${finished} of ${pairs.length} connections found. Every pair is its own shortest-connection search.`;
    };
    // Redraw as pairs arrive, but not on every one: a burst of twelve would
    // otherwise re-lay the graph twelve times in a few milliseconds.
    const redraw = () => {
      if (drawTimer) return;
      drawTimer = setTimeout(() => {
        drawTimer = null;
        if (current() && state.web === web) renderWeb(web, false);
      }, 350);
    };
    report();
    let next = 0;
    const worker = async () => {
      while (next < pairs.length && current()) {
        const pair = pairs[next++];
        try {
          pair.data = await runPair(pair.a.id, pair.b.id, current);
        } catch (error) {
          pair.error = error;
        }
        pair.done = true;
        finished += 1;
        if (current()) { report(); redraw(); }
      }
    };
    await Promise.all(Array.from({ length: Math.min(WEB_CONCURRENCY, pairs.length) }, worker));
    if (drawTimer) clearTimeout(drawTimer);
    if (!current()) return;
    $("#deep-progress").classList.add("hidden");
    setLoading($("#find-connection"), false);
    renderWeb(web, true);
  }

  /* ------------------------------------------- more than two people --- */

  /* Added people join the group; order does not matter. Each field reuses the
     ordinary picker - its key ("stop1", "stop2", ...) is the same handle
     "source" and "target" are. */
  state.stopKeys = [];
  let nextStop = 1;

  const groupPeople = () =>
    [state.source, state.target, ...state.stopKeys.map((key) => state[key])];

  function renumberStops() {
    const group = state.stopKeys.length > 0;
    state.stopKeys.forEach((key, index) => {
      const number = $(`[data-stop="${key}"] .stop-number`);
      if (number) number.textContent = String(index + 3);
    });
    // "From" and "To" read as a direction; a group has none.
    $('label[for="source-query"]').textContent = group ? "Person 1" : "From researcher";
    $('label[for="target-query"]').textContent = group ? "Person 2" : "To researcher";
    $("#swap-people").hidden = group;
    $(".identity-grid").classList.toggle("is-group", group);
    // setLoading restores the label it cached, so the cache is what changes.
    const find = $("#find-connection");
    find.dataset.label = group ? "Connect everyone →" : "Find connection →";
    if (!find.disabled) find.textContent = find.dataset.label;
  }

  function addStop(person = null) {
    const key = `stop${nextStop++}`;
    state.stopKeys.push(key);
    state[key] = null;
    const field = document.createElement("div");
    field.className = "identity-field route-stop";
    field.dataset.stop = key;
    field.innerHTML = `
      <label for="${key}-query">Person <span class="stop-number"></span></label>
      <div class="picker-wrap">
        <input id="${key}-query" name="${key}-query" type="search" autocomplete="off"
          placeholder="Name, INSPIRE ID, or ORCID" aria-controls="${key}-results"
          aria-expanded="false" /><button class="clear-picker" type="button"
          aria-label="Clear this person">×</button>
      </div>
      <div id="${key}-selected" class="selection" hidden></div>
      <div id="${key}-results" class="result-menu" role="listbox"
        aria-label="Suggestions for this person"></div>
      <div class="route-stop-tools">
        <button class="secondary-button" type="button" data-remove
          aria-label="Remove this person" title="Remove">✕</button>
      </div>`;
    $("#route-stops").append(field);
    setupSearch(key);
    field.querySelector(".clear-picker").addEventListener("click", () => clearPicker(key));
    field.querySelector("[data-remove]").addEventListener("click", () => removeStop(key));
    renumberStops();
    if (person) {
      state[key] = remember(person);
      renderPicker(key);
    }
    return key;
  }

  function removeStop(key) {
    invalidateResults();
    state.stopKeys = state.stopKeys.filter((item) => item !== key);
    delete state[key];
    $(`[data-stop="${key}"]`)?.remove();
    renumberStops();
    syncUrl();
  }

  function addGraphNode(person, kind = "") {
    if (!person?.id) return;
    const old = state.graph.nodes.get(person.id);
    if (old) {
      if (kind) old.kind = kind;
      return old;
    }
    const n = {
      person,
      x: 120 + Math.random() * 600,
      y: 100 + Math.random() * 280,
      kind,
      pinned: false,
    };
    state.graph.nodes.set(person.id, n);
    return n;
  }
  function drawPathGraph(data) {
    state.displayGraph = null;
    state.graph.nodes.clear();
    state.graph.edges = [];
    (data.paths || []).forEach((path, pi) => {
      (path.people || []).forEach((p) => {
        remember(p);
        addGraphNode(p, "path");
      });
      (path.edges || []).forEach((e) => {
        const key = [e.source, e.target].sort().join(":");
        const existing = state.graph.edges.find(
          (edge) => [edge.source, edge.target].sort().join(":") === key,
        );
        if (existing) existing.path ||= pi === 0;
        else state.graph.edges.push({ ...e, path: pi === 0 });
      });
    });
    const nodes = [...state.graph.nodes.values()];
    // Rows snake back and forth, so the next person on a long route sits
    // beside the last one instead of at the far end of the row below.
    nodes.forEach((n, idx) => {
      const row = Math.floor(idx / 4);
      const col = row % 2 ? 3 - (idx % 4) : idx % 4;
      n.x = 160 + col * 240;
      n.y = 160 + row * 165;
    });
    state.graph.scale = 1;
    state.graph.tx = 0;
    state.graph.ty = 0;
    renderGraph();
    requestAnimationFrame(() => {
      fitGraph();
      renderGraph();
    });
  }

  function pointerPos(e) {
    const r = $("#connection-graph").getBoundingClientRect();
    return {
      x: (e.clientX - r.left - state.graph.tx) / state.graph.scale,
      y: (e.clientY - r.top - state.graph.ty) / state.graph.scale,
    };
  }
  function startNodeDrag(e, n) {
    e.stopPropagation();
    state.graph.drag = {
      n,
      offset: { x: pointerPos(e).x - n.x, y: pointerPos(e).y - n.y },
      moved: false,
    };
    $("#graph-stage").setPointerCapture?.(e.pointerId);
  }
  function setupGraphInteractions() {
    const stage = $("#graph-stage");
    stage.addEventListener("pointerdown", (e) => {
      if (e.target === stage || e.target.tagName === "svg") {
        state.graph.pan = {
          x: e.clientX,
          y: e.clientY,
          tx: state.graph.tx,
          ty: state.graph.ty,
        };
        stage.setPointerCapture?.(e.pointerId);
      }
    });
    stage.addEventListener("pointermove", (e) => {
      if (state.graph.drag) {
        const p = pointerPos(e);
        state.graph.drag.n.x = p.x - state.graph.drag.offset.x;
        state.graph.drag.n.y = p.y - state.graph.drag.offset.y;
        state.graph.drag.n.pinned = true;
        state.graph.drag.moved = true;
        renderGraph();
      } else if (state.graph.pan) {
        state.graph.tx = state.graph.pan.tx + e.clientX - state.graph.pan.x;
        state.graph.ty = state.graph.pan.ty + e.clientY - state.graph.pan.y;
        renderGraph();
      }
    });
    stage.addEventListener("pointerup", () => {
      state.graph.drag = null;
      state.graph.pan = null;
    });
    stage.addEventListener(
      "wheel",
      (e) => {
        e.preventDefault();
        state.graph.scale = Math.min(
          2.8,
          Math.max(0.35, state.graph.scale * (e.deltaY < 0 ? 1.12 : 0.89)),
        );
        renderGraph();
      },
      { passive: false },
    );
    $$("[data-graph]").forEach((b) =>
      b.addEventListener("click", () => {
        const a = b.dataset.graph;
        if (a === "zoom-in")
          state.graph.scale = Math.min(2.8, state.graph.scale * 1.2);
        if (a === "zoom-out")
          state.graph.scale = Math.max(0.35, state.graph.scale * 0.8);
        if (a === "reset") {
          state.graph.scale = 1;
          state.graph.tx = 0;
          state.graph.ty = 0;
        }
        if (a === "fit") fitGraph();
        renderGraph();
      }),
    );
    $("#show-labels").addEventListener("change", renderGraph);
  }

  function personButton(p, extra = "") {
    const b = document.createElement("button");
    b.type = "button";
    b.className = "person-link";
    b.textContent = personName(p);
    if (extra) b.append(document.createTextNode(extra));
    b.addEventListener("click", () => openProfile(p.id));
    return b;
  }
  async function hydratePeople(ids) {
    const revision = state.revision;
    const mode = state.mode;
    const current = () => revision === state.revision && mode === state.mode;
    await Promise.all(
      [...new Set(ids)]
        .filter((x) => x && !state.people.has(x))
        .map(async (id) => {
          try {
            if (!current()) return;
            const d = await api(
              urlWithFilters(`/api/person/${encodeURIComponent(id)}`, { summary: "1" }),
            );
            if (!current()) return;
            remember({
              ...d.person,
              indexed: d.indexed ?? d.person?.indexed ?? false,
              queryable: d.queryable ?? d.person?.queryable ?? false,
            });
          } catch {
            /* ID is still shown if this profile is unavailable */
          }
        }),
    );
  }

  function jsonExport() {
    const result = state.lastPath || state.displayGraph;
    if (!result) return;
    const shown = {
      nodes: [...state.graph.nodes.values()].map((n) => ({
        person: n.person,
        x: n.x,
        y: n.y,
        pinned: n.pinned,
        kind: n.kind,
      })),
      edges: state.graph.edges,
      transform: {
        scale: state.graph.scale,
        x: state.graph.tx,
        y: state.graph.ty,
      },
    };
    const payload = {
      mode: result.mode || state.mode,
      snapshot_version: result.version || state.dataset?.version,
      filters: { min_authors: 1, ...(result.filters || filters()) },
      path_result: state.lastPath || null,
      // The export describes the route on screen, which may be an older
      // verified route than the server's best; both are named here.
      route_delivery: state.lastPath ? {
        route_status: state.lastPath.route_status ?? null,
        route_state: state.lastPath.route_state ?? null,
        displayed_route_id: state.lastPath.displayed_route_id ?? state.lastPath.paths?.[0]?.route_id ?? null,
        displayed_is_best: state.lastPath.displayed_is_best ?? (state.lastPath.best_route ? true : null),
        best_route: state.lastPath.best_route ?? null,
        sequence_number: state.lastPath.sequence_number ?? null,
        metrics: state.lastPath.metrics ?? null,
        events: state.lastPath.events ?? null,
      } : null,
      display_scope: state.displayGraph || null,
      displayed_graph: shown,
    };
    const blob = new Blob([JSON.stringify(payload, null, 2)], {
      type: "application/json",
    });
    download(
      blob,
      `hep-graph-path-${payload.snapshot_version || "snapshot"}.json`,
    );
  }
  function svgExport() {
    const result = state.lastPath || state.displayGraph;
    if (!result) return;
    const copy = $("#connection-graph").cloneNode(true);
    copy.setAttribute("xmlns", "http://www.w3.org/2000/svg");
    copy.setAttribute(
      "viewBox",
      `0 0 ${$("#graph-stage").clientWidth} ${$("#graph-stage").clientHeight}`,
    );
    const style = document.createElementNS(
      "http://www.w3.org/2000/svg",
      "style",
    );
    style.textContent =
      ".edge{stroke:#168b85;stroke-width:2.4;fill:none}.edge.phd{stroke:#b86c06;stroke-dasharray:7 4}.edge.selected{stroke-width:4}.edge-label{font:11px system-ui;fill:#4c626d;paint-order:stroke;stroke:#fff;stroke-width:3}.node circle{fill:#e8f7f5;stroke:#168b85;stroke-width:2.3}.node.path circle{fill:#d1f1ed;stroke-width:3.3}.node.expanded circle{fill:#fff1d8;stroke:#b86c06}.node text{font:12px system-ui;fill:#233e4b;paint-order:stroke;stroke:#fff;stroke-width:3}";
    copy.prepend(style);
    copy.querySelector("desc").textContent =
      `HEP Graph: bounded display of documented coauthorship ties. Filters ${JSON.stringify({ min_authors: 1, ...(result.filters || filters()) })}. ${coverageText(result.coverage)} The displayed neighborhood does not define the path calculation.`;
    const blob = new Blob([new XMLSerializer().serializeToString(copy)], {
      type: "image/svg+xml",
    });
    download(blob, "hep-graph-connection.svg");
  }
  function download(blob, name) {
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = name;
    document.body.append(a);
    a.click();
    a.remove();
    setTimeout(() => URL.revokeObjectURL(a.href), 1000);
  }
  async function resolvePerson(id) {
    const revision = state.revision;
    const mode = state.mode;
    const d = await api(
      urlWithFilters(`/api/person/${encodeURIComponent(id)}`, { summary: "1" }),
    );
    if (revision !== state.revision || mode !== state.mode) return null;
    return remember({
      ...d.person,
      indexed: d.indexed ?? d.person?.indexed ?? false,
      queryable: d.queryable ?? d.person?.queryable ?? false,
      indexed_publications: d.indexed_publications ?? d.person?.indexed_publications,
    });
  }

  function registerModelContext() {
    const mc = navigator.modelContext;
    if (!mc?.registerTool) return;
    try {
      mc.registerTool({
        name: "findConnection",
        description:
          "Find documented researcher connections in the published research data. Searches may return a resumable job that can be polled for progress.",
        inputSchema: {
          type: "object",
          properties: {
            source: { type: "string" },
            target: { type: "string" },
          },
          required: ["source", "target"],
        },
        execute: async ({ source, target }) =>
          api(urlWithFilters("/api/path", { source, target })),
      });
      mc.registerTool({
        name: "setFilters",
        description:
          "Set HEP Graph connection filters in the active research workspace.",
        inputSchema: {
          type: "object",
          properties: {
            min_authors: { type: "number" },
            max_authors: { type: "string" },
            min_shared: { type: "number" },
            year_start: { type: "number" },
            year_end: { type: "number" },
            genealogy: { type: "boolean" },
          },
        },
        execute: async (f) => {
          Object.entries(f).forEach(([k, v]) => {
            const el = $(`#${k.replace("_", "-")}`);
            if (el)
              el.type === "checkbox"
                ? (el.checked = Boolean(v))
                : (el.value = String(v));
          });
          updateFilterSummary();
          return { filters: filters() };
        },
      });
    } catch {
      /* WebMCP is optional and varies by browser */
    }
  }
  function phdDirection(edge) {
    if (!edge.types?.includes("phd")) return null;
    const record = (edge.phd || [])[0];
    return record
      ? { source: String(record.adviser), target: String(record.student) }
      : null;
  }
  function edgeInspector(edge) {
    const box = $("#edge-inspector");
    box.replaceChildren();
    box.classList.remove("hidden");
    const h = document.createElement("strong");
    h.textContent = `Relationship evidence: ${personName(byId(edge.source))} and ${personName(byId(edge.target))}`;
    box.append(h);
    box.append(evidenceItem(edge));
    box.focus?.();
  }
  function evidenceItem(edge) {
    const div = document.createElement("div");
    div.className = "evidence-item";
    const labels = [];
    if (edge.types?.includes("coauthor"))
      labels.push(
        `${edge.shared_works || 0} eligible shared work${edge.shared_works === 1 ? "" : "s"}`,
      );
    if (edge.phd?.length)
      labels.push(
        `${edge.phd?.length || 0} ${edge.types?.includes("coauthor") ? "supplemental " : ""}adviser record${edge.phd?.length === 1 ? "" : "s"}`,
      );
    div.append(
      document.createTextNode(labels.join(" · ") || "Documented relationship"),
    );
    for (const work of edge.works || []) {
      const row = document.createElement("div");
      const tag = document.createElement("span");
      tag.className = "tag";
      tag.textContent = "WORK";
      row.append(tag, link(work.title || `Work ${work.id}`, work.source_url));
      const date = work.date || work.year || "undated";
      row.append(
        document.createTextNode(
          ` · documented ${date} (${work.date_source || "date source not supplied"}) · full author count ${work.author_count ?? "not supplied"}`,
        ),
      );
      for (const doi of work.doi || []) {
        row.append(
          document.createTextNode(" · "),
          link(`DOI ${doi}`, `https://doi.org/${doi}`),
        );
      }
      for (const arxiv of work.arxiv || []) {
        const id = String(arxiv).replace(/^arXiv:/i, "");
        row.append(
          document.createTextNode(" · "),
          link(`arXiv ${id}`, `https://arxiv.org/abs/${id}`),
        );
      }
      if (work.retrieved_at)
        row.append(
          document.createTextNode(
            ` · retrieved ${formatDate(work.retrieved_at)}`,
          ),
        );
      div.append(row);
    }
    for (const phd of edge.phd || []) {
      const row = document.createElement("div");
      const tag = document.createElement("span");
      tag.className = "tag phd";
      tag.textContent = edge.types?.includes("coauthor") ? "PHD CONTEXT" : "PHD";
      row.append(
        tag,
        personButton(byId(String(phd.adviser))),
        document.createTextNode(" (adviser) → "),
        personButton(byId(String(phd.student))),
        document.createTextNode(
          ` (student) · ${degreeLabel(phd.degree)}${phd.year ? ` · ${phd.year}` : ""}`,
        ),
      );
      if (phd.uncertainty)
        row.append(
          document.createTextNode(
            ` · uncertainty: ${phd.uncertainty === "curated_relation_not_true" ? "INSPIRE link not marked curator-verified" : phd.uncertainty}`,
          ),
        );
      if (phd.source_kind === "institutional_historical_supplement")
        row.append(document.createTextNode(" · institutional historical source"));
      row.append(
        document.createTextNode(" · "),
        link(sourceLabel(phd), phd.source_url),
      );
      if (phd.retrieved_at)
        row.append(
          document.createTextNode(
            ` · retrieved ${formatDate(phd.retrieved_at)}`,
          ),
        );
      div.append(row);
    }
    return div;
  }
  function renderGraph() {
    const svg = $("#connection-graph"),
      vp = $(".viewport", svg),
      edgeLayer = $(".edge-layer", svg),
      nodeLayer = $(".node-layer", svg),
      ns = "http://www.w3.org/2000/svg";
    edgeLayer.replaceChildren();
    nodeLayer.replaceChildren();
    vp.setAttribute(
      "transform",
      `translate(${state.graph.tx} ${state.graph.ty}) scale(${state.graph.scale})`,
    );
    const el = (tag, attrs = {}) => {
      const x = document.createElementNS(ns, tag);
      Object.entries(attrs).forEach(([k, v]) => x.setAttribute(k, String(v)));
      return x;
    };
    if (!svg.querySelector("defs")) {
      const defs = el("defs"),
        m = el("marker", {
          id: "arrowhead",
          viewBox: "0 0 10 10",
          refX: 9,
          refY: 5,
          markerWidth: 7,
          markerHeight: 7,
          orient: "auto",
        });
      m.append(el("path", { d: "M 0 0 L 10 5 L 0 10 z", fill: "#b86c06" }));
      defs.append(m);
      svg.prepend(defs);
    }
    const addLine = (
      edge,
      a,
      b,
      kind,
      offset = 0,
      orientationA = a,
      orientationB = b,
    ) => {
      const dx = orientationB.x - orientationA.x,
        dy = orientationB.y - orientationA.y,
        len = Math.hypot(dx, dy) || 1,
        ox = (-dy / len) * offset,
        oy = (dx / len) * offset,
        lineDx = b.x - a.x,
        lineDy = b.y - a.y,
        lineLength = Math.hypot(lineDx, lineDy) || 1,
        startInset = kind === "phd" ? 20 : 0,
        endInset = kind === "phd" ? 24 : 0;
      const line = el("line", {
        x1: a.x + ox + (lineDx / lineLength) * startInset,
        y1: a.y + oy + (lineDy / lineLength) * startInset,
        x2: b.x + ox - (lineDx / lineLength) * endInset,
        y2: b.y + oy - (lineDy / lineLength) * endInset,
        class: `edge ${kind} ${edge.path ? "selected" : ""}`,
        tabindex: "0",
        role: "button",
        "aria-label": `${kind === "phd" ? "PhD adviser to student" : "Coauthorship"} evidence`,
      });
      if (kind === "phd") line.setAttribute("marker-end", "url(#arrowhead)");
      line.addEventListener("click", (e) => {
        e.stopPropagation();
        edgeInspector(edge);
      });
      line.addEventListener("keydown", (e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          edgeInspector(edge);
        }
      });
      edgeLayer.append(line);
    };
    state.graph.edges.forEach((edge) => {
      const a = state.graph.nodes.get(edge.source),
        b = state.graph.nodes.get(edge.target);
      if (!a || !b) return;
      if (edge.types?.includes("coauthor"))
        addLine(edge, a, b, "coauthor");
      else if (edge.types?.includes("phd")) {
        const d = phdDirection(edge),
          from = d && state.graph.nodes.get(d.source),
          to = d && state.graph.nodes.get(d.target);
        if (from && to) addLine(edge, from, to, "phd", 0, a, b);
      }
      if (state.graph.scale > 0.72 && edge.shared_works) {
        const t = el("text", {
          x: (a.x + b.x) / 2,
          y: (a.y + b.y) / 2 - 8,
          class: "edge-label",
        });
        t.textContent = `${edge.shared_works} work${edge.shared_works === 1 ? "" : "s"}`;
        edgeLayer.append(t);
      }
    });
    state.graph.nodes.forEach((n) => {
      const g = el("g", {
        class: `node ${n.kind || ""}`,
        transform: `translate(${n.x} ${n.y})`,
        tabindex: "0",
        role: "button",
        "aria-label": `Open profile for ${personName(n.person)}`,
      });
      g.append(el("circle", { r: 20 }));
      if ($("#show-labels").checked) {
        const t = el("text", { x: 0, y: 36, "text-anchor": "middle" });
        t.textContent = personName(n.person);
        g.append(t);
      }
      g.addEventListener("click", () => openProfile(n.person.id));
      g.addEventListener("keydown", (e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          openProfile(n.person.id);
        }
      });
      g.addEventListener("pointerdown", (e) => startNodeDrag(e, n));
      nodeLayer.append(g);
    });
  }
  async function expandNeighborhood(id) {
    const revision = state.revision,
      key = filterKey(),
      prior = state.lastPath;
    try {
      const data = await api(
        urlWithFilters(`/api/neighborhood/${encodeURIComponent(id)}`, {
          limit: 40,
        }),
      );
      if (
        revision !== state.revision ||
        key !== filterKey() ||
        prior !== state.lastPath
      )
        return;
      if (!state.graph.nodes.has(id)) addGraphNode(byId(id), "expanded");
      const available = Math.max(0, 100 - state.graph.nodes.size),
        people = (data.people || [])
          .filter((p) => !state.graph.nodes.has(p.id))
          .slice(0, available);
      people.forEach((p) => {
        remember(p);
        addGraphNode(p, "expanded");
      });
      (data.edges || []).forEach((e) => {
        if (
          state.graph.nodes.has(e.source) &&
          state.graph.nodes.has(e.target) &&
          !state.graph.edges.some(
            (x) =>
              [x.source, x.target].sort().join(":") ===
                [e.source, e.target].sort().join(":") &&
              JSON.stringify(x.types) === JSON.stringify(e.types),
          )
        )
          state.graph.edges.push({ ...e, path: false });
      });
      const anchor = state.graph.nodes.get(id),
        added = people.map((p) => state.graph.nodes.get(p.id));
      added.forEach((n, i) => {
        const ring = Math.floor(Math.sqrt(i / 8)),
          slots = Math.max(8, (ring + 1) * 10),
          angle = ((i % slots) / slots) * Math.PI * 2,
          radius = 125 + ring * 105;
        n.x = (anchor?.x || 360) + radius * Math.cos(angle);
        n.y = (anchor?.y || 240) + radius * Math.sin(angle);
      });
      renderGraph();
      if (!state.lastPath) {
        state.displayGraph = {
          type: "bounded_neighborhood",
          center: id,
          version: data.version || state.dataset?.version,
          filters: data.filters || filters(),
          coverage: data.coverage || state.dataset?.coverage,
          truncated: Boolean(data.truncated) || state.graph.nodes.size >= 100,
        };
        showTab("connections");
        $("#person-panel").classList.add("hidden");
        $("#connection-empty").classList.add("hidden");
        $("#connection-results").classList.remove("hidden");
        $("#copy-share").hidden = true;
        $("#path-cards").replaceChildren();
        $("#path-title").textContent = "Bounded local neighborhood";
        $("#graph-stage").classList.remove("is-compact");
        $("#relation-crosslink")?.remove();
        $("#path-meta").textContent =
          `${lastUpdatedText()} · ${filterDescription(state.displayGraph.filters)} · neighborhood around ${personName(byId(id))} · this display does not define the path calculation.`;
        fitGraph();
        renderGraph();
      }
      if (
        data.truncated ||
        available <
          (data.people || []).filter((p) => !state.graph.nodes.has(p.id)).length
      )
        setStatus(
          `The displayed neighborhood is bounded to ${Math.min(100, state.graph.nodes.size)} people. This does not alter path calculations.`,
          "warning",
        );
    } catch (e) {
      setStatus(e.message, "error");
    }
  }
  async function searchPeople(which) {
    const q = $(`#${which}-query`).value.trim();
    const token = state.searches[which]?.token;
    if (q.length < 2) {
      $(`#${which}-results`).replaceChildren();
      return;
    }
    try {
      const data = await api(
        urlWithFilters("/api/search", { q }),
      );
      if (
        token !== state.searches[which]?.token ||
        q !== $(`#${which}-query`).value.trim()
      )
        return;
      renderSearches(which, data);
    } catch (e) {
      if (
        token !== state.searches[which]?.token ||
        q !== $(`#${which}-query`).value.trim()
      )
        return;
      renderSearches(which, {
        status: "not_found",
        message: e.message,
        results: [],
      });
    }
  }
  function copyShare() {
    const value = location.href;
    const done = () => {
      const b = $("#copy-share");
      b.textContent = "Link copied";
      setTimeout(() => (b.textContent = "Copy share link"), 1500);
    };
    if (navigator.clipboard?.writeText)
      navigator.clipboard
        .writeText(value)
        .then(done)
        .catch(() => shareFallback(value));
    else shareFallback(value);
  }
  function shareFallback(value) {
    let input = $("#share-url");
    if (!input) {
      input = document.createElement("input");
      input.id = "share-url";
      input.className = "share-url";
      input.readOnly = true;
      $("#path-meta").append(document.createElement("br"), input);
    }
    input.value = value;
    input.focus();
    input.select();
  }
  function populateAbout(coverage) {
    const card = $("#about-coverage");
    if (!coverage) return;
    card.replaceChildren();
    const h = document.createElement("h2");
    h.textContent = "Data coverage";
    const p = document.createElement("p");
    p.textContent = `Connections reflect source records available as of ${updateDate(state.dataset?.source_cutoff || state.dataset?.created_at)}. An absent route does not prove that no connection exists outside this release.`;
    const meta = document.createElement("p");
    meta.className = "muted";
    const works = state.dataset?.counts?.works;
    meta.textContent = coverage.complete
      ? `This release holds the whole INSPIRE literature collection as of that date${
          works ? `: ${Number(works).toLocaleString()} papers eligible for coauthorship` : ""
        }.`
      : "This release holds only part of the INSPIRE literature collection, so results may miss connections.";
    card.append(h, p, meta);
  }
  function displayCoverage(coverage) {
    populateAbout(coverage);
  }
  async function loadDataset({ restoreQuery = true } = {}) {
    const revision = state.revision;
    try {
      const d = await api("/api/dataset?mode=database");
      if (revision !== state.revision) return;
      state.dataset = d;
      if (d.source_mode !== "database") throw new Error("The research data is unavailable.");
      state.mode = "database";
      if (d.capabilities?.genealogy !== true) {
        $("#genealogy").checked = false;
        $("#genealogy").disabled = true;
        $("#genealogy-note").textContent = "Not in this release; routes use coauthorship only.";
      } else {
        // The control shipped disabled while availability was unknown, and
        // nothing ever switched it on - so no one could use adviser records.
        $("#genealogy").disabled = false;
        $("#genealogy-note").textContent =
          "Adds documented adviser-to-student relations as hops of their own, alongside coauthorship.";
      }
      updateFilterSummary({ invalidate: false });
      $("#last-updated").textContent = lastUpdatedText();
      displayCoverage(d.coverage);
      clearStatus();
      if (!state.restoring) syncUrl();
      $("#version-warning").classList.add("hidden");
      const ids = restoreQuery
        ? [state.restore?.source, state.restore?.target].filter(Boolean)
        : [];
      if (ids.length && revision === state.revision) {
        try {
          // Everyone on a shared route is looked up at once; one at a time made
          // a ten-person link wait half a minute before searching.
          const then = state.restore.then || [];
          const everyone = await Promise.all([...ids, ...then].map(resolvePerson));
          if (revision !== state.revision) return;
          const people = everyone.slice(0, ids.length);
          const extra = everyone.slice(ids.length);
          if (state.restore.source)
            state.source = people[ids.indexOf(state.restore.source)];
          if (state.restore.target)
            state.target = people[ids.indexOf(state.restore.target)];
          renderPicker("source");
          renderPicker("target");
          extra.forEach((person) => { if (person) addStop(person); });
          syncUrl();
          schedulePreparation([state.source, state.target], 0, "restore");
          if (state.source && state.target) findPath();
        } catch (e) {
          setStatus(
            `This shared query could not restore one or more profiles: ${e.message}`,
            "warning",
          );
        }
      }
    } catch (e) {
      setStatus(`Could not load the research data: ${e.message}`, "error");
    }
  }

  const seconds = (value) => `${value < 10 ? Math.round(value * 10) / 10 : Math.round(value)}s`;

  // Title, message and meta line only: updated on every poll without
  // rebuilding the route cards, so an opened evidence panel stays open.
  function renderPathHeading(data) {
    state.lastPath = data;
    $("#copy-share").hidden = false;
    $("#connection-empty").classList.add("hidden");
    $("#connection-results").classList.remove("hidden");
    $("#connection-results").dataset.routeState = data.route_state || "";
    const message = statusForPath(data),
      msg = $("#path-message");
    msg.className = `notice ${message ? "" : "hidden"} ${data.status === "resource_limit" ? "warning" : ""}`;
    msg.textContent = message || "";
    const routes = data.paths?.length || 0;
    const hops = data.paths?.[0]?.hops;
    const hopText = Number.isInteger(hops) ? ` · ${hops} hop${hops === 1 ? "" : "s"}` : "";
    const rs = routes ? data.route_state : null;
    $("#path-title").textContent =
      rs === "EXACT_ROUTE_PROVEN"
        ? `Exact shortest path${hopText}${routes > 1 ? ` · ${routes} routes` : ""}`
        : rs === "VERIFIED_ROUTE_FOUND"
          ? `Verified route shown${hopText} · looking for a shorter one`
          : rs === "BETTER_ROUTE_AVAILABLE"
            ? `Verified route shown${hopText} · shorter route available`
            : rs === "VERIFIED_SEARCH_STOPPED"
              ? `Verified route${hopText} · search stopped`
              : rs === "SEARCH_INCOMPLETE"
                ? `Verified route${hopText} · exact search incomplete`
                : data.status === "ok"
                  ? `${routes} documented route${routes === 1 ? "" : "s"}`
                  : routes
                    ? `${routes} verified route${routes === 1 ? "" : "s"} · exact search incomplete`
                    : "Connection result";
    const scopedFilters = data.filters || filters();
    const hasPath = Boolean(data.paths?.length);
    const incomplete = ["search_incomplete", "resource_limit", "cancelled", "upstream_unavailable"].includes(data.status);
    const precision = data.global_shortest_proven === true
      ? "proven shortest in this release and filters"
      : hasPath
        ? "verified route; shortestness not established"
        : incomplete || data.route_status !== "no_path"
          ? "search incomplete; no no-path conclusion"
          : "no path in this release and filters";
    const retrievalInfo = data.retrieval || data.coverage?.retrieved;
    const retrieval = retrievalInfo
      ? ` · retrieved ${retrievalInfo.people ?? retrievalInfo.profiles ?? "?"} people / ${retrievalInfo.works ?? "?"} works${data.retrieval?.truncated || data.coverage?.partial ? " · truncated" : ""}`
      : "";
    const metrics = data.metrics || {};
    const timing = hasPath && metrics.time_to_first_verified_path != null
      ? ` · first route after ${seconds(metrics.time_to_first_verified_path)}${
        metrics.time_to_exact_proof != null ? `, proven shortest after ${seconds(metrics.time_to_exact_proof)}` : ""}`
      : "";
    $("#path-meta").textContent =
      `${lastUpdatedText()} · ${precision} · ${filterDescription(scopedFilters)}${retrieval}${timing}`;
    displayCoverage(data.coverage || state.dataset?.coverage);
  }

  function renderPath(data) {
    renderPathHeading(data);
    $("#path-cards").replaceChildren();
    $("#legend-stop").hidden = true;
    $("#graph-stage").classList.remove("is-tall");
    (data.paths || []).forEach((path, index) => {
      $("#path-cards").append(pathCard(path, `Route ${index + 1}`));
    });
    const people = new Set();
    (data.paths || []).forEach((path) => (path.people || []).forEach((p) => people.add(String(p.id))));
    $("#graph-stage").classList.toggle("is-compact", people.size > 0 && people.size <= 7);
    drawPathGraph(data);
    showAcademicRelation(data);
  }

  function pathCard(path, label, heading = "") {
      const card = document.createElement("article");
      card.className = "path-card";
      if (heading) {
        const title = document.createElement("p");
        title.className = "leg-label";
        title.textContent = heading;
        card.append(title);
      }
      const route = document.createElement("div");
      route.className = "path-route";
      path.people.forEach((p, i) => {
        remember(p);
        const b = personButton(p);
        route.append(b);
        if (i < path.people.length - 1) {
          const e = path.edges[i],
            d = e.types?.includes("coauthor") ? null : phdDirection(e),
            next = path.people[i + 1],
            arrow = document.createElement("span");
          arrow.className = "route-arrow";
          arrow.textContent = d
            ? String(d.source) === String(p.id) &&
              String(d.target) === String(next.id)
              ? "→"
              : "←"
            : "—";
          arrow.title = d
            ? "Actual adviser → student direction; this route may traverse it in either direction."
            : e.types?.includes("coauthor")
              ? "Coauthorship tie; supplemental adviser metadata does not add another hop."
              : "Documented relationship";
          route.append(arrow);
        }
      });
      card.append(route);
      const summary = document.createElement("p");
      summary.className = "edge-summary";
      summary.textContent = `${label} · ${path.hops} person-to-person hop${path.hops === 1 ? "" : "s"}.`;
      card.append(summary);
      (path.edges || []).forEach((e, i) => {
        const details = document.createElement("details");
        details.className = "evidence";
        const sum = document.createElement("summary");
        sum.textContent = `Evidence for hop ${i + 1}: ${personName(byId(e.source))} ↔ ${personName(byId(e.target))}`;
        details.append(sum, evidenceItem(e));
        card.append(details);
      });
      return card;
  }

  /* The web: a grid of how far apart every pair is, the route for the pair
     the reader picks, and one network drawn from every pair's route. */
  function renderWeb(web, final) {
    const { people, pairs } = web;
    const plural = (n, word) => `${n} ${word}${n === 1 ? "" : "s"}`;
    const done = pairs.filter((pair) => pair.done);
    const found = done.filter((pair) => pair.data?.paths?.length);
    const missing = done.filter((pair) => !pair.data?.paths?.length);
    // A pair the service could not search is not a pair with no route.
    const noRoute = missing.filter((pair) => !pair.error && pair.data?.route_status === "no_path");
    const unsearched = missing.length - noRoute.length;
    const proven = found.length === pairs.length &&
      pairs.every((pair) => pair.data?.global_shortest_proven === true);
    $("#path-title").textContent =
      `How ${people.length} people connect` +
      (final && noRoute.length ? ` · ${plural(noRoute.length, "pair")} without a route` : "") +
      (final && unsearched ? ` · ${plural(unsearched, "pair")} not settled` : "");
    const claim = !final
      ? `${done.length} of ${pairs.length} connections found so far`
      : unsearched
        ? "some pairs could not be settled - select them to see why; nothing is concluded about those"
        : noRoute.length
        ? "some pairs have no route in this release and filters; the rest are shown"
        : proven
          ? "every connection proven shortest in this release and filters"
          : "every connection verified; not every one is proven shortest";
    $("#path-meta").textContent =
      `${lastUpdatedText()} · ${claim} · ${filterDescription(found[0]?.data?.filters || filters())}` +
      (final ? ` · ${plural(pairs.length, "pair")} in ${((performance.now() - web.began) / 1000).toFixed(1)} s` : "");

    $("#path-cards").replaceChildren(webMatrix(web), webPairCard(web));

    // One network from every pair's route. The selected pair's route goes
    // first, so it is the one drawn as the highlighted path.
    const routes = found.map((pair) => pair.data.paths[0]);
    const selectedRoute = pairs[web.selected]?.data?.paths?.[0];
    drawPathGraph({
      paths: selectedRoute ? [selectedRoute, ...routes.filter((route) => route !== selectedRoute)] : routes,
    });
    const ids = people.map((person) => String(person.id));
    const group = new Set(ids);
    state.graph.nodes.forEach((node, id) => { if (group.has(String(id))) node.kind = "path stop"; });
    layoutWeb(ids);
    $("#graph-stage").classList.toggle("is-compact", state.graph.nodes.size <= 7);
    $("#graph-stage").classList.toggle("is-tall", state.graph.nodes.size > 16);
    $("#legend-stop").hidden = false;
    state.lastPath = {
      ...(found[0]?.data || {}), paths: routes, group: ids,
      pairs: pairs.map((pair) => ({
        a: String(pair.a.id), b: String(pair.b.id),
        route_status: pair.data?.route_status || null,
        proven_shortest: pair.data?.global_shortest_proven === true,
        hops: pair.data?.paths?.[0]?.hops ?? null,
        path: pair.data?.paths?.[0] || null })),
    };
    if (final) {
      $("#copy-share").hidden = false;
      syncUrl();
    }
  }

  const shortName = (person) => {
    const name = personName(person);
    return name.length > 18 ? `${name.slice(0, 17)}…` : name;
  };

  /* Hops between every pair; a cell opens that pair's route. */
  function webMatrix(web) {
    const { people, pairs } = web;
    const wrap = document.createElement("div");
    wrap.className = "web-matrix-wrap";
    const table = document.createElement("table");
    table.className = "web-matrix";
    const caption = document.createElement("caption");
    caption.textContent = "Hops between each pair. Select a number to see that route and its evidence.";
    table.append(caption);
    const head = document.createElement("tr");
    head.append(document.createElement("th"));
    people.forEach((person) => {
      const th = document.createElement("th");
      th.scope = "col";
      th.textContent = shortName(person);
      th.title = personName(person);
      head.append(th);
    });
    table.append(head);
    const pairIndex = (i, k) => pairs.findIndex((pair) =>
      (pair.a === people[i] && pair.b === people[k]) || (pair.a === people[k] && pair.b === people[i]));
    people.forEach((person, i) => {
      const row = document.createElement("tr");
      const th = document.createElement("th");
      th.scope = "row";
      th.textContent = shortName(person);
      th.title = personName(person);
      row.append(th);
      people.forEach((_, k) => {
        const td = document.createElement("td");
        if (i === k) {
          td.className = "web-self";
          td.textContent = "–";
        } else {
          const index = pairIndex(i, k);
          const pair = pairs[index];
          const cell = document.createElement("button");
          cell.type = "button";
          const hops = pair.data?.paths?.[0]?.hops;
          cell.textContent = !pair.done ? "…" : hops != null ? String(hops)
            : pair.data?.route_status === "no_path" ? "none" : "?";
          cell.title = `${personName(pair.a)} and ${personName(pair.b)}`;
          if (index === web.selected) cell.classList.add("is-selected");
          cell.disabled = !pair.done;
          cell.addEventListener("click", () => {
            web.selected = index;
            renderWeb(web, pairs.every((item) => item.done));
          });
          td.append(cell);
        }
        row.append(td);
      });
      table.append(row);
    });
    wrap.append(table);
    return wrap;
  }

  function webPairCard(web) {
    const pair = web.pairs[web.selected];
    const label = pair ? `${personName(pair.a)} and ${personName(pair.b)}` : "";
    if (!pair?.done) {
      const card = document.createElement("article");
      card.className = "path-card";
      card.textContent = `Finding the connection between ${label}…`;
      return card;
    }
    const path = pair.data?.paths?.[0];
    if (path) {
      const card = pathCard(path, "This connection", label);
      if (pair.data.global_shortest_proven !== true) {
        const note = document.createElement("p");
        note.className = "edge-summary";
        note.textContent = "This connection is verified; a shorter one was not ruled out.";
        card.append(note);
      }
      return card;
    }
    const card = document.createElement("article");
    card.className = "path-card leg-broken";
    const title = document.createElement("p");
    title.className = "leg-label";
    title.textContent = label;
    const why = document.createElement("p");
    why.className = "edge-summary";
    why.textContent = pair.error
      ? `This pair could not be searched: ${pair.error.message}`
      : pair.data?.route_status === "no_path"
        ? "No route connects these two in this release and filters."
        : "The search for this pair did not finish, so nothing is concluded about it.";
    card.append(title, why);
    return card;
  }

  /* A small force layout: the chosen people start on a ring, everyone else
     starts between the people they link, then springs along edges and a
     gentle push between all nodes settle it. Deterministic, so the same web
     is drawn the same way twice. */
  function layoutWeb(anchorIds) {
    const nodes = [...state.graph.nodes.values()];
    const index = new Map(nodes.map((node, i) => [String(node.person.id), i]));
    const n = nodes.length;
    if (!n) return;
    const radius = Math.max(170, 45 * anchorIds.length);
    const cx = 480;
    const cy = 320;
    const px = new Float64Array(n);
    const py = new Float64Array(n);
    const placed = new Uint8Array(n);
    anchorIds.forEach((id, k) => {
      const i = index.get(id);
      if (i == null) return;
      const angle = (2 * Math.PI * k) / anchorIds.length - Math.PI / 2;
      px[i] = cx + radius * Math.cos(angle);
      py[i] = cy + radius * Math.sin(angle);
      placed[i] = 1;
    });
    const links = state.graph.edges
      .map((edge) => [index.get(String(edge.source)), index.get(String(edge.target))])
      .filter(([a, b]) => a != null && b != null);
    // Seed each unplaced node at the average of its placed neighbours,
    // repeating so chains fill in from both ends; the rest start central.
    for (let round = 0; round < n; round += 1) {
      let changed = false;
      for (let i = 0; i < n; i += 1) {
        if (placed[i]) continue;
        let sx = 0, sy = 0, count = 0;
        links.forEach(([a, b]) => {
          const other = a === i ? b : b === i ? a : -1;
          if (other >= 0 && placed[other]) { sx += px[other]; sy += py[other]; count += 1; }
        });
        if (count) {
          px[i] = sx / count + ((i * 37) % 23) - 11;
          py[i] = sy / count + ((i * 53) % 23) - 11;
          placed[i] = 2;
          changed = true;
        }
      }
      if (!changed) break;
    }
    for (let i = 0; i < n; i += 1) if (!placed[i]) { px[i] = cx; py[i] = cy; }
    const ideal = 150;
    const steps = 260;
    for (let step = 0; step < steps; step += 1) {
      const fx = new Float64Array(n);
      const fy = new Float64Array(n);
      for (let i = 0; i < n; i += 1)
        for (let k = i + 1; k < n; k += 1) {
          let dx = px[i] - px[k];
          let dy = py[i] - py[k];
          let d2 = dx * dx + dy * dy;
          if (d2 < 1) { dx = 1; dy = 0; d2 = 1; }
          const push = ((ideal * ideal) / d2) * 0.05;
          fx[i] += dx * push; fy[i] += dy * push;
          fx[k] -= dx * push; fy[k] -= dy * push;
        }
      links.forEach(([a, b]) => {
        const dx = px[b] - px[a];
        const dy = py[b] - py[a];
        const d = Math.max(1, Math.hypot(dx, dy));
        const pull = (d - ideal) * 0.06;
        fx[a] += (dx / d) * pull; fy[a] += (dy / d) * pull;
        fx[b] -= (dx / d) * pull; fy[b] -= (dy / d) * pull;
      });
      const cool = 1 - step / steps;
      for (let i = 0; i < n; i += 1) {
        // The chosen people give the web its shape; they move far less.
        const weight = placed[i] === 1 ? 0.15 : 1;
        px[i] += Math.max(-30, Math.min(30, fx[i])) * cool * weight;
        py[i] += Math.max(-30, Math.min(30, fy[i])) * cool * weight;
      }
    }
    // The panel is far wider than tall and a force layout comes out round,
    // so flatten it towards the panel's shape - never so far that rows merge.
    const stage = $("#graph-stage");
    const aspect = stage.clientHeight / Math.max(1, stage.clientWidth);
    let minY = Infinity, maxY = -Infinity, minX = Infinity, maxX = -Infinity;
    for (let i = 0; i < n; i += 1) {
      minX = Math.min(minX, px[i]); maxX = Math.max(maxX, px[i]);
      minY = Math.min(minY, py[i]); maxY = Math.max(maxY, py[i]);
    }
    const spanX = Math.max(1, maxX - minX);
    const spanY = Math.max(1, maxY - minY);
    const squash = spanY / spanX > aspect ? Math.max(0.5, (aspect * spanX) / spanY) : 1;
    const midY = (minY + maxY) / 2;
    nodes.forEach((node, i) => { node.x = px[i]; node.y = midY + (py[i] - midY) * squash; });
  }

  /* ---------------------------------------- the other kind of connection --- */

  /* Coauthorship and supervision are different questions about the same two
     people. A route result says, in one line, how they are related through
     advisers too, and opens the full answer on the family map. */
  async function showAcademicRelation(data) {
    const old = $("#relation-crosslink");
    if (old) old.remove();
    const route = (data.paths || [])[0];
    if (!route || !state.source || !state.target) return;
    const a = { id: String(state.source.id), name: personName(state.source) };
    const b = { id: String(state.target.id), name: personName(state.target) };
    const box = document.createElement("div");
    box.id = "relation-crosslink";
    box.className = "relation-crosslink is-quiet";
    box.textContent = "Checking adviser records for these two…";
    $("#path-cards").after(box);
    const revision = state.revision;
    let relation;
    try {
      relation = await api(`/api/relationship?a=${encodeURIComponent(a.id)}&b=${encodeURIComponent(b.id)}`);
    } catch {
      box.remove();
      return;
    }
    if (revision !== state.revision || !box.isConnected) return;
    box.replaceChildren();
    if (relation.status === "ok" || relation.status === "connected") {
      box.classList.remove("is-quiet");
      const text = document.createElement("span");
      const term = document.createElement("span");
      term.className = "relate-term";
      term.textContent = relation.label;
      text.append(document.createTextNode("Through adviser records: "), term, document.createTextNode("."));
      const open = document.createElement("button");
      open.type = "button";
      open.className = "secondary-button";
      open.textContent = "Show on the family map";
      open.addEventListener("click", () => openRelationshipFinder(a, b));
      box.append(text, open);
    } else if (relation.status === "no_relation") {
      box.textContent = "No chain of adviser records connects these two in this release.";
    } else {
      box.textContent = "Adviser records do not include one of these two, so how they are related academically is unknown here.";
    }
  }

  function waitForMap(timeout = 30000) {
    return new Promise((resolve) => {
      const began = Date.now();
      const check = () => {
        if (mapState.status === "ready") return resolve(true);
        if (["error", "unavailable"].includes(mapState.status) || Date.now() - began > timeout)
          return resolve(false);
        setTimeout(check, 150);
      };
      check();
    });
  }

  async function openRelationshipFinder(a, b) {
    showTab("lineage-map");
    $("#relate-form").scrollIntoView({ behavior: "smooth", block: "start" });
    mapState.relate = { a: { ...a }, b: { ...b } };
    $("#relate-a").value = a.name;
    $("#relate-b").value = b.name;
    $("#relate-run").disabled = false;
    // The answer needs no map, but lighting the route on it does.
    await waitForMap();
    runRelationship({ preventDefault() {} });
  }

  function openCoauthorRoute(a, b) {
    choosePerson("source", { id: a.id, name: a.name });
    choosePerson("target", { id: b.id, name: b.name });
    showTab("connections");
    $("#search-form").scrollIntoView({ behavior: "smooth", block: "start" });
    $("#search-form").requestSubmit();
  }
  function fitGraph() {
    const ns = [...state.graph.nodes.values()];
    if (!ns.length) return;
    const width = $("#graph-stage").clientWidth,
      height = $("#graph-stage").clientHeight,
      labelPad = $("#show-labels").checked ? 130 : 60,
      xs = ns.map((n) => n.x),
      ys = ns.map((n) => n.y),
      minX = Math.min(...xs) - labelPad,
      maxX = Math.max(...xs) + labelPad,
      minY = Math.min(...ys) - 60,
      maxY = Math.max(...ys) + ($("#show-labels").checked ? 88 : 60);
    state.graph.scale = Math.min(
      1.6,
      Math.max(0.15, Math.min(width / (maxX - minX), height / (maxY - minY))),
    );
    state.graph.tx = width / 2 - (state.graph.scale * (minX + maxX)) / 2;
    state.graph.ty = height / 2 - (state.graph.scale * (minY + maxY)) / 2;
  }
  async function openProfile(id) {
    const panel = $("#person-panel"),
      content = $("#person-content"),
      revision = state.revision,
      request = ++state.profileRequest,
      key = filterKey(),
      current = () =>
        revision === state.revision &&
        request === state.profileRequest &&
        key === filterKey();
    panel.classList.remove("hidden");
    content.textContent = "Loading researcher profile…";
    try {
      const d = await api(
        urlWithFilters(`/api/person/${encodeURIComponent(id)}`),
      );
      if (!current()) return;
      if (d.status && d.status !== "ok")
        throw new Error(d.message || "Profile unavailable.");
      const p = remember(d.person),
        ties = [...(d.advisers || []), ...(d.students || [])];
      (d.collaborators || []).forEach((x) => remember(x.person));
      await hydratePeople(
        ties.map((x) => (x.adviser === id ? x.student : x.adviser)),
      );
      if (!current()) return;
      content.replaceChildren();
      const title = document.createElement("div"),
        h = document.createElement("h2"),
        meta = document.createElement("p");
      title.className = "profile-title";
      h.textContent = personName(p);
      meta.className = "profile-meta";
      meta.textContent = `${p.id}${p.profile_status === "literature_only" ? " · no INSPIRE author profile" : ""}${p.orcid ? ` · ORCID ${p.orcid}` : ""}${p.affiliations?.length ? ` · Affiliations reported in retrieved sources: ${p.affiliations.join("; ")}` : " · Affiliations reported in retrieved sources: not supplied"}`;
      title.append(h, meta);
      if (p.source_url)
        title.append(link("Open source profile ↗", p.source_url));
      content.append(title);
      const stats = document.createElement("div");
      stats.className = "profile-stats";
      for (const [field, label] of [
        ["indexed_publications", "Indexed works"],
        ["eligible_publications", "Eligible works"],
        ["coauthor_count", "Unique coauthors"],
        ["combined_degree", "Combined degree"],
      ]) {
        const cell = document.createElement("div"),
          number = document.createElement("strong"),
          caption = document.createElement("span");
        number.dataset.stat = field;
        const value = d[field];
        number.textContent =
          value == null ? "Not supplied" : String(value);
        caption.textContent = label;
        cell.append(number, caption);
        stats.append(cell);
      }
      content.append(stats);
      const scope = document.createElement("p");
      scope.className = "profile-meta";
      scope.textContent = `${lastUpdatedText()}. Counts refer to this release, not all upstream publications. Active filters: ${filterDescription(d.filters || filters())}. Paper eligibility controls eligible works; the repeat threshold controls coauthor ties.`;
      content.append(scope);
      const actions = document.createElement("div");
      actions.className = "profile-actions";
      [
        ["Use as From", "source"],
        ["Use as To", "target"],
      ].forEach(([text, slot]) => {
        const b = document.createElement("button");
        b.className = "secondary-button";
        b.type = "button";
        b.textContent = text;
        b.addEventListener("click", () => {
          invalidateResults();
          state[slot] = {
            ...p,
            indexed: d.indexed ?? p.indexed ?? false,
            queryable: d.queryable ?? p.queryable ?? false,
          };
          renderPicker(slot);
          syncUrl();
          schedulePreparation([state[slot]], 0, slot);
          showTab("connections");
        });
        actions.append(b);
      });
      const lineage = document.createElement("button");
      lineage.className = "secondary-button";
      lineage.type = "button";
      lineage.textContent = "View academic lineage";
      lineage.addEventListener("click", () => setLineageRoot({ ...p }));
      actions.append(lineage);
      const expand = document.createElement("button");
      expand.className = "secondary-button";
      expand.type = "button";
      expand.textContent = "Add graph neighborhood";
      expand.addEventListener("click", () => expandNeighborhood(id));
      actions.append(expand);
      content.append(actions);
      const reach = document.createElement("p");
      reach.className = "profile-meta";
      reach.textContent = `Reachability: ${
        d.reachability
          ? Object.entries(d.reachability)
              .map(
                ([k, v]) =>
                  `${k.replaceAll("_", " ")} ${typeof v === "object" ? JSON.stringify(v) : v}`,
              )
              .join(" · ")
          : "not supplied"
      }`;
      content.append(reach);
      const coll = document.createElement("div"),
        ch = document.createElement("h3"),
        ul = document.createElement("ul");
      coll.className = "profile-section";
      ch.textContent = "Collaborators";
      ul.className = "profile-list";
      (d.collaborators || []).slice(0, 15).forEach((x) => {
        const li = document.createElement("li");
        li.append(
          personButton(
            x.person,
            ` · ${x.shared_works} shared work${x.shared_works === 1 ? "" : "s"}`,
          ),
        );
        ul.append(li);
      });
      if (!ul.children.length)
        ul.textContent = "No eligible coauthor ties under these filters.";
      coll.append(ch, ul);
      content.append(coll);
      const phd = document.createElement("div"),
        ph = document.createElement("h3"),
        pu = document.createElement("ul");
      phd.className = "profile-section";
      ph.textContent = "Documented adviser ties";
      pu.className = "profile-list";
      ties.forEach((x) => {
        const other = x.adviser === id ? x.student : x.adviser,
          side = x.adviser === id ? "Student" : "Adviser",
          li = document.createElement("li");
        li.append(
          document.createTextNode(`${side}: `),
          personButton(byId(other)),
          document.createTextNode(
            ` · ${degreeLabel(x.degree)} · ${x.year || "year unknown"} · `,
          ),
          link(sourceLabel(x), x.source_url),
        );
        pu.append(li);
      });
      if (!pu.children.length)
        pu.textContent = "No adviser records in this release.";
      phd.append(ph, pu);
      content.append(phd);
      displayCoverage(d.coverage || state.dataset?.coverage);
    } catch (e) {
      if (current()) content.textContent = `Profile unavailable: ${e.message}`;
    }
  }
  // --- Academic lineage -----------------------------------------------------
  // Adviser→student records only. A person may have several advisers, so the
  // rendering groups people by generation and lists every documented relation
  // that reached them rather than assuming a single parent.
  /* Supervision is recorded in more than one place, and they are not equally
     direct: a thesis names its own supervisors, an author profile is a claim
     on the student's own record, and a Wikidata relation is not INSPIRE's at
     all. Say which one a relation rests on. */
  function sourceLabel(relation) {
    const record = relation.source_record;
    if (record == null || record === "") return "source record";
    if (relation.source_kind === "wikidata") return `Wikidata ${record}`;
    if (/^https?:\/\//.test(record)) {
      /* A relation cited to a published page is named by where it lives. */
      try {
        return new URL(record).hostname.replace(/^www\./, "");
      } catch {
        return "cited source";
      }
    }
    return relation.source_kind === "thesis"
      ? `thesis ${record}`
      : `author record ${record}`;
  }
  const degreeLabels = {
    phd: "PhD",
    doctorate: "Doctorate",
    doctoral: "Doctoral degree",
    habilitation: "Habilitation",
    master: "Master's",
    masters: "Master's",
    diploma: "Diploma",
    bachelor: "Bachelor's",
    bachelors: "Bachelor's",
    other: "Degree not recorded by INSPIRE",
  };
  const degreeLabel = (degree) =>
    degree
      ? degreeLabels[String(degree).toLowerCase()] || String(degree)
      : "degree not recorded";
  const lineageDirection = () =>
    $("#lineage-direction").value === "descendants"
      ? "descendants"
      : "ancestors";
  const lineageDepth = () => {
    const value = Number($("#lineage-depth").value);
    return Number.isInteger(value) && value >= 1 && value <= 6 ? value : 3;
  };
  const inspireAuthorUrl = (id) =>
    /^\d+$/.test(String(id ?? ""))
      ? `https://inspirehep.net/authors/${String(id)}`
      : null;
  const generationLabel = (generation, direction, count) => {
    if (generation === 0) return "Selected researcher";
    if (!Number.isFinite(generation)) return "Generation not recorded";
    if (generation === 1)
      return direction === "ancestors"
        ? count === 1
          ? "Adviser"
          : "Advisers"
        : count === 1
          ? "Student"
          : "Students";
    return `${generation} generation${generation === 1 ? "" : "s"} ${direction === "ancestors" ? "back" : "forward"}`;
  };
  const lineageNotice = (message, kind = "") => {
    const box = $("#lineage-message");
    box.className = `notice ${kind}`;
    box.textContent = message;
  };
  function renderLineagePicker() {
    const holder = $("#lineage-selected");
    holder.replaceChildren();
    holder.hidden = !state.lineage;
    if (!state.lineage) return;
    $("#lineage-query").value = personName(state.lineage);
    const sub = document.createElement("span");
    sub.textContent = `INSPIRE ${state.lineage.id}`;
    holder.append(sub);
  }
  function setLineageRoot(person) {
    if (!person?.id) return;
    // A lineage entry without a name must not overwrite a known profile.
    const known = state.people.get(String(person.id));
    state.lineage = person.name ? remember({ ...person }) : known || person;
    $("#lineage-results").replaceChildren();
    $("#lineage-results").classList.remove("inline-search-notice");
    $("#lineage-query").setAttribute("aria-expanded", "false");
    renderLineagePicker();
    $("#person-panel").classList.add("hidden");
    showTab("lineage");
    loadLineage();
  }
  function clearLineage() {
    state.lineageRequest++;
    state.lineage = null;
    $("#lineage-query").value = "";
    $("#lineage-results").replaceChildren();
    $("#lineage-results").classList.remove("inline-search-notice");
    $("#lineage-query").setAttribute("aria-expanded", "false");
    renderLineagePicker();
    $("#lineage-generations").replaceChildren();
    lineageNotice("", "hidden");
    $("#lineage-output").classList.add("hidden");
    $("#lineage-empty").classList.remove("hidden");
    setLoading($("#lineage-run"), false);
  }
  function lineagePersonButton(person) {
    const b = document.createElement("button");
    b.type = "button";
    b.className = "person-link";
    b.textContent = personName(person);
    b.title = `Show the academic lineage of ${personName(person)}`;
    b.addEventListener("click", () => setLineageRoot(person));
    return b;
  }
  function lineageRelationRow(edge, lookup, direction) {
    const li = document.createElement("li");
    li.className = "lineage-relation";
    const counterpart = lookup(
      direction === "ancestors" ? edge.student : edge.adviser,
    );
    li.append(
      document.createTextNode(
        direction === "ancestors" ? "Adviser of " : "Student of ",
      ),
      lineagePersonButton(counterpart),
      document.createTextNode(` · ${degreeLabel(edge.degree)}`),
    );
    if (edge.source_record != null && edge.source_record !== "") {
      const record = document.createElement("span");
      record.className = "lineage-id";
      record.textContent = ` · ${sourceLabel(edge)}`;
      li.append(record);
    }
    return li;
  }
  function lineagePersonCard(person, relations, lookup, direction, isRoot) {
    const li = document.createElement("li");
    li.className = "lineage-person";
    const head = document.createElement("div");
    head.className = "lineage-person-head";
    head.append(lineagePersonButton(person));
    const id = document.createElement("span");
    id.className = "lineage-id";
    id.textContent = `INSPIRE ${person.id}`;
    head.append(id);
    const href = person.source_url || inspireAuthorUrl(person.id);
    if (href && safeHref(href)) head.append(link("Profile ↗", href));
    li.append(head);
    if (person.details_unavailable === true) {
      const note = document.createElement("p");
      note.className = "lineage-note";
      const reason = String(person.reason || "").trim();
      note.textContent = `Name not retrieved${reason ? `: ${reason.replace(/[.;:,]$/, "")}` : ""}. The INSPIRE identifier is shown instead.`;
      li.append(note);
    }
    if (relations.length > 1) {
      const note = document.createElement("p");
      note.className = "lineage-note";
      note.textContent =
        direction === "ancestors"
          ? `Documented as adviser to ${relations.length} people shown here.`
          : `Documented as student of ${relations.length} people shown here.`;
      li.append(note);
    }
    if (isRoot) return li;
    const list = document.createElement("ul");
    list.className = "lineage-relations";
    relations.forEach((edge) =>
      list.append(lineageRelationRow(edge, lookup, direction)),
    );
    if (!relations.length) {
      const empty = document.createElement("li");
      empty.className = "lineage-relation";
      empty.textContent =
        "No relation record accompanied this person in the response.";
      list.append(empty);
    }
    li.append(list);
    return li;
  }
  function lineageGroup(generation, entries, direction, lookup, relations) {
    const section = document.createElement("section");
    section.className = `lineage-generation${generation === 0 ? " is-root" : ""}`;
    const headingId = `lineage-gen-${Number.isFinite(generation) ? generation : "unknown"}`;
    section.setAttribute("aria-labelledby", headingId);
    const heading = document.createElement("h3");
    heading.id = headingId;
    heading.textContent = `${generationLabel(generation, direction, entries.length)} · ${entries.length} ${entries.length === 1 ? "person" : "people"}`;
    section.append(heading);
    const list = document.createElement("ul");
    list.className = "lineage-people";
    entries.forEach((person) =>
      list.append(
        lineagePersonCard(
          person,
          relations.get(String(person.id)) || [],
          lookup,
          direction,
          generation === 0,
        ),
      ),
    );
    section.append(list);
    return section;
  }
  function renderLineage(data, context) {
    const { person, direction, depth } = context;
    const holder = $("#lineage-generations");
    holder.replaceChildren();
    const status = data.status || "ok";
    if (status !== "ok") {
      $("#lineage-heading").textContent =
        status === "unavailable"
          ? "Academic lineage is not available"
          : "No adviser record found";
      $("#lineage-meta").textContent =
        status === "unavailable"
          ? "Nothing is claimed about this researcher's advisers or students."
          : `${personName(person)} · INSPIRE ${person.id}`;
      lineageNotice(
        data.message ||
          (status === "unavailable"
            ? "Adviser records are not configured in this release."
            : "This researcher was not found in the adviser records of this release. That silence describes the records, not the researcher."),
      );
      return;
    }
    const root = data.person && data.person.id != null ? data.person : person;
    if (root.name) remember({ ...root });
    const shown =
      data.direction === "descendants"
        ? "descendants"
        : data.direction === "ancestors"
          ? "ancestors"
          : direction;
    $("#lineage-heading").textContent =
      shown === "ancestors"
        ? `Academic ancestors of ${personName(root)}`
        : `Academic descendants of ${personName(root)}`;
    const people = Array.isArray(data.people) ? data.people : [];
    const edges = Array.isArray(data.edges) ? data.edges : [];
    const known = new Map();
    people.forEach((p) => {
      if (p && p.id != null && !known.has(String(p.id)))
        known.set(String(p.id), p);
    });
    const lookup = (id) =>
      known.get(String(id)) ||
      (String(id) === String(root.id) ? root : null) ||
      state.people.get(String(id)) || { id: String(id) };
    // The near side of an edge is the person further from the root: their
    // adviser links for ancestors, their student links for descendants.
    const nearKey = shown === "ancestors" ? "adviser" : "student";
    const relations = new Map();
    edges.forEach((edge) => {
      if (!edge || edge[nearKey] == null) return;
      const key = String(edge[nearKey]);
      if (!relations.has(key)) relations.set(key, []);
      relations.get(key).push(edge);
    });
    const groups = new Map();
    const seen = new Map();
    people.forEach((p) => {
      if (!p || p.id == null) return;
      const raw = Number(p.generation);
      const generation = Number.isFinite(raw) && raw > 0 ? raw : NaN;
      const key = Number.isFinite(generation) ? generation : "unknown";
      if (!groups.has(key)) {
        groups.set(key, []);
        seen.set(key, new Set());
      }
      if (seen.get(key).has(String(p.id))) return;
      seen.get(key).add(String(p.id));
      groups.get(key).push(p);
    });
    const ordered = [...groups.keys()]
      .filter((k) => k !== "unknown")
      .sort((a, b) => a - b);
    if (groups.has("unknown")) ordered.push("unknown");
    holder.append(
      lineageGroup(0, [root], shown, lookup, new Map()),
      ...ordered.map((key) =>
        lineageGroup(
          key === "unknown" ? NaN : key,
          groups
            .get(key)
            .slice()
            .sort((a, b) => personName(a).localeCompare(personName(b))),
          shown,
          lookup,
          relations,
        ),
      ),
    );
    const total = [...groups.values()].reduce((n, list) => n + list.length, 0);
    $("#lineage-meta").textContent =
      `${lastUpdatedText()} · ${shown === "ancestors" ? "adviser" : "student"} records to ${data.depth ?? depth} generation${(data.depth ?? depth) === 1 ? "" : "s"} · ` +
      `${total} ${total === 1 ? "person" : "people"} · ${edges.length} documented relation${edges.length === 1 ? "" : "s"} · ` +
      `${data.version ? `records ${data.version}` : "record version not supplied"}`;
    if (data.truncated === true)
      lineageNotice(
        "This lineage is truncated: more documented relations exist than are shown. Open a person shown here to continue from them, or reduce the depth.",
        "warning",
      );
    else if (!total)
      lineageNotice(
        shown === "ancestors"
          ? "No adviser is recorded for this researcher in this release. That is a gap in the records, not proof that none exists."
          : "No documented student is recorded for this researcher in this release. That is a gap in the records, not proof that none exists.",
      );
    else lineageNotice("", "hidden");
  }
  async function loadLineage() {
    const person = state.lineage;
    if (!person?.id) {
      clearLineage();
      return;
    }
    const direction = lineageDirection(),
      depth = lineageDepth(),
      request = ++state.lineageRequest,
      current = () =>
        request === state.lineageRequest && state.lineage === person;
    const button = $("#lineage-run");
    setLoading(button, true, "Loading…");
    $("#lineage-empty").classList.add("hidden");
    $("#lineage-output").classList.remove("hidden");
    $("#lineage-generations").replaceChildren();
    lineageNotice("", "hidden");
    $("#lineage-heading").textContent =
      direction === "ancestors"
        ? `Academic ancestors of ${personName(person)}`
        : `Academic descendants of ${personName(person)}`;
    $("#lineage-meta").textContent = "Loading documented adviser records…";
    try {
      const u = new URL(
        `/api/ancestry/${encodeURIComponent(person.id)}`,
        location.origin,
      );
      u.searchParams.set("direction", direction);
      u.searchParams.set("depth", String(depth));
      const data = await api(u.pathname + "?" + u.searchParams.toString());
      if (!current()) return;
      renderLineage(data, { person, direction, depth });
    } catch (e) {
      if (!current()) return;
      const body = e.body || {};
      if (body.status === "unavailable" || body.status === "not_found")
        renderLineage(body, { person, direction, depth });
      else {
        $("#lineage-generations").replaceChildren();
        $("#lineage-meta").textContent =
          "No lineage is shown for this request.";
        lineageNotice(`Academic lineage is unavailable: ${e.message}`, "error");
      }
    } finally {
      if (current()) setLoading(button, false);
    }
  }
  function setupLineageSearch() {
    const input = $("#lineage-query");
    input.addEventListener("input", () => {
      state.searches.lineage = {
        query: input.value,
        token: (state.searches.lineage?.token || 0) + 1,
      };
      clearTimeout(state.timers.lineage);
      state.timers.lineage = setTimeout(() => searchPeople("lineage"), 220);
    });
    input.addEventListener("keydown", (e) => {
      const buttons = $$(
        '.search-result[role="option"]',
        $("#lineage-results"),
      );
      if (e.key === "Escape") $("#lineage-results").replaceChildren();
      if (e.key === "ArrowDown" && buttons[0]) {
        e.preventDefault();
        buttons[0].focus();
      }
    });
  }

  /* ---- Whole-forest lineage map -----------------------------------------
     One canvas holds every documented adviser-to-student relation in the
     release. Typed arrays and a uniform grid keep 20k+ boxes affordable:
     nothing is drawn unless it is inside the viewport, and nothing is
     redrawn unless the reader moved something. */
  // Box size is derived from the layout the API sends, so the chart reads the
  // same whether generations are 95 units apart or 0.95. Level of detail is
  // then decided in drawn pixels, not in layout units.
  const MAP_BOX_PX = 5; // below this a person is a mark, not a box
  const MAP_LABEL_PX = 34; // names start here
  const MAP_LABEL_LIMIT = 1400; // never queue more text draws than this
  const MAP_CHUNK_MS = 12;
  const mapState = {
    status: "idle",
    request: 0,
    count: 0,
    edgeCount: 0,
    ids: null,
    xs: null,
    ys: null,
    gens: null,
    comps: null,
    names: null,
    lower: null,
    edgeA: null,
    edgeB: null,
    childOff: null,
    childNode: null,
    childEdge: null,
    parentOff: null,
    parentNode: null,
    parentEdge: null,
    genTop: null,
    genBottom: null,
    cell: 256,
    gridW: 0,
    gridH: 0,
    gridOff: null,
    gridIdx: null,
    minX: 0,
    minY: 0,
    maxX: 0,
    maxY: 0,
    nodeW: 1,
    nodeH: 1,
    rowSpacing: 1,
    bandsUsable: true,
    view: { scale: 1, tx: 0, ty: 0 },
    minScale: 0.01,
    maxScale: 8,
    fitScale: 1,
    mark: null,
    edgeMark: null,
    selection: -1,
    ancestors: 0,
    descendants: 0,
    visNodes: null,
    visCount: 0,
    visEdges: null,
    visEdgeCount: 0,
    labelsShown: false,
    counts: null,
    version: "",
    ctx: null,
    dpr: 1,
    w: 0,
    h: 0,
    frame: 0,
    pointers: new Map(),
    gesture: null,
    suggestions: [],
    byId: null,
    pathActive: false,
    pathSpread: false,
    relate: { a: null, b: null },
    // Distances from a person the reader picked, over every recorded relation.
    anchor: null,
    edgeYear: null,
    yearMin: 0,
    yearMax: 0,
    time: { on: false, year: 0, undated: false, playing: 0 },
    timeNode: null,
  };

  /* Working titles for the family-map features. Every visible name for them
     is read from here, so renaming a feature is a single edit. */
  const FEATURE_NAMES = {
    relationship: "Relationship finder",
    distance: "Distance from a chosen person",
    summary: "Lineage summary",
    connectors: "Everyone on the shortest chains",
    timeline: "Relations by thesis year",
  };
  state.map = mapState;
  const mapClamp = (v, lo, hi) => (v < lo ? lo : v > hi ? hi : v);
  const mapCount = (value) => Number(value || 0).toLocaleString();
  const mapNodeName = (i) =>
    mapState.names && mapState.names[i]
      ? mapState.names[i]
      : `INSPIRE ${mapState.ids ? mapState.ids[i] : "unknown"}`;
  const mapNotice = (message, kind = "") => {
    const box = $("#map-message");
    if (!box) return;
    box.className = `notice ${kind}`;
    box.textContent = message;
  };
  const mapAnnounce = (message) => {
    const box = $("#map-status");
    if (box) box.textContent = message;
  };
  const setMapLoading = (message) => {
    const box = $("#map-loading");
    if (!box) return;
    box.classList.toggle("hidden", !message);
    if (message) box.textContent = message;
  };

  function mapUnavailable(message, retryable) {
    mapState.status = "error";
    setMapLoading("");
    mapNotice(
      message || "The family map is not available in this release.",
      "warning",
    );
    $("#map-alt").textContent =
      "The family map could not be loaded, so nothing is drawn.";
    if (retryable) {
      const retry = document.createElement("button");
      retry.type = "button";
      retry.id = "map-retry";
      retry.className = "secondary-button";
      retry.textContent = "Try again";
      retry.addEventListener("click", () => loadLineageMap());
      $("#map-message").append(document.createTextNode(" "), retry);
    }
  }

  const mapYield = () => new Promise((resolve) => setTimeout(resolve, 0));
  /* Indexing 21k nodes is chunked so a slow device never freezes on load. */
  async function mapChunks(total, label, request, worker) {
    let i = 0;
    while (i < total) {
      const deadline = performance.now() + MAP_CHUNK_MS;
      while (i < total && performance.now() < deadline) {
        const end = Math.min(total, i + 2048);
        worker(i, end);
        i = end;
      }
      if (i < total) {
        setMapLoading(`${label} ${Math.round((i / total) * 100)}%`);
        await mapYield();
        if (request !== mapState.request) return false;
      }
    }
    return true;
  }

  async function buildMapIndex(data, request) {
    const m = mapState;
    const nodes = Array.isArray(data.nodes) ? data.nodes : [];
    const rawEdges = Array.isArray(data.edges) ? data.edges : [];
    const rawNames = Array.isArray(data.names) ? data.names : [];
    const n = nodes.length;
    if (!n) {
      mapUnavailable(
        "The family map contains no people in this release.",
        false,
      );
      return;
    }
    m.count = n;
    m.ids = new Float64Array(n);
    m.xs = new Float32Array(n);
    m.ys = new Float32Array(n);
    m.gens = new Uint16Array(n);
    m.comps = new Int32Array(n);
    m.names = new Array(n);
    m.lower = new Array(n);
    let minX = Infinity,
      minY = Infinity,
      maxX = -Infinity,
      maxY = -Infinity,
      maxGen = 0;
    let ok = await mapChunks(n, "Reading people", request, (from, to) => {
      for (let i = from; i < to; i += 1) {
        const row = nodes[i] || [];
        const id = Number(row[0]);
        const x = Number(row[1]) || 0;
        const y = Number(row[2]) || 0;
        const gen = Number(row[3]);
        m.ids[i] = Number.isFinite(id) ? id : 0;
        m.xs[i] = x;
        m.ys[i] = y;
        m.gens[i] = Number.isFinite(gen) && gen > 0 ? Math.min(gen, 65535) : 0;
        m.comps[i] = Number(row[4]) || 0;
        if (x < minX) minX = x;
        if (x > maxX) maxX = x;
        if (y < minY) minY = y;
        if (y > maxY) maxY = y;
        if (m.gens[i] > maxGen) maxGen = m.gens[i];
        const name = rawNames[i];
        m.names[i] = typeof name === "string" ? name : "";
        m.lower[i] = m.names[i] ? foldName(m.names[i]) : "";
      }
    });
    if (!ok) return;
    m.minX = minX;
    m.maxX = maxX;
    m.minY = minY;
    m.maxY = maxY;
    m.genTop = new Float32Array(maxGen + 1).fill(Infinity);
    m.genBottom = new Float32Array(maxGen + 1).fill(-Infinity);
    const genCount = new Int32Array(maxGen + 1);
    for (let i = 0; i < n; i += 1) {
      const g = m.gens[i];
      genCount[g] += 1;
      if (m.ys[i] < m.genTop[g]) m.genTop[g] = m.ys[i];
      if (m.ys[i] > m.genBottom[g]) m.genBottom[g] = m.ys[i];
    }
    measureMapLayout(genCount, maxGen);

    const edgeTotal = rawEdges.length;
    const edgeA = new Int32Array(edgeTotal);
    const edgeB = new Int32Array(edgeTotal);
    // Thesis year per relation, 0 where none is recorded. Only thesis records
    // carry a date, so roughly half the relations have one.
    const rawYears = Array.isArray(data.years) ? data.years : [];
    const edgeYear = new Int16Array(edgeTotal);
    let yearMin = 0;
    let yearMax = 0;
    let kept = 0;
    ok = await mapChunks(edgeTotal, "Reading relations", request, (from, to) => {
      for (let e = from; e < to; e += 1) {
        const row = rawEdges[e] || [];
        const a = Number(row[0]);
        const b = Number(row[1]);
        if (!Number.isInteger(a) || !Number.isInteger(b)) continue;
        if (a < 0 || b < 0 || a >= n || b >= n || a === b) continue;
        edgeA[kept] = a;
        edgeB[kept] = b;
        const year = Number(rawYears[e]);
        if (Number.isInteger(year) && year >= 1600 && year <= 2100) {
          edgeYear[kept] = year;
          if (!yearMin || year < yearMin) yearMin = year;
          if (year > yearMax) yearMax = year;
        }
        kept += 1;
      }
    });
    if (!ok) return;
    m.edgeA = edgeA.subarray(0, kept);
    m.edgeB = edgeB.subarray(0, kept);
    m.edgeYear = edgeYear.subarray(0, kept);
    m.yearMin = yearMin;
    m.yearMax = yearMax;
    m.edgeCount = kept;

    // Compressed adjacency: children (adviser to student) and parents.
    const childOff = new Int32Array(n + 1);
    const parentOff = new Int32Array(n + 1);
    for (let e = 0; e < kept; e += 1) {
      childOff[m.edgeA[e] + 1] += 1;
      parentOff[m.edgeB[e] + 1] += 1;
    }
    for (let i = 0; i < n; i += 1) {
      childOff[i + 1] += childOff[i];
      parentOff[i + 1] += parentOff[i];
    }
    const childNode = new Int32Array(kept);
    const childEdge = new Int32Array(kept);
    const parentNode = new Int32Array(kept);
    const parentEdge = new Int32Array(kept);
    const childFill = childOff.slice(0, n);
    const parentFill = parentOff.slice(0, n);
    for (let e = 0; e < kept; e += 1) {
      const a = m.edgeA[e];
      const b = m.edgeB[e];
      const ci = childFill[a]++;
      childNode[ci] = b;
      childEdge[ci] = e;
      const pi = parentFill[b]++;
      parentNode[pi] = a;
      parentEdge[pi] = e;
    }
    m.childOff = childOff;
    m.childNode = childNode;
    m.childEdge = childEdge;
    m.parentOff = parentOff;
    m.parentNode = parentNode;
    m.parentEdge = parentEdge;

    // Uniform grid so the viewport query and hit test never scan all nodes.
    const spanX = Math.max(1, maxX - minX);
    const spanY = Math.max(1, maxY - minY);
    const cell = Math.max(
      128,
      Math.ceil(Math.sqrt((spanX * spanY) / Math.max(1, n / 3))),
    );
    const gridW = Math.max(1, Math.ceil(spanX / cell) + 1);
    const gridH = Math.max(1, Math.ceil(spanY / cell) + 1);
    const cells = gridW * gridH;
    const gridOff = new Int32Array(cells + 1);
    const cellOf = new Int32Array(n);
    for (let i = 0; i < n; i += 1) {
      const cx = mapClamp(Math.floor((m.xs[i] - minX) / cell), 0, gridW - 1);
      const cy = mapClamp(Math.floor((m.ys[i] - minY) / cell), 0, gridH - 1);
      const c = cy * gridW + cx;
      cellOf[i] = c;
      gridOff[c + 1] += 1;
    }
    for (let c = 0; c < cells; c += 1) gridOff[c + 1] += gridOff[c];
    const gridIdx = new Int32Array(n);
    const gridFill = gridOff.slice(0, cells);
    for (let i = 0; i < n; i += 1) gridIdx[gridFill[cellOf[i]]++] = i;
    m.cell = cell;
    m.gridW = gridW;
    m.gridH = gridH;
    m.gridOff = gridOff;
    m.gridIdx = gridIdx;

    m.mark = new Uint8Array(n);
    m.edgeMark = new Uint8Array(kept);
    m.visNodes = new Int32Array(n);
    m.visEdges = new Int32Array(kept);
    m.selection = -1;
    m.ancestors = 0;
    m.descendants = 0;
    m.counts = data.counts && typeof data.counts === "object" ? data.counts : null;
    m.version = typeof data.version === "string" ? data.version : "";
    m.status = "ready";
    setMapLoading("");
    mapNotice("", "hidden");
    $("#map-query").disabled = false;
    // The relationship finder searches the same loaded index, so it opens for
    // business at the same moment the map does.
    ["#relate-a", "#relate-b"].forEach((id) => {
      const field = $(id);
      if (field) field.disabled = false;
    });
    setupMapTimeline();
    renderMapMeta();
    resizeMapCanvas();
    openMapView();
    scheduleMapDraw();
    updateMapAlt();
  }

  /* The API lays the forest out in its own coordinate space, so the box size
     is measured from the data: the typical gap between neighbouring siblings
     across, and the gap between generation rows down. */
  function measureMapLayout(genCount, maxGen) {
    const m = mapState;
    const rows = [];
    for (let g = 0; g <= maxGen; g += 1)
      if (genCount[g] && Number.isFinite(m.genTop[g])) rows.push(m.genTop[g]);
    rows.sort((a, b) => a - b);
    const rowGaps = [];
    for (let k = 1; k < rows.length; k += 1)
      if (rows[k] - rows[k - 1] > 0) rowGaps.push(rows[k] - rows[k - 1]);
    rowGaps.sort((a, b) => a - b);
    const spanY = Math.max(1e-6, m.maxY - m.minY);
    const rowSpacing = rowGaps.length
      ? rowGaps[Math.floor(rowGaps.length / 2)]
      : spanY || 1;
    // Sample the busiest generation for the usual distance between siblings.
    let busiest = 0;
    for (let g = 0; g <= maxGen; g += 1)
      if (genCount[g] > genCount[busiest]) busiest = g;
    const sample = [];
    for (let i = 0; i < m.count && sample.length < 6000; i += 1)
      if (m.gens[i] === busiest) sample.push(m.xs[i]);
    sample.sort((a, b) => a - b);
    const colGaps = [];
    for (let k = 1; k < sample.length; k += 1)
      if (sample[k] - sample[k - 1] > 0) colGaps.push(sample[k] - sample[k - 1]);
    colGaps.sort((a, b) => a - b);
    // The narrowest gap, not the typical one: neighbours one column apart are
    // common, and a box sized to the median overlapped them wherever the map
    // was zoomed in far enough to read.
    const colSpacing = colGaps.length ? colGaps[0] : rowSpacing;
    m.rowSpacing = rowSpacing;
    // Boxes never grow wider than the gap to the next sibling, so they cannot
    // collide however dense or sparse the layout is.
    m.nodeW = Math.max(1e-6, Math.min(colSpacing * 0.86, rowSpacing * 3));
    m.nodeH = Math.max(1e-6, Math.min(rowSpacing * 0.34, m.nodeW * 0.9));
    // Generation bands are only honest when each generation owns its own
    // horizontal strip; a layout that wraps trees into stacked rows does not.
    m.bandsUsable = true;
    let previous = -Infinity;
    for (let g = 0; g <= maxGen; g += 1) {
      if (!genCount[g] || !Number.isFinite(m.genTop[g])) continue;
      if (m.genTop[g] <= previous) {
        m.bandsUsable = false;
        break;
      }
      previous = m.genBottom[g];
    }
  }

  function renderMapMeta() {
    const m = mapState;
    const people = m.counts?.people ?? m.count;
    const relations = m.counts?.relations ?? m.edgeCount;
    const components = m.counts?.components;
    const parts = [
      `${mapCount(people)} people`,
      `${mapCount(relations)} adviser-to-student records`,
    ];
    if (components != null)
      parts.push(`${mapCount(components)} separate family trees`);
    parts.push(m.version ? `data version ${m.version}` : "data version not supplied");
    $("#map-meta").textContent = `${lastUpdatedText()} · ${parts.join(" · ")}`;
  }

  async function loadLineageMap() {
    const m = mapState;
    const request = ++m.request;
    m.status = "loading";
    mapNotice("", "hidden");
    setMapLoading("Loading the family map…");
    try {
      const data = await api("/api/lineage-map");
      if (request !== m.request) return;
      if (data.status && data.status !== "ok") {
        mapUnavailable(data.message, false);
        return;
      }
      await buildMapIndex(data, request);
    } catch (e) {
      if (request !== m.request) return;
      const body = e.body || {};
      if (body.status === "unavailable") mapUnavailable(body.message, false);
      else mapUnavailable(`The family map could not be loaded: ${e.message}`, true);
    }
  }

  function ensureLineageMap() {
    if (mapState.status === "idle") {
      loadLineageMap();
      return;
    }
    if (mapState.status === "ready") {
      if (resizeMapCanvas()) scheduleMapDraw();
    }
  }

  function resizeMapCanvas() {
    const stage = $("#map-stage");
    const canvas = $("#map-canvas");
    if (!stage || !canvas) return false;
    const w = stage.clientWidth;
    const h = stage.clientHeight;
    if (!w || !h) return false;
    const dpr = mapClamp(window.devicePixelRatio || 1, 1, 3);
    if (!mapState.ctx) mapState.ctx = canvas.getContext("2d");
    if (mapState.w === w && mapState.h === h && mapState.dpr === dpr)
      return true;
    mapState.w = w;
    mapState.h = h;
    mapState.dpr = dpr;
    canvas.width = Math.round(w * dpr);
    canvas.height = Math.round(h * dpr);
    return true;
  }

  function fitMapView() {
    const m = mapState;
    if (m.status !== "ready" || !m.w || !m.h) return;
    const spanX = Math.max(1e-6, m.maxX - m.minX + m.nodeW * 2);
    const spanY = Math.max(1e-6, m.maxY - m.minY + m.nodeH * 4);
    const whole = Math.min((m.w - 24) / spanX, (m.h - 24) / spanY);
    m.fitScale = whole;
    // Zooming out past the whole forest would only shrink it into a speck.
    m.minScale = whole * 0.9;
    m.maxScale = Math.max(whole * 8, (MAP_LABEL_PX * 4) / Math.max(1e-6, m.nodeW));
    const scale = mapClamp(whole, m.minScale, m.maxScale);
    m.view.scale = scale;
    m.view.tx = m.w / 2 - ((m.minX + m.maxX) / 2) * scale;
    m.view.ty = m.h / 2 - ((m.minY + m.maxY) / 2) * scale;
    scheduleMapDraw();
  }

  // The forest is one very wide tree beside thousands of small ones, so the
  // whole extent fits the screen only as a hairline. Opening on the height
  // instead shows every generation at once, anchored at the left edge where the
  // largest tree begins, so the first thing a reader sees is a tree.
  /* The first view is a readable piece of a tree, with names drawn: the
     person with the most recorded students, framed from a little above them
     so their students fill the space below. "Fit to screen" still shows the
     whole forest at once. */
  function openMapView() {
    const m = mapState;
    fitMapView();
    if (m.status !== "ready" || !m.w || !m.h) return;
    let start = -1;
    let most = 0;
    for (let i = 0; i < m.count; i += 1) {
      const students = m.childOff[i + 1] - m.childOff[i];
      if (students > most) {
        most = students;
        start = i;
      }
    }
    if (start < 0) return;
    // Wide enough that most names fit whole, not merely wide enough to draw.
    const readable = mapClamp(128 / Math.max(1e-6, m.nodeW), m.minScale, m.maxScale);
    m.view.scale = readable;
    m.view.tx = m.w / 2 - m.xs[start] * readable;
    m.view.ty = Math.min(m.h * 0.28, 90) - m.ys[start] * readable;
    scheduleMapDraw();
  }

  function mapZoomAt(px, py, factor) {
    const m = mapState;
    const next = mapClamp(m.view.scale * factor, m.minScale, m.maxScale);
    const ratio = next / m.view.scale;
    if (ratio === 1) return;
    m.view.tx = px - (px - m.view.tx) * ratio;
    m.view.ty = py - (py - m.view.ty) * ratio;
    m.view.scale = next;
    scheduleMapDraw();
  }
  const mapZoomCentre = (factor) =>
    mapZoomAt(mapState.w / 2, mapState.h / 2, factor);

  function mapCentreOn(i, scale) {
    const m = mapState;
    if (scale) m.view.scale = mapClamp(scale, m.minScale, m.maxScale);
    m.view.tx = m.w / 2 - m.xs[i] * m.view.scale;
    m.view.ty = m.h / 2 - m.ys[i] * m.view.scale;
    scheduleMapDraw();
  }

  /* Visible-node collection walks only the grid cells the viewport covers. */
  function collectVisible() {
    const m = mapState;
    const { scale, tx, ty } = m.view;
    const padX = m.nodeW / 2 + 4 / scale;
    const padY = m.nodeH / 2 + 4 / scale;
    const x0 = (0 - tx) / scale - padX;
    const x1 = (m.w - tx) / scale + padX;
    const y0 = (0 - ty) / scale - padY;
    const y1 = (m.h - ty) / scale + padY;
    const cell = m.cell;
    const cx0 = mapClamp(Math.floor((x0 - m.minX) / cell), 0, m.gridW - 1);
    const cx1 = mapClamp(Math.floor((x1 - m.minX) / cell), 0, m.gridW - 1);
    const cy0 = mapClamp(Math.floor((y0 - m.minY) / cell), 0, m.gridH - 1);
    const cy1 = mapClamp(Math.floor((y1 - m.minY) / cell), 0, m.gridH - 1);
    let count = 0;
    for (let cy = cy0; cy <= cy1; cy += 1) {
      const row = cy * m.gridW;
      const start = m.gridOff[row + cx0];
      const end = m.gridOff[row + cx1 + 1];
      for (let k = start; k < end; k += 1) {
        const i = m.gridIdx[k];
        const x = m.xs[i];
        const y = m.ys[i];
        if (x < x0 || x > x1 || y < y0 || y > y1) continue;
        m.visNodes[count++] = i;
      }
    }
    m.visCount = count;
    m.visRect = { x0, x1, y0, y1 };
    return count;
  }

  const mapInRect = (i, r) => {
    const x = mapState.xs[i];
    const y = mapState.ys[i];
    return x >= r.x0 && x <= r.x1 && y >= r.y0 && y <= r.y1;
  };

  function collectVisibleEdges() {
    const m = mapState;
    const r = m.visRect;
    let count = 0;
    for (let k = 0; k < m.visCount; k += 1) {
      const i = m.visNodes[k];
      for (let c = m.childOff[i]; c < m.childOff[i + 1]; c += 1)
        m.visEdges[count++] = m.childEdge[c];
      for (let p = m.parentOff[i]; p < m.parentOff[i + 1]; p += 1) {
        // Only claim an incoming edge when its adviser is off-screen, so an
        // edge with both ends visible is collected exactly once.
        if (!mapInRect(m.parentNode[p], r)) m.visEdges[count++] = m.parentEdge[p];
      }
    }
    m.visEdgeCount = count;
    return count;
  }

  function strokeMapEdges(ctx, filter, style, width, alpha) {
    const m = mapState;
    const { scale, tx, ty } = m.view;
    const orth = m.nodeW * scale >= MAP_BOX_PX;
    const half = (m.nodeH / 2) * scale;
    let drawn = 0;
    ctx.beginPath();
    for (let k = 0; k < m.visEdgeCount; k += 1) {
      const e = m.visEdges[k];
      if (m.time.on && !mapEdgeInTime(e)) continue;
      if (!filter(e)) continue;
      const a = m.edgeA[e];
      const b = m.edgeB[e];
      const ax = m.xs[a] * scale + tx;
      const ay = m.ys[a] * scale + ty;
      const bx = m.xs[b] * scale + tx;
      const by = m.ys[b] * scale + ty;
      if (!orth) {
        ctx.moveTo(ax, ay);
        ctx.lineTo(bx, by);
      } else {
        const top = ay + half;
        const bottom = by - half;
        const mid = (top + bottom) / 2;
        ctx.moveTo(ax, top);
        ctx.lineTo(ax, mid);
        ctx.lineTo(bx, mid);
        ctx.lineTo(bx, bottom);
      }
      drawn += 1;
    }
    if (!drawn) return;
    ctx.globalAlpha = alpha;
    ctx.strokeStyle = style;
    ctx.lineWidth = width;
    ctx.stroke();
    ctx.globalAlpha = 1;
  }

  function drawLineageMap() {
    const m = mapState;
    const ctx = m.ctx;
    if (!ctx || !m.w || !m.h) return;
    ctx.setTransform(m.dpr, 0, 0, m.dpr, 0, 0);
    ctx.fillStyle = "#fbfcfd";
    ctx.fillRect(0, 0, m.w, m.h);
    if (m.status !== "ready") return;
    const { scale, tx, ty } = m.view;
    const boxPx = m.nodeW * scale;
    const selected = m.selection;
    const dimming = selected >= 0 || m.pathActive;

    // Generation bands give the chart its rows.
    if (m.bandsUsable && m.rowSpacing * scale >= 5 && m.genTop) {
      for (let g = 0; g < m.genTop.length; g += 1) {
        if (!Number.isFinite(m.genTop[g])) continue;
        const top = (m.genTop[g] - m.rowSpacing * 0.42) * scale + ty;
        const bottom = (m.genBottom[g] + m.rowSpacing * 0.42) * scale + ty;
        if (bottom < 0 || top > m.h) continue;
        ctx.fillStyle = g % 2 ? "#f2f6f8" : "#f8fbfb";
        ctx.fillRect(0, top, m.w, Math.max(1, bottom - top));
      }
    }

    collectVisible();
    collectVisibleEdges();

    strokeMapEdges(
      ctx,
      (e) => !m.edgeMark[e],
      "#9db3bd",
      boxPx >= MAP_BOX_PX ? 1.1 : 0.6,
      dimming ? 0.16 : boxPx >= MAP_BOX_PX ? 0.75 : 0.45,
    );
    if (dimming) {
      strokeMapEdges(ctx, (e) => m.edgeMark[e] === 1, "#b86c06", 2, 0.95);
      strokeMapEdges(ctx, (e) => m.edgeMark[e] === 2, "#168b85", 2, 0.95);
      /* The route between two people is the loudest thing on the map. */
      strokeMapEdges(ctx, (e) => m.edgeMark[e] === 3, "#c2185b", 3.2, 1);
    }

    const boxes = boxPx >= MAP_BOX_PX;
    const w = boxPx;
    const h = m.nodeH * scale;
    const markSize = mapClamp(boxPx, 1.5, 4);
    const paint = (filter, fill, stroke, alpha) => {
      ctx.globalAlpha = alpha;
      ctx.fillStyle = fill;
      for (let k = 0; k < m.visCount; k += 1) {
        const i = m.visNodes[k];
        if (m.time.on && !m.timeNode[i]) continue;
        if (!filter(i)) continue;
        const x = m.xs[i] * scale + tx;
        const y = m.ys[i] * scale + ty;
        if (boxes) ctx.fillRect(x - w / 2, y - h / 2, w, h);
        else ctx.fillRect(x - markSize / 2, y - markSize / 2, markSize, markSize);
      }
      if (boxes && stroke) {
        ctx.strokeStyle = stroke;
        ctx.lineWidth = scale > 1 ? 1.2 : 1;
        ctx.beginPath();
        for (let k = 0; k < m.visCount; k += 1) {
          const i = m.visNodes[k];
          if (m.time.on && !m.timeNode[i]) continue;
          if (!filter(i)) continue;
          const x = m.xs[i] * scale + tx;
          const y = m.ys[i] * scale + ty;
          ctx.rect(x - w / 2, y - h / 2, w, h);
        }
        ctx.stroke();
      }
      ctx.globalAlpha = 1;
    };

    paint(
      (i) => !m.mark[i],
      boxes ? "#ffffff" : "#5d7885",
      "#a8bcc5",
      dimming ? 0.25 : 1,
    );
    if (dimming) {
      paint((i) => m.mark[i] & 1 && !(m.mark[i] & 4), "#fff0d6", "#b86c06", 1);
      paint((i) => m.mark[i] & 2 && !(m.mark[i] & 4), "#dcf3f0", "#168b85", 1);
      paint((i) => m.mark[i] & 4, "#10283f", "#10283f", 1);
      paint((i) => m.mark[i] & 8 && !(m.mark[i] & 16), "#ffe3ee", "#c2185b", 1);
      paint((i) => m.mark[i] & 16, "#c2185b", "#7d1038", 1);
    }

    m.labelsShown = boxPx >= MAP_LABEL_PX && m.visCount <= MAP_LABEL_LIMIT;
    if (m.labelsShown) {
      const fontSize = mapClamp(Math.round(h * 0.42), 9, 18);
      ctx.font = `${fontSize}px Inter, system-ui, sans-serif`;
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      const budget = Math.max(3, Math.floor((w - 6) / (fontSize * 0.53)));
      for (let k = 0; k < m.visCount; k += 1) {
        const i = m.visNodes[k];
        if (m.time.on && !m.timeNode[i]) continue;
        const flags = m.mark[i];
        ctx.globalAlpha = dimming && !flags ? 0.35 : 1;
        ctx.fillStyle = flags & 4 || flags & 16 ? "#ffffff" : "#1d3442";
        const label = mapNodeName(i);
        const text =
          label.length > budget ? `${label.slice(0, budget - 1)}…` : label;
        ctx.fillText(text, m.xs[i] * scale + tx, m.ys[i] * scale + ty);
      }
      ctx.globalAlpha = 1;
    }

    if (selected >= 0) {
      const x = m.xs[selected] * scale + tx;
      const y = m.ys[selected] * scale + ty;
      ctx.strokeStyle = "#168b85";
      ctx.lineWidth = 3;
      const rw = Math.max(w, 14);
      const rh = Math.max(h, 12);
      ctx.strokeRect(x - rw / 2 - 3, y - rh / 2 - 3, rw + 6, rh + 6);
    }
    clearTimeout(state.timers.mapAlt);
    state.timers.mapAlt = setTimeout(updateMapAlt, 400);
  }

  function scheduleMapDraw() {
    if (mapState.frame) return;
    mapState.frame = requestAnimationFrame(() => {
      mapState.frame = 0;
      drawLineageMap();
      renderMapZoomReadout();
    });
  }

  function mapHitTest(px, py) {
    const m = mapState;
    if (m.status !== "ready") return -1;
    const { scale, tx, ty } = m.view;
    const x = (px - tx) / scale;
    const y = (py - ty) / scale;
    const tolerance = Math.max(m.nodeW / 2, 9 / scale);
    const toleranceY = Math.max(m.nodeH / 2, 9 / scale);
    const cell = m.cell;
    const cx0 = mapClamp(Math.floor((x - tolerance - m.minX) / cell), 0, m.gridW - 1);
    const cx1 = mapClamp(Math.floor((x + tolerance - m.minX) / cell), 0, m.gridW - 1);
    const cy0 = mapClamp(Math.floor((y - toleranceY - m.minY) / cell), 0, m.gridH - 1);
    const cy1 = mapClamp(Math.floor((y + toleranceY - m.minY) / cell), 0, m.gridH - 1);
    let best = -1;
    let bestDist = Infinity;
    for (let cy = cy0; cy <= cy1; cy += 1) {
      const row = cy * m.gridW;
      for (let k = m.gridOff[row + cx0]; k < m.gridOff[row + cx1 + 1]; k += 1) {
        const i = m.gridIdx[k];
        if (m.time.on && !m.timeNode[i]) continue;
        const dx = Math.abs(m.xs[i] - x);
        const dy = Math.abs(m.ys[i] - y);
        if (dx > tolerance || dy > toleranceY) continue;
        const dist = dx / tolerance + dy / toleranceY;
        if (dist < bestDist) {
          bestDist = dist;
          best = i;
        }
      }
    }
    return best;
  }

  /* Selection lights one person's own lineage: every adviser above them and
     every student below them, following the loaded relations only. */
  function selectMapNode(i, options = {}) {
    const m = mapState;
    if (m.status !== "ready") return;
    m.mark.fill(0);
    m.edgeMark.fill(0);
    m.ancestors = 0;
    m.descendants = 0;
    m.selection = i >= 0 ? i : -1;
    if (m.selection < 0) {
      renderMapDetail();
      scheduleMapDraw();
      updateMapAlt();
      return;
    }
    const stack = [i];
    m.mark[i] |= 1;
    while (stack.length) {
      const node = stack.pop();
      for (let p = m.parentOff[node]; p < m.parentOff[node + 1]; p += 1) {
        m.edgeMark[m.parentEdge[p]] = 1;
        const parent = m.parentNode[p];
        if (m.mark[parent] & 1) continue;
        m.mark[parent] |= 1;
        m.ancestors += 1;
        stack.push(parent);
      }
    }
    stack.push(i);
    m.mark[i] |= 2;
    while (stack.length) {
      const node = stack.pop();
      for (let c = m.childOff[node]; c < m.childOff[node + 1]; c += 1) {
        m.edgeMark[m.childEdge[c]] = m.edgeMark[m.childEdge[c]] || 2;
        const child = m.childNode[c];
        if (m.mark[child] & 2) continue;
        m.mark[child] |= 2;
        m.descendants += 1;
        stack.push(child);
      }
    }
    m.mark[i] |= 4;
    renderMapDetail();
    scheduleMapDraw();
    updateMapAlt();
    if (options.announce !== false)
      mapAnnounce(
        `${mapNodeName(i)} selected. ${mapCount(m.ancestors)} advisers above, ${mapCount(m.descendants)} students below.`,
      );
  }

  function mapAdviserCount(i) {
    return mapState.parentOff[i + 1] - mapState.parentOff[i];
  }
  function mapStudentCount(i) {
    return mapState.childOff[i + 1] - mapState.childOff[i];
  }

  function renderMapDetail() {
    const m = mapState;
    const panel = $("#map-detail");
    const body = $("#map-detail-body");
    body.replaceChildren();
    if (m.selection < 0) {
      panel.classList.add("hidden");
      $("#map-detail-name").textContent = "No one selected";
      return;
    }
    const i = m.selection;
    const id = String(m.ids[i]);
    panel.classList.remove("hidden");
    $("#map-detail-name").textContent = m.names[i] || `INSPIRE ${id}`;
    const facts = document.createElement("dl");
    const add = (label, value) => {
      const dt = document.createElement("dt");
      dt.textContent = label;
      const dd = document.createElement("dd");
      dd.textContent = value;
      facts.append(dt, dd);
    };
    add("INSPIRE", id);
    add(
      "Generation",
      m.gens[i] === 0 ? "0 (no recorded adviser)" : String(m.gens[i]),
    );
    body.append(facts);
    const href = inspireAuthorUrl(id);
    if (href && safeHref(href)) body.append(link("Profile ↗", href));
    const open = document.createElement("button");
    open.type = "button";
    open.id = "map-open-lineage";
    open.className = "primary-button";
    open.textContent = "Open in Lineage view";
    open.addEventListener("click", () =>
      setLineageRoot({ id, name: m.names[i] || "" }),
    );
    body.append(open);
    if (!m.names[i]) {
      const note = document.createElement("p");
      note.className = "lineage-note";
      note.textContent =
        "No name accompanied this person in the map data; the INSPIRE identifier is shown instead.";
      body.append(note);
    }
    body.append(mapSummarySection(i), mapDistanceSection(i));
  }

  function mapDetailSection(key) {
    const section = document.createElement("section");
    section.className = "map-detail-section";
    const heading = document.createElement("h3");
    heading.dataset.featureName = key;
    heading.textContent = FEATURE_NAMES[key];
    section.append(heading);
    return section;
  }

  function mapSummarySection(i) {
    const m = mapState;
    const section = mapDetailSection("summary");
    const facts = document.createElement("dl");
    const add = (label, value) => {
      const dt = document.createElement("dt");
      dt.textContent = label;
      const dd = document.createElement("dd");
      dd.textContent = value;
      facts.append(dt, dd);
    };
    const up = mapLineageReach(i, true);
    const down = mapLineageReach(i, false);
    const years = mapThesisYears(i);
    const across = (reach) =>
      reach.people
        ? `${mapCount(reach.people)} across ${reach.generations} generation${reach.generations === 1 ? "" : "s"}`
        : "none recorded";
    add("Advisers", mapCount(mapAdviserCount(i)));
    add("Students", mapCount(mapStudentCount(i)));
    add("Academic ancestors", across(up));
    add("Academic descendants", across(down));
    add("Own thesis year", years.own ? String(years.own) : "not recorded");
    if (years.first)
      add("Students' thesis years",
        years.first === years.last ? String(years.first) : `${years.first}–${years.last}`);
    if (m.comps[i]) add("Connected group", `${mapCount(m.comps[i])} people`);
    section.append(facts);
    return section;
  }

  function mapDistanceSection(i) {
    const m = mapState;
    const section = mapDetailSection("distance");
    const text = document.createElement("p");
    text.className = "relate-note";
    const actions = document.createElement("div");
    actions.className = "relate-actions";
    const button = (label, primary, action) => {
      const b = document.createElement("button");
      b.type = "button";
      b.className = primary ? "primary-button" : "secondary-button";
      b.textContent = label;
      b.addEventListener("click", action);
      actions.append(b);
    };
    const setAnchor = (index) => {
      m.anchor = index < 0 ? null : { index, dist: mapDistancesFrom(index) };
      renderMapDetail();
    };
    const anchor = m.anchor;
    if (!anchor) {
      text.textContent =
        "Set this person as the reference point, then select anyone else on the map " +
        "to see how many supervision links separate them.";
      button("Set as reference point", true, () => setAnchor(i));
    } else if (anchor.index === i) {
      let reached = 0;
      let furthest = 0;
      for (let k = 0; k < m.count; k += 1) {
        const d = anchor.dist[k];
        if (d > 0) { reached += 1; if (d > furthest) furthest = d; }
      }
      text.textContent =
        `This is the reference point. ${mapCount(reached)} people are connected to them ` +
        `through recorded supervision; the furthest is ${furthest} links away.`;
      button("Clear reference point", false, () => setAnchor(-1));
    } else {
      const d = anchor.dist[i];
      const other = mapNodeName(anchor.index);
      text.textContent = d < 0
        ? `No chain of recorded supervision connects them to ${other}.`
        : `${d} supervision link${d === 1 ? "" : "s"} from ${other}, following relations in either direction.`;
      if (d > 0)
        button("Show how they are related", true, () => {
          mapState.relate = {
            a: { index: anchor.index, id: String(m.ids[anchor.index]), name: other },
            b: { index: i, id: String(m.ids[i]), name: mapNodeName(i) },
          };
          $("#relate-a").value = other;
          $("#relate-b").value = mapNodeName(i);
          $("#relate-run").disabled = false;
          $("#relate-form").scrollIntoView({ behavior: "smooth", block: "start" });
          runRelationship({ preventDefault() {} });
        });
      button("Make this the reference point", false, () => setAnchor(i));
      button("Clear", false, () => setAnchor(-1));
    }
    section.append(text, actions);
    return section;
  }

  function updateMapAlt() {
    const m = mapState;
    const alt = $("#map-alt");
    if (!alt) return;
    if (m.status !== "ready") return;
    // Count what is in view now: before the first frame the visible set is
    // still empty, which read as "covers 0" over a screen full of boxes.
    if (m.w && m.h) collectVisible();
    const people = m.counts?.people ?? m.count;
    const relations = m.counts?.relations ?? m.edgeCount;
    const components = m.counts?.components;
    const sentences = [
      `A chart of ${mapCount(people)} researchers joined by ${mapCount(relations)} documented adviser-to-student records${
        components != null
          ? `, in ${mapCount(components)} separate family trees`
          : ""
      }. Advisers sit above their students, one row per generation.`,
      `${mapCount(m.visCount)} of them are in view; names are ${m.labelsShown ? "drawn on the boxes" : "hidden until you zoom in further"}.`,
    ];
    if (m.selection >= 0) {
      const i = m.selection;
      sentences.push(
        `${mapNodeName(i)} is selected: generation ${m.gens[i]}, ${mapCount(mapAdviserCount(i))} recorded advisers, ${mapCount(mapStudentCount(i))} recorded students, with ${mapCount(m.ancestors)} people above and ${mapCount(m.descendants)} below highlighted.`,
      );
    } else {
      sentences.push("No one is selected. Use the search field to find a person.");
    }
    alt.textContent = sentences.join(" ");
    renderMapZoomReadout();
  }

  // Whether names are shown is only known once a frame is drawn, so the readout
  // is refreshed after drawing rather than before, or it describes the last one.
  function renderMapZoomReadout() {
    const readout = $("#map-zoom-readout");
    if (readout)
      readout.textContent = `${mapCount(mapState.visCount)} people in view · ${
        mapState.labelsShown ? "names shown" : "zoom in to read names"
      }`;
  }

  function focusMapNode(i) {
    const m = mapState;
    if (i < 0 || i >= m.count) return;
    resizeMapCanvas();
    mapCentreOn(i, Math.max(m.view.scale, 1.1));
    selectMapNode(i, { announce: false });
    mapAnnounce(
      `Centred on ${mapNodeName(i)}. ${mapCount(m.ancestors)} advisers above, ${mapCount(m.descendants)} students below.`,
    );
  }

  /* Half this corpus is spelled with diacritics - Lüst, Söldner-Rembold,
     Helayël-Neto - and people type the plain letters. Search compares folded
     forms so "Dieter Lust" finds "Dieter Lüst"; the map still draws the real
     spelling. */
  function foldName(value) {
    return String(value)
      .normalize("NFD")
      .replace(/\p{Diacritic}/gu, "")
      .replace(/[øØ]/g, "o")
      .replace(/[đĐ]/g, "d")
      .replace(/[łŁ]/g, "l")
      .replace(/[æ]/g, "ae")
      .replace(/[ß]/g, "ss")
      .toLowerCase();
  }

  /* Search runs over precomputed folded names, so it stays instant. */
  function mapIndexOf(id) {
    const m = mapState;
    if (m.status !== "ready") return -1;
    if (!m.byId) {
      m.byId = new Map();
      for (let i = 0; i < m.count; i += 1) m.byId.set(String(m.ids[i]), i);
    }
    const found = m.byId.get(String(id));
    return found === undefined ? -1 : found;
  }

  /* The edge index joining two nodes, whichever way the supervision runs. */
  function mapEdgeBetween(a, b) {
    const m = mapState;
    for (let p = m.parentOff[a]; p < m.parentOff[a + 1]; p += 1)
      if (m.parentNode[p] === b) return m.parentEdge[p];
    for (let c = m.childOff[a]; c < m.childOff[a + 1]; c += 1)
      if (m.childNode[c] === b) return m.childEdge[c];
    return -1;
  }

  /* Light one route and dim the rest, then bring it into view. */
  function highlightMapPath(ids) {
    const m = mapState;
    if (m.status !== "ready") return 0;
    m.mark.fill(0);
    m.edgeMark.fill(0);
    m.selection = -1;
    m.pathActive = false;
    const indices = ids.map(mapIndexOf).filter((i) => i >= 0);
    if (!indices.length) {
      scheduleMapDraw();
      return 0;
    }
    indices.forEach((i) => {
      m.mark[i] |= 8;
    });
    m.mark[indices[0]] |= 16;
    m.mark[indices[indices.length - 1]] |= 16;
    for (let k = 0; k + 1 < indices.length; k += 1) {
      const edge = mapEdgeBetween(indices[k], indices[k + 1]);
      if (edge >= 0) m.edgeMark[edge] = 3;
    }
    m.pathActive = true;
    frameMapIndices(indices);
    return indices.length;
  }

  /* Bring a group of people into view - or, when they are spread so far
     apart that every box would be under a pixel, the first of them. */
  function frameMapIndices(indices) {
    const m = mapState;
    let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity;
    indices.forEach((i) => {
      minX = Math.min(minX, m.xs[i]);
      maxX = Math.max(maxX, m.xs[i]);
      minY = Math.min(minY, m.ys[i]);
      maxY = Math.max(maxY, m.ys[i]);
    });
    const pad = Math.max(m.nodeW * 2, 260);
    const whole = mapClamp(
      Math.min(m.w / (maxX - minX + pad), m.h / (maxY - minY + pad)),
      m.minScale,
      m.maxScale,
    );
    // Two people in distant families are thousands of columns apart, and the
    // scale that fits both draws every box below a pixel. Showing one end
    // legibly beats showing the whole route as a hairline.
    m.pathSpread = m.nodeW * whole < 3;
    if (m.pathSpread) {
      mapCentreOn(indices[0], Math.max(m.fitScale * 6, whole));
    } else {
      m.view.scale = whole;
      m.view.tx = m.w / 2 - ((minX + maxX) / 2) * whole;
      m.view.ty = m.h / 2 - ((minY + maxY) / 2) * whole;
    }
    scheduleMapDraw();
    renderMapZoomReadout();
  }

  function mapSearch(query) {
    const m = mapState;
    const q = foldName(query.trim());
    if (m.status !== "ready" || q.length < 2) return [];
    const digits = /^\d+$/.test(q);
    const words = q.split(/[\s,]+/).filter((word) => word.length > 1);
    const best = [];
    const consider = (i, score) => {
      if (best.length < 8) {
        best.push({ i, score });
      } else {
        let worst = 0;
        for (let k = 1; k < best.length; k += 1)
          if (best[k].score > best[worst].score) worst = k;
        if (best[worst].score <= score) return;
        best[worst] = { i, score };
      }
    };
    for (let i = 0; i < m.count; i += 1) {
      if (digits) {
        const id = String(m.ids[i]);
        if (id === q) consider(i, -1);
        else if (id.startsWith(q)) consider(i, 0);
        continue;
      }
      const name = m.lower[i];
      if (!name) continue;
      const at = name.indexOf(q);
      if (at >= 0) {
        if (at === 0) consider(i, name.length === q.length ? 0 : 1);
        else if (name.charCodeAt(at - 1) === 32 || name.charCodeAt(at - 1) === 46)
          consider(i, 2);
        else consider(i, 3);
        continue;
      }
      // "Sidney Coleman" should find "Sidney Richard Coleman", and surnames
      // are stored first as often as not, so every word has to appear but
      // their order does not matter.
      if (words.length > 1 && words.every((word) => name.includes(word)))
        consider(i, 4);
    }
    best.sort(
      (a, b) => a.score - b.score || mapNodeName(a.i).localeCompare(mapNodeName(b.i)),
    );
    return best.map((entry) => entry.i);
  }

  function renderMapSuggestions(indices, query) {
    const menu = $("#map-results");
    const input = $("#map-query");
    menu.replaceChildren();
    menu.classList.remove("inline-search-notice");
    mapState.suggestions = indices;
    if (!query.trim()) {
      input.setAttribute("aria-expanded", "false");
      return;
    }
    if (!indices.length) {
      const empty = document.createElement("div");
      empty.className = "search-result search-notice";
      empty.textContent =
        mapState.status === "ready"
          ? "No one on the map matches that."
          : "The map is still loading.";
      menu.append(empty);
      menu.classList.add("inline-search-notice");
      input.setAttribute("aria-expanded", "false");
      return;
    }
    indices.forEach((i) => {
      const b = document.createElement("button");
      b.type = "button";
      b.className = "search-result";
      b.setAttribute("role", "option");
      const strong = document.createElement("strong");
      strong.textContent = mapNodeName(i);
      const small = document.createElement("small");
      small.textContent = `INSPIRE ${mapState.ids[i]} · generation ${mapState.gens[i]} · connected group of ${mapCount(mapState.comps[i] || 0)}`;
      b.append(strong, small);
      b.addEventListener("click", () => {
        menu.replaceChildren();
        input.setAttribute("aria-expanded", "false");
        focusMapNode(i);
        $("#map-stage").focus();
      });
      menu.append(b);
    });
    input.setAttribute("aria-expanded", "true");
  }

  /* ------------------------------------------------ shared graph walks --- */

  /* Supervision links between one person and everyone else, following each
     relation in either direction. -1 means no recorded chain reaches them. */
  function mapDistancesFrom(start) {
    const m = mapState;
    const dist = new Int32Array(m.count).fill(-1);
    const queue = new Int32Array(m.count);
    let head = 0;
    let tail = 0;
    dist[start] = 0;
    queue[tail++] = start;
    while (head < tail) {
      const node = queue[head++];
      const next = dist[node] + 1;
      for (let p = m.parentOff[node]; p < m.parentOff[node + 1]; p += 1) {
        const other = m.parentNode[p];
        if (dist[other] < 0) { dist[other] = next; queue[tail++] = other; }
      }
      for (let c = m.childOff[node]; c < m.childOff[node + 1]; c += 1) {
        const other = m.childNode[c];
        if (dist[other] < 0) { dist[other] = next; queue[tail++] = other; }
      }
    }
    return dist;
  }

  /* How many academic ancestors or descendants a person has, and how many
     generations those records reach. */
  function mapLineageReach(start, upward) {
    const m = mapState;
    const off = upward ? m.parentOff : m.childOff;
    const nodes = upward ? m.parentNode : m.childNode;
    const seen = new Set([start]);
    let frontier = [start];
    let generations = 0;
    while (frontier.length) {
      const next = [];
      frontier.forEach((node) => {
        for (let k = off[node]; k < off[node + 1]; k += 1) {
          const other = nodes[k];
          if (!seen.has(other)) { seen.add(other); next.push(other); }
        }
      });
      if (next.length) generations += 1;
      frontier = next;
    }
    return { people: seen.size - 1, generations };
  }

  /* Thesis years on the relations where a person is the student, and where
     they are the adviser. */
  function mapThesisYears(i) {
    const m = mapState;
    let own = 0;
    for (let p = m.parentOff[i]; p < m.parentOff[i + 1]; p += 1) {
      const year = m.edgeYear[m.parentEdge[p]];
      if (year && (!own || year < own)) own = year;
    }
    let first = 0;
    let last = 0;
    for (let c = m.childOff[i]; c < m.childOff[i + 1]; c += 1) {
      const year = m.edgeYear[m.childEdge[c]];
      if (!year) continue;
      if (!first || year < first) first = year;
      if (year > last) last = year;
    }
    return { own, first, last };
  }

  /* ------------------------------------------------------------ timeline --- */

  function mapEdgeInTime(e) {
    const m = mapState;
    const year = m.edgeYear[e];
    return year ? year <= m.time.year : m.time.undated;
  }

  /* A person is on the map at a given year when one of their relations is. */
  function refreshMapTime() {
    const m = mapState;
    if (m.status !== "ready") return;
    if (!m.timeNode) m.timeNode = new Uint8Array(m.count);
    m.timeNode.fill(0);
    let relations = 0;
    let undated = 0;
    for (let e = 0; e < m.edgeCount; e += 1) {
      if (!m.edgeYear[e]) undated += 1;
      if (!mapEdgeInTime(e)) continue;
      relations += 1;
      m.timeNode[m.edgeA[e]] = 1;
      m.timeNode[m.edgeB[e]] = 1;
    }
    let people = 0;
    for (let i = 0; i < m.count; i += 1) people += m.timeNode[i];
    $("#map-time-label").textContent = String(m.time.year);
    const note = $("#map-time-note");
    const dated = m.edgeCount - undated;
    note.textContent = m.time.on
      ? `Up to ${m.time.year}: ${mapCount(relations)} relations and ${mapCount(people)} people. ` +
        `${mapCount(dated)} of ${mapCount(m.edgeCount)} relations carry a thesis year; ` +
        `the other ${mapCount(undated)} are ${m.time.undated ? "shown throughout" : "hidden"}.`
      : `${mapCount(dated)} of ${mapCount(m.edgeCount)} relations carry a thesis year, ` +
        `from ${m.yearMin} to ${m.yearMax}. Only thesis records are dated.`;
    scheduleMapDraw();
  }

  function stopMapPlayback() {
    const m = mapState;
    clearInterval(m.time.playing);
    m.time.playing = 0;
    const play = $("#map-time-play");
    if (play) {
      play.firstElementChild.textContent = "▶";
      play.setAttribute("aria-label", "Play through the years");
    }
  }

  function setupMapTimeline() {
    const m = mapState;
    const box = $("#map-timeline");
    if (!box || !m.yearMin) return;
    const toggle = $("#map-time-on");
    const slider = $("#map-time-year");
    const undated = $("#map-time-undated");
    const play = $("#map-time-play");
    slider.min = String(m.yearMin);
    slider.max = String(m.yearMax);
    slider.value = String(m.yearMax);
    m.time.year = m.yearMax;
    box.hidden = false;
    const enable = (on) => {
      m.time.on = on;
      box.classList.toggle("is-on", on);
      [slider, undated, play].forEach((control) => { control.disabled = !on; });
      if (!on) stopMapPlayback();
      refreshMapTime();
    };
    toggle.addEventListener("change", () => enable(toggle.checked));
    slider.addEventListener("input", () => {
      m.time.year = Number(slider.value);
      refreshMapTime();
    });
    undated.addEventListener("change", () => {
      m.time.undated = undated.checked;
      refreshMapTime();
    });
    play.addEventListener("click", () => {
      if (m.time.playing) { stopMapPlayback(); return; }
      if (m.time.year >= m.yearMax) m.time.year = m.yearMin;
      play.firstElementChild.textContent = "❚❚";
      play.setAttribute("aria-label", "Pause");
      m.time.playing = setInterval(() => {
        m.time.year = Math.min(m.yearMax, m.time.year + 1);
        slider.value = String(m.time.year);
        refreshMapTime();
        if (m.time.year >= m.yearMax) stopMapPlayback();
      }, 110);
    });
    refreshMapTime();
  }

  /* ---------------------------------------------- people on the chains --- */

  /* Everyone whose distance to the first person plus distance to the second
     is at most the shortest chain plus some slack. With no slack that is
     exactly the people on some shortest chain. */
  function mapChainMembers(a, b, slack) {
    const fromA = mapDistancesFrom(a);
    const shortest = fromA[b];
    if (shortest < 0) return { shortest: -1, members: [], fromA, fromB: null };
    const fromB = mapDistancesFrom(b);
    const limit = shortest + slack;
    const members = [];
    for (let i = 0; i < mapState.count; i += 1)
      if (fromA[i] >= 0 && fromB[i] >= 0 && fromA[i] + fromB[i] <= limit) members.push(i);
    return { shortest, limit, members, fromA, fromB };
  }

  function highlightMapChains(found, a, b) {
    const m = mapState;
    m.mark.fill(0);
    m.edgeMark.fill(0);
    m.selection = -1;
    const inside = new Uint8Array(m.count);
    found.members.forEach((i) => { inside[i] = 1; m.mark[i] |= 8; });
    m.mark[a] |= 16;
    m.mark[b] |= 16;
    const { fromA, fromB, limit } = found;
    found.members.forEach((u) => {
      const step = (other, edge) => {
        if (inside[other] && fromA[other] === fromA[u] + 1 &&
            fromA[u] + 1 + fromB[other] <= limit) m.edgeMark[edge] = 3;
      };
      for (let p = m.parentOff[u]; p < m.parentOff[u + 1]; p += 1)
        step(m.parentNode[p], m.parentEdge[p]);
      for (let c = m.childOff[u]; c < m.childOff[u + 1]; c += 1)
        step(m.childNode[c], m.childEdge[c]);
    });
    m.pathActive = true;
    frameMapIndices(found.members);
  }

  function renderChainMembers(target, a, b, slack) {
    target.replaceChildren();
    const found = mapChainMembers(a, b, slack);
    if (found.shortest < 0) {
      target.textContent = "No chain of recorded supervision connects these two on the map.";
      return;
    }
    highlightMapChains(found, a, b);
    const summary = document.createElement("p");
    summary.className = "relate-note";
    const between = found.members.length - 2;
    summary.textContent =
      `The shortest chains are ${found.shortest} link${found.shortest === 1 ? "" : "s"} long, ` +
      `following supervision in either direction. ` +
      (slack
        ? `Allowing up to ${found.limit} links, ${mapCount(between)} people sit between them.`
        : `${mapCount(between)} ${between === 1 ? "person sits" : "people sit"} on at least one of them.`);
    target.append(summary);
    const layers = new Map();
    found.members.forEach((i) => {
      if (i === a || i === b) return;
      const k = found.fromA[i];
      if (!layers.has(k)) layers.set(k, []);
      layers.get(k).push(i);
    });
    const list = document.createElement("ol");
    list.className = "connector-layers";
    [...layers.keys()].sort((x, y) => x - y).forEach((k) => {
      const people = layers.get(k).sort((x, y) => mapNodeName(x).localeCompare(mapNodeName(y)));
      const li = document.createElement("li");
      const step = document.createElement("span");
      step.className = "connector-step";
      step.textContent = `${k} link${k === 1 ? "" : "s"} out`;
      const names = document.createElement("span");
      const shown = people.slice(0, 14);
      shown.forEach((i, index) => {
        const jump = document.createElement("button");
        jump.type = "button";
        jump.className = "relate-jump";
        jump.textContent = mapNodeName(i);
        jump.addEventListener("click", () => {
          mapCentreOn(i, Math.max(mapState.fitScale * 6, mapState.view.scale));
          scheduleMapDraw();
          $("#map-stage").scrollIntoView({ behavior: "smooth", block: "center" });
        });
        names.append(jump);
        if (index < shown.length - 1) names.append(document.createTextNode(", "));
      });
      if (people.length > shown.length)
        names.append(document.createTextNode(` and ${mapCount(people.length - shown.length)} more`));
      li.append(step, names);
      list.append(li);
    });
    target.append(list);
    mapAnnounce(`${mapCount(between)} people highlighted between them on the map.`);
  }

  /* ------------------------------------------------- relationship finder --- */

  /* Each field holds a person only once one has been picked, so a half-typed
     name can never be sent as if it were a choice. */
  function relateField(which) {
    const input = $(`#relate-${which}`);
    const menu = $(`#relate-${which}-results`);
    let offered = [];
    const choose = (index) => {
      mapState.relate[which] = { index, id: String(mapState.ids[index]),
                                 name: mapNodeName(index) };
      input.value = mapNodeName(index);
      menu.replaceChildren();
      input.setAttribute("aria-expanded", "false");
      $("#relate-run").disabled = !(mapState.relate.a && mapState.relate.b);
    };
    const suggest = () => {
      const query = input.value;
      mapState.relate[which] = null;
      $("#relate-run").disabled = true;
      menu.replaceChildren();
      menu.classList.remove("inline-search-notice");
      const found = mapSearch(query);
      offered = found;
      if (!query.trim()) {
        input.setAttribute("aria-expanded", "false");
        return;
      }
      if (!found.length) {
        const empty = document.createElement("div");
        empty.className = "search-result search-notice";
        empty.textContent =
          mapState.status === "ready"
            ? "No one on the map matches that."
            : "The map is still loading.";
        menu.append(empty);
        menu.classList.add("inline-search-notice");
        return;
      }
      found.forEach((i) => {
        const b = document.createElement("button");
        b.type = "button";
        b.className = "search-result";
        b.setAttribute("role", "option");
        const strong = document.createElement("strong");
        strong.textContent = mapNodeName(i);
        const small = document.createElement("small");
        small.textContent = `INSPIRE ${mapState.ids[i]} · connected group of ${mapCount(mapState.comps[i] || 0)}`;
        b.append(strong, small);
        b.addEventListener("click", () => choose(i));
        menu.append(b);
      });
      input.setAttribute("aria-expanded", "true");
    };
    input.addEventListener("input", () => {
      clearTimeout(state.timers[`relate${which}`]);
      state.timers[`relate${which}`] = setTimeout(suggest, 120);
    });
    input.addEventListener("keydown", (e) => {
      if (e.key === "Escape") {
        menu.replaceChildren();
        input.setAttribute("aria-expanded", "false");
      }
      if (e.key === "Enter") {
        e.preventDefault();
        if (offered.length && !mapState.relate[which]) choose(offered[0]);
      }
    });
  }

  function relateName(data, id) {
    const person = (data.people || {})[String(id)];
    return (person && person.name) || `INSPIRE ${id}`;
  }

  function renderRelationship(data) {
    const box = $("#relate-result");
    box.replaceChildren();
    const a = mapState.relate.a;
    const b = mapState.relate.b;

    const verdict = document.createElement("p");
    verdict.className = "relate-verdict";
    if (data.status === "not_found" || data.status === "unavailable") {
      verdict.textContent = data.message || "That could not be answered.";
      box.append(verdict);
      return;
    }
    const term = document.createElement("span");
    term.className = "relate-term";
    term.textContent = data.label;
    verdict.append(
      document.createTextNode(`${a.name} and ${b.name}: `),
      term,
    );
    const note = document.createElement("p");
    note.className = "relate-note";
    note.textContent = data.explanation || "";
    box.append(verdict, note);

    const chain = data.chain || [];
    if (!chain.length) {
      // Two people with no adviser chain between them may still have written
      // together, and that is the more useful next question.
      const coauthor = coauthorCrosslink(a, b);
      if (coauthor) box.append(coauthor);
      return;
    }
    const list = document.createElement("ol");
    list.className = "relate-chain";
    chain.forEach((step, index) => {
      const li = document.createElement("li");
      if (data.meeting_point &&
          (step.adviser === data.meeting_point || step.student === data.meeting_point))
        li.className = "relate-meet";
      const number = document.createElement("span");
      number.className = "relate-step";
      number.textContent = `${index + 1}.`;
      const jump = document.createElement("button");
      jump.type = "button";
      jump.className = "relate-jump";
      jump.textContent =
        `${relateName(data, step.adviser)} advised ${relateName(data, step.student)}`;
      jump.title = "Show this person on the map";
      jump.addEventListener("click", () => {
        const index = mapIndexOf(step.student);
        if (index >= 0) {
          mapCentreOn(index, Math.max(mapState.fitScale * 6, mapState.view.scale));
          scheduleMapDraw();
          $("#map-stage").scrollIntoView({ behavior: "smooth", block: "center" });
        }
      });
      li.append(
        number,
        jump,
        document.createTextNode(" · "),
        link(sourceLabel(step), step.source_url),
      );
      if (step.degree)
        li.append(document.createTextNode(` · ${degreeLabel(step.degree)}`));
      list.append(li);
    });
    const diagram = relationshipDiagram(data);
    if (diagram) box.append(diagram);
    box.append(list);

    // Only a shared ancestor is a meeting point; on a direct line of descent
    // one of the two people is the ancestor, and saying so again adds nothing.
    const [up, down] = data.distances || [0, 0];
    if (data.meeting_point && up > 0 && down > 0) {
      const meet = document.createElement("p");
      meet.className = "relate-note";
      meet.textContent = `Their lines meet at ${relateName(data, data.meeting_point)}.`;
      box.append(meet);
    }

    box.append(connectorSection());
    const coauthor = coauthorCrosslink(a, b);
    if (coauthor) box.append(coauthor);

    if (mapState.pathSpread) {
      const spread = document.createElement("p");
      spread.className = "relate-note";
      spread.textContent =
        "These two sit in different parts of the forest, so the map is showing the " +
        "first of them; use the chain above to step along the route.";
      box.append(spread);
    }


  }

  function relationshipDiagram(data) {
    const chain = data.chain || [];
    if (!chain.length) return null;
    const people = [];
    chain.forEach((step, index) => {
      const from = step.direction === "down" ? step.adviser : step.student;
      const to = step.direction === "down" ? step.student : step.adviser;
      if (!index) people.push({ id: from, level: 0 });
      const level = people[people.length - 1].level + (step.direction === "up" ? -1 : 1);
      people.push({ id: to, level });
    });
    const levels = people.map((person) => person.level);
    const top = Math.min(...levels);
    const rows = Math.max(...levels) - top;
    const stepX = 168;
    const rowY = 62;
    const width = Math.max(320, (people.length - 1) * stepX + 220);
    const height = rows * rowY + 76;
    const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svg.setAttribute("viewBox", `0 0 ${width} ${height}`);
    svg.setAttribute("class", "relate-diagram");
    // Draw at natural size: a three-person chain stretched to full width
    // turns its labels into headlines.
    svg.style.maxWidth = `${width}px`;
    svg.setAttribute("role", "img");
    svg.setAttribute("aria-label",
      `${data.label}: a chain of ${chain.length} supervision records.`);
    const at = (index) => ({
      x: 110 + index * stepX,
      y: 38 + (people[index].level - top) * rowY,
    });
    people.forEach((person, index) => {
      if (index) {
        const from = at(index - 1);
        const to = at(index);
        const line = document.createElementNS("http://www.w3.org/2000/svg", "path");
        line.setAttribute("d",
          `M ${from.x} ${from.y} C ${(from.x + to.x) / 2} ${from.y}, ` +
          `${(from.x + to.x) / 2} ${to.y}, ${to.x} ${to.y}`);
        line.setAttribute("class", "relate-diagram-link");
        svg.append(line);
      }
      const spot = at(index);
      const dot = document.createElementNS("http://www.w3.org/2000/svg", "circle");
      dot.setAttribute("cx", spot.x);
      dot.setAttribute("cy", spot.y);
      dot.setAttribute("r", index === 0 || index === people.length - 1 ? 7 : 5);
      dot.setAttribute("class",
        person.id === data.meeting_point ? "relate-diagram-meet" : "relate-diagram-dot");
      const text = document.createElementNS("http://www.w3.org/2000/svg", "text");
      text.setAttribute("x", spot.x);
      text.setAttribute("y", spot.y - 14);
      text.setAttribute("text-anchor", "middle");
      text.setAttribute("class", "relate-diagram-label");
      const name = relateName(data, person.id);
      text.textContent = name.length > 20 ? `${name.slice(0, 19)}…` : name;
      svg.append(dot, text);
    });
    return svg;
  }

  function coauthorCrosslink(a, b) {
    if (!a || !b || a.id === b.id) return null;
    const other = document.createElement("div");
    other.className = "relation-crosslink is-quiet";
    other.append(document.createTextNode("Coauthorship is a separate question. "));
    const go = document.createElement("button");
    go.type = "button";
    go.className = "secondary-button";
    go.textContent = "Find a coauthor route between them";
    go.addEventListener("click", () => openCoauthorRoute(a, b));
    other.append(go);
    return other;
  }

  function connectorSection() {
    const section = document.createElement("section");
    section.className = "map-detail-section";
    const heading = document.createElement("h3");
    heading.dataset.featureName = "connectors";
    heading.textContent = FEATURE_NAMES.connectors;
    const note = document.createElement("p");
    note.className = "relate-note";
    note.textContent =
      "The chain above is one route. Show every person on any of the shortest routes " +
      "between them, or on routes up to one link longer.";
    const controls = document.createElement("div");
    controls.className = "connector-controls";
    const slack = document.createElement("select");
    slack.setAttribute("aria-label", "How long a route to include");
    [["0", "Shortest routes only"], ["1", "Up to one link longer"]].forEach(([value, label]) => {
      const option = document.createElement("option");
      option.value = value;
      option.textContent = label;
      slack.append(option);
    });
    const run = document.createElement("button");
    run.type = "button";
    run.className = "secondary-button";
    run.textContent = "Show them";
    const out = document.createElement("div");
    run.addEventListener("click", () => {
      const { a, b } = mapState.relate;
      const ia = a ? mapIndexOf(a.id) : -1;
      const ib = b ? mapIndexOf(b.id) : -1;
      if (ia < 0 || ib < 0) {
        out.textContent = "Both people need to be on the map for this.";
        return;
      }
      renderChainMembers(out, ia, ib, Number(slack.value));
    });
    controls.append(slack, run);
    section.append(heading, note, controls, out);
    return section;
  }

  async function runRelationship(event) {
    event.preventDefault();
    const a = mapState.relate.a;
    const b = mapState.relate.b;
    const box = $("#relate-result");
    if (!a || !b) {
      box.textContent = "Choose two people from the suggestions first.";
      return;
    }
    $("#relate-run").disabled = true;
    box.textContent = "Tracing the supervision records…";
    try {
      const data = await api(`/api/relationship?a=${encodeURIComponent(a.id)}&b=${encodeURIComponent(b.id)}`);
      renderRelationship(data);
      const route = data.line ||
        (data.line_up || []).concat((data.line_down || []).slice().reverse().slice(1));
      if (route && route.length > 1) {
        const shown = highlightMapPath(route);
        mapAnnounce(`${data.label}. ${shown} people highlighted on the map.`);
      } else if (data.status === "ok" && data.label === "the same person") {
        highlightMapPath([a.id]);
      } else {
        highlightMapPath([]);
      }
    } catch (error) {
      box.textContent = `The relationship could not be traced: ${error.message}`;
    } finally {
      $("#relate-run").disabled = !(mapState.relate.a && mapState.relate.b);
    }
  }

  function applyFeatureNames(root = document) {
    $$("[data-feature-name]", root).forEach((element) => {
      const name = FEATURE_NAMES[element.dataset.featureName];
      if (name) element.textContent = name;
    });
  }

  function setupRelationshipFinder() {
    applyFeatureNames();
    const form = $("#relate-form");
    if (!form) return;
    relateField("a");
    relateField("b");
    form.addEventListener("submit", runRelationship);
    $("#relate-clear").addEventListener("click", () => {
      mapState.relate = { a: null, b: null };
      ["a", "b"].forEach((which) => {
        $(`#relate-${which}`).value = "";
        $(`#relate-${which}-results`).replaceChildren();
      });
      $("#relate-result").replaceChildren();
      $("#relate-run").disabled = true;
      mapState.pathActive = false;
      selectMapNode(-1);
    });
  }

  function setupLineageMapSearch() {
    const input = $("#map-query");
    input.addEventListener("input", () => {
      clearTimeout(state.timers.mapSearch);
      const value = input.value;
      state.timers.mapSearch = setTimeout(
        () => renderMapSuggestions(mapSearch(value), value),
        120,
      );
    });
    input.addEventListener("keydown", (e) => {
      const options = $$('.search-result[role="option"]', $("#map-results"));
      if (e.key === "Escape") {
        $("#map-results").replaceChildren();
        input.setAttribute("aria-expanded", "false");
      }
      if (e.key === "ArrowDown" && options[0]) {
        e.preventDefault();
        options[0].focus();
      }
      if (e.key === "Enter") {
        e.preventDefault();
        const first = mapState.suggestions[0];
        if (first != null) {
          $("#map-results").replaceChildren();
          input.setAttribute("aria-expanded", "false");
          focusMapNode(first);
        }
      }
    });
  }

  function setupLineageMapInteractions() {
    const stage = $("#map-stage");
    if (!stage) return;
    const local = (e) => {
      const rect = stage.getBoundingClientRect();
      return { x: e.clientX - rect.left, y: e.clientY - rect.top };
    };
    stage.addEventListener("pointerdown", (e) => {
      if (mapState.status !== "ready") return;
      stage.setPointerCapture(e.pointerId);
      mapState.pointers.set(e.pointerId, local(e));
      if (mapState.pointers.size === 1) {
        const p = mapState.pointers.get(e.pointerId);
        mapState.gesture = { moved: 0, startX: p.x, startY: p.y };
      }
    });
    stage.addEventListener("pointermove", (e) => {
      const pointers = mapState.pointers;
      if (!pointers.has(e.pointerId)) return;
      const previous = pointers.get(e.pointerId);
      const point = local(e);
      pointers.set(e.pointerId, point);
      if (pointers.size === 1) {
        mapState.view.tx += point.x - previous.x;
        mapState.view.ty += point.y - previous.y;
        if (mapState.gesture)
          mapState.gesture.moved +=
            Math.abs(point.x - previous.x) + Math.abs(point.y - previous.y);
        scheduleMapDraw();
        return;
      }
      if (pointers.size === 2) {
        const [a, b] = [...pointers.values()];
        const distance = Math.hypot(a.x - b.x, a.y - b.y);
        const midX = (a.x + b.x) / 2;
        const midY = (a.y + b.y) / 2;
        const last = mapState.gesture?.pinch;
        if (last && last.distance > 0 && distance > 0) {
          mapState.view.tx += midX - last.midX;
          mapState.view.ty += midY - last.midY;
          mapZoomAt(midX, midY, distance / last.distance);
        }
        mapState.gesture = {
          moved: 999,
          pinch: { distance, midX, midY },
        };
        scheduleMapDraw();
      }
    });
    const endPointer = (e) => {
      const pointers = mapState.pointers;
      if (!pointers.has(e.pointerId)) return;
      pointers.delete(e.pointerId);
      if (stage.hasPointerCapture?.(e.pointerId))
        stage.releasePointerCapture(e.pointerId);
      if (pointers.size === 0 && mapState.gesture) {
        const tap = mapState.gesture.moved < 6;
        const start = { x: mapState.gesture.startX, y: mapState.gesture.startY };
        mapState.gesture = null;
        if (tap && e.type === "pointerup") {
          const hit = mapHitTest(start.x, start.y);
          selectMapNode(hit);
          stage.focus();
        }
      } else if (pointers.size === 1) {
        mapState.gesture = { moved: 999 };
      }
    };
    stage.addEventListener("pointerup", endPointer);
    stage.addEventListener("pointercancel", endPointer);
    stage.addEventListener(
      "wheel",
      (e) => {
        if (mapState.status !== "ready") return;
        e.preventDefault();
        const unit = e.deltaMode === 1 ? 16 : e.deltaMode === 2 ? 400 : 1;
        const point = local(e);
        mapZoomAt(
          point.x,
          point.y,
          Math.exp(mapClamp(-e.deltaY * unit * 0.0018, -0.6, 0.6)),
        );
      },
      { passive: false },
    );
    stage.addEventListener("keydown", (e) => {
      if (mapState.status !== "ready") return;
      const step = 60;
      const keys = {
        ArrowLeft: () => (mapState.view.tx += step),
        ArrowRight: () => (mapState.view.tx -= step),
        ArrowUp: () => (mapState.view.ty += step),
        ArrowDown: () => (mapState.view.ty -= step),
      };
      if (keys[e.key]) {
        e.preventDefault();
        keys[e.key]();
        scheduleMapDraw();
        return;
      }
      if (e.key === "+" || e.key === "=") {
        e.preventDefault();
        mapZoomCentre(1.3);
      } else if (e.key === "-" || e.key === "_") {
        e.preventDefault();
        mapZoomCentre(1 / 1.3);
      } else if (e.key === "0") {
        e.preventDefault();
        fitMapView();
      } else if (e.key === "Escape") {
        selectMapNode(-1);
      }
    });
    $("#map-zoom-in").addEventListener("click", () => mapZoomCentre(1.4));
    $("#map-zoom-out").addEventListener("click", () => mapZoomCentre(1 / 1.4));
    $("#map-fit").addEventListener("click", () => {
      resizeMapCanvas();
      fitMapView();
      updateMapAlt();
    });
    $("#map-clear-selection").addEventListener("click", () => {
      selectMapNode(-1);
      mapAnnounce("Selection cleared.");
    });
    const observe = () => {
      if (resizeMapCanvas()) {
        if (mapState.status === "ready") scheduleMapDraw();
      }
    };
    if (window.ResizeObserver) new ResizeObserver(observe).observe(stage);
    else window.addEventListener("resize", observe);
  }

  function init() {
    setupPageChrome();
    restoreUrl();
    setupSearch("source");
    setupSearch("target");
    setupLineageSearch();
    setupLineageMapSearch();
    setupRelationshipFinder();
    setupLineageMapInteractions();
    document.addEventListener("pointerdown", (event) => {
      ["source", "target", "lineage", "map", ...(state.stopKeys || [])].forEach((which) => {
        const field = $(`#${which}-query`).closest(".identity-field");
        if (!field.contains(event.target)) {
          const menu = $(`#${which}-results`);
          if (!menu.classList.contains("inline-search-notice")) {
            menu.replaceChildren();
            $(`#${which}-query`).setAttribute("aria-expanded", "false");
          }
        }
      });
    });
    $("#search-form").addEventListener("submit", (e) => {
      e.preventDefault();
      findPath();
    });
    $("#lineage-form").addEventListener("submit", (e) => {
      e.preventDefault();
      loadLineage();
    });
    ["lineage-direction", "lineage-depth"].forEach((id) =>
      $("#" + id).addEventListener("change", () => {
        if (state.lineage) loadLineage();
      }),
    );
    $$(".clear-picker").forEach((b) =>
      b.addEventListener("click", () => clearPicker(b.dataset.clear)),
    );
    $("#add-stop").addEventListener("click", () => {
      invalidateResults();
      const key = addStop();
      $(`#${key}-query`).focus();
    });
    $("#swap-people").addEventListener("click", () => {
      invalidateResults();
      [state.source, state.target] = [state.target, state.source];
      ["source", "target"].forEach((which) => {
        if (!state[which]) $(`#${which}-query`).value = "";
        renderPicker(which);
      });
      syncUrl();
    });
    $("#paper-team-size").addEventListener("change", () => {
      applyTeamSizePreset($("#paper-team-size").value);
      updateFilterSummary();
    });
    ["min-authors", "max-authors", "min-authors-custom", "max-authors-custom"].forEach((id) =>
      $("#" + id).addEventListener("change", () => {
        syncTeamSizeFromBounds();
        updateFilterSummary();
      }),
    );
    $$(".tab").forEach((b) =>
      b.addEventListener("click", () => showTab(b.dataset.tab)),
    );
    [
      "min-shared",
      "year-start",
      "year-end",
      "genealogy",
      "min-shared-custom",
    ].forEach((id) =>
      $("#" + id).addEventListener("change", () => updateFilterSummary()),
    );
    $("#copy-share").addEventListener("click", copyShare);
    $("#deep-stop").addEventListener("click", stopDeepSearch);
    $("#deep-continue").addEventListener("click", () => {
      if (state.deepJob) continueDeepSearch(state.deepJob);
    });
    $("#route-update-show").addEventListener("click", () => state.routeOffer?.apply());
    $("#export-json").addEventListener("click", jsonExport);
    $("#export-svg").addEventListener("click", svgExport);
    $("#close-profile").addEventListener("click", () => {
      state.profileRequest++;
      $("#person-panel").classList.add("hidden");
    });
    setupGraphInteractions();
    const graphStage = $("#graph-stage");
    let graphSize = "";
    const fitGraphOnResize = () => {
      const size = `${graphStage.clientWidth}x${graphStage.clientHeight}`;
      if (size === graphSize) return;
      graphSize = size;
      if (state.graph.nodes.size) {
        fitGraph();
        renderGraph();
      }
    };
    if (window.ResizeObserver) {
      new ResizeObserver(fitGraphOnResize).observe(graphStage);
    } else {
      window.addEventListener("resize", fitGraphOnResize);
    }
    fitGraphOnResize();
    registerModelContext();
    loadDataset();
  }
  document.addEventListener("DOMContentLoaded", init);
})();
